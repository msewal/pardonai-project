# views.py
from __future__ import annotations
from typing import List, Tuple
import csv
import io

from django.db.models import Sum, F, FloatField, Q
from django.db.models.functions import Coalesce
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.shortcuts import render
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_GET

from .models import ProductMetric
from accounts.models import Businesses
from pardonai.menu.models import Menu  # Menü modeliniz
from pardonai.orders.models import Order  # Sipariş modeliniz
from pardonai.performance.models import PerformanceMetric, Goal  # Performans ve hedef modelleriniz

# -------------------- Pages --------------------

def dashboard_page(request: HttpRequest):
    """Ana dashboard sayfası - istatistikler ve modül erişimi"""
    try:
        # İşletme sayıları: Üyelikten aktif olanlar varsa, distinct() kullanarak sayıyoruz.
        total_businesses = Businesses.objects.count()
        active_businesses = Businesses.objects.filter(memberships__is_active=True).distinct().count()
        
        # Menü verileri: is_active alanı varsayılarak
        total_menus = Menu.objects.count()
        active_menus = Menu.objects.filter(is_active=True).count()
        
        # Sipariş verileri: Order modelinde 'order_status' alanı kullanılıyor
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(order_status='pending').count()
        
        # Performans verileri:
        total_metrics = PerformanceMetric.objects.count()
        total_goals = Goal.objects.count()
    except Exception as e:
        # Hata durumunda varsayılan değerler
        total_businesses = 0
        active_businesses = 0
        total_menus = 0
        active_menus = 0
        total_orders = 0
        pending_orders = 0
        total_metrics = 0
        total_goals = 0
    
    context = {
        "total_businesses": total_businesses,
        "active_businesses": active_businesses,
        "total_menus": total_menus,
        "active_menus": active_menus,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "total_metrics": total_metrics,
        "total_goals": total_goals,
    }
    return render(request, "dashboard/dashboard.html", context)
    
def pareto_page(request: HttpRequest):
    return render(request, "dashboard/pareto.html")

def test_page(request: HttpRequest):
    """Test sayfası - template sistemini test etmek için"""
    try:
        # İşletme sayıları
        total_businesses = Businesses.objects.count()
        active_businesses = Businesses.objects.filter(memberships__is_active=True).distinct().count()
        
        # Menü verileri
        total_menus = Menu.objects.count()
        active_menus = Menu.objects.filter(is_active=True).count()
        
        # Sipariş verileri
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(order_status='pending').count()
    except Exception as e:
        # Hata durumunda varsayılan değerler
        total_businesses = 0
        active_businesses = 0
        total_menus = 0
        active_menus = 0
        total_orders = 0
        pending_orders = 0
    
    context = {
        "total_businesses": total_businesses,
        "active_businesses": active_businesses,
        "total_menus": total_menus,
        "active_menus": active_menus,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
    }
    return render(request, "dashboard/test.html", context)

def trendyol_page(request: HttpRequest):
    """
    Trendyol sayfası: Trendyol butonuna tıkladığınızda bu sayfa açılır;
    e-ticaret ile ilgili firmaların isimleri dinamik olarak veritabanından çekilir.
    """
    # Dinamik veri çekimi: subject veya notes alanında ecommerce ilgili kelimelere göre filtreleme
    companies_qs = Businesses.objects.filter(
        Q(subject__iregex=r'(?i)e-?ticaret|ecommerce|online') | Q(notes__iregex=r'(?i)e-?ticaret|ecommerce|online')
    ).values_list('business_name', flat=True).distinct()
    
    companies = list(companies_qs)
    context = {"companies": companies}
    return render(request, "dashboard/trendyol.html", context)

# -------------------- Helpers --------------------

def _filter_queryset(request: HttpRequest):
    """
    Filtreler: date_from/date_to (varsa tarih kolonu yoksa atlanır), search (product_name LIKE), product_ids
    """
    qs = ProductMetric.objects.all()

    df = request.GET.get("date_from")
    dt = request.GET.get("date_to")
    dfp = parse_date(df) if df else None
    dtp = parse_date(dt) if dt else None
    if dfp:
        qs = qs.filter(ts__gte=dfp)
    if dtp:
        qs = qs.filter(ts__lte=dtp)

    search = (request.GET.get("search") or "").strip()
    if search:
        qs = qs.filter(product_name__icontains=search)

    product_ids = (request.GET.get("product_ids") or "").strip()
    if product_ids:
        id_list = [int(x) for x in product_ids.split(",") if x.strip().isdigit()]
        if id_list:
            qs = qs.filter(product_id__in=id_list)

    return qs

def _group_aggregate(qs, groupby: str = "name") -> Tuple[List[str], List[float]]:
    """
    DB tarafında grupla + SUM(total_profit) + DESC sırala.
    """
    if groupby == "id":
        group_fields = ["product_id"]
        label_key = "product_id"
    else:
        group_fields = ["product_name"]
        label_key = "product_name"

    agg_qs = (
        qs.values(*group_fields)
          .annotate(total_profit_sum=Coalesce(Sum("total_profit"), 0.0, output_field=FloatField()))
          .order_by()
          .order_by(F("total_profit_sum").desc())
    )

    labels: List[str] = []
    profits: List[float] = []
    for row in agg_qs:
        labels.append(str(row[label_key]))
        profits.append(float(row["total_profit_sum"]))

    return labels, profits

def _cumulative_percent(values: List[float]) -> Tuple[List[float], int]:
    total = float(sum(values))
    cum, run = [], 0.0
    for v in values:
        run += v
        cum.append((run / total * 100.0) if total else 0.0)
    idx80 = next((i for i, cp in enumerate(cum) if cp >= 80.0), -1)
    return cum, idx80

def _selected_share(labels: List[str], profits: List[float], selected: List[str]) -> float | None:
    if not selected:
        return None
    total = float(sum(profits))
    sel_sum = sum(p for l, p in zip(labels, profits) if l in selected)
    return round((sel_sum / total * 100.0), 2) if total else 0.0

# -------------------- APIs ----------------------

@require_GET
def pareto_api(request: HttpRequest):
    try:
        qs = _filter_queryset(request)
        groupby = (request.GET.get("groupby") or "name").lower()
        threshold = float(request.GET.get("threshold") or 80.0)

        labels, profits = _group_aggregate(qs, groupby=groupby)
        cum_pct, _ = _cumulative_percent(profits)

        idx_th = next((i for i, cp in enumerate(cum_pct) if cp >= threshold), -1)
        top_th = labels[: idx_th + 1] if idx_th >= 0 else []
        total_sum = round(float(sum(profits)), 2)

        selected_param = (request.GET.get("selected") or "").strip()
        selected = [s.strip() for s in selected_param.split(",") if s.strip()]
        selected_share_pct = _selected_share(labels, profits, selected)

        return JsonResponse({
            "labels": labels,
            "profit": [round(x, 2) for x in profits],
            "cum_pct": [round(x, 2) for x in cum_pct],
            "sum_profit": total_sum,
            "idx_threshold": idx_th,
            "top_threshold": top_th,
            "selected_share_pct": selected_share_pct,
            "success": True,
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_GET
def pareto_topn_api(request: HttpRequest):
    """ /api/pareto/topn?n=10&groupby=name """
    try:
        qs = _filter_queryset(request)
        groupby = (request.GET.get("groupby") or "name").lower()
        n = int(request.GET.get("n") or 10)

        labels, profits = _group_aggregate(qs, groupby=groupby)
        labels_n = labels[:n]
        profits_n = profits[:n]
        total_sum = float(sum(profits))
        shares_n = [(p / total_sum * 100.0) if total_sum else 0.0 for p in profits_n]

        return JsonResponse({
            "labels": labels_n,
            "profit": [round(x, 2) for x in profits_n],
            "share_pct": [round(x, 2) for x in shares_n],
            "success": True,
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_GET
def pareto_export_csv(request: HttpRequest):
    """ /api/pareto/export """
    try:
        qs = _filter_queryset(request)
        groupby = (request.GET.get("groupby") or "name").lower()
        labels, profits = _group_aggregate(qs, groupby=groupby)
        cum_pct, _ = _cumulative_percent(profits)

        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["Label", "Total Profit", "Cumulative %"])
        for l, p, c in zip(labels, profits, cum_pct):
            writer.writerow([l, f"{p:.2f}", f"{c:.2f}"])

        out = HttpResponse(buf.getvalue(), content_type="text/csv; charset=utf-8")
        out["Content-Disposition"] = 'attachment; filename="pareto_export.csv"'
        return out
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_GET
def pareto_whatif_api(request: HttpRequest):
    """
    /api/pareto/whatif
      selected=A,B
      groupby=id|name
      price_delta_pct=+3
      sales_uplift_pct=+10
    """
    try:
        qs = _filter_queryset(request)
        groupby = (request.GET.get("groupby") or "name").lower()
        label_field = "product_id" if groupby == "id" else "product_name"

        selected_param = (request.GET.get("selected") or "").strip()
        selected = set([s.strip() for s in selected_param.split(",") if s.strip()])

        price_delta_pct = float(request.GET.get("price_delta_pct") or 0.0)
        sales_uplift_pct = float(request.GET.get("sales_uplift_pct") or 0.0)

        rows = qs.values(label_field, "cost", "sales_price", "sales")
        agg_map = {}

        for r in rows:
            label = str(r[label_field])
            cost = float(r["cost"] or 0.0)
            sales_price = float(r["sales_price"] or 0.0)
            sales = float(r["sales"] or 0.0)

            if (not selected) or (label in selected):
                new_sales_price = sales_price * (1.0 + price_delta_pct / 100.0)
                new_sales = sales * (1.0 + sales_uplift_pct / 100.0)
            else:
                new_sales_price = sales_price
                new_sales = sales

            new_unit_profit = new_sales_price - cost
            new_total_profit = new_unit_profit * new_sales
            agg_map[label] = agg_map.get(label, 0.0) + new_total_profit

        items = sorted(agg_map.items(), key=lambda x: x[1], reverse=True)
        labels = [k for k, _ in items]
        profits = [float(v) for _, v in items]

        cum_pct, idx_th = _cumulative_percent(profits)
        total_sum = round(float(sum(profits)), 2)

        return JsonResponse({
            "labels": labels,
            "profit": [round(x, 2) for x in profits],
            "cum_pct": [round(x, 2) for x in cum_pct],
            "sum_profit": total_sum,
            "idx_threshold": idx_th,
            "params": {
                "selected": list(selected),
                "price_delta_pct": price_delta_pct,
                "sales_uplift_pct": sales_uplift_pct,
                "groupby": groupby,
            },
            "success": True,
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
