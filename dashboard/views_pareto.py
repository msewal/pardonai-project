# pardonai/dashboard/views_pareto.py
from __future__ import annotations
from typing import List, Dict, Any, Optional
from math import fsum

from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Avg, Q
from django.views.decorators.http import require_GET
from django.utils.dateparse import parse_date

from .models import ProductMetric

# İsteğe bağlı bilimsel paketler
try:
    import pandas as pd  # type: ignore
except Exception:  # pandas yoksa
    pd = None  # type: ignore

try:
    import numpy as np  # type: ignore
except Exception:
    np = None  # type: ignore


# --------------------- yardımcılar ---------------------
def _safe_float(x, default=0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default

def _get_params(request):
    date_from = parse_date(request.GET.get("date_from") or "")
    date_to   = parse_date(request.GET.get("date_to") or "")
    search    = (request.GET.get("search") or "").strip()
    groupby   = (request.GET.get("groupby") or "name").lower()  # name|id
    threshold = int(request.GET.get("threshold") or 80)
    threshold = max(50, min(threshold, 95))
    return date_from, date_to, search, groupby, threshold

def _filtered_qs(request):
    date_from, date_to, search, groupby, _ = _get_params(request)
    qs = ProductMetric.objects.all()
    if date_from:
        qs = qs.filter(ts__gte=date_from)
    if date_to:
        qs = qs.filter(ts__lte=date_to)
    if search:
        qs = qs.filter(product_name__icontains=search)

    # gruplama
    key = "product_name" if groupby == "name" else "product_id"
    agg = qs.values(key).annotate(
        sum_profit=Sum("total_profit"),
        sum_click=Sum("click"),
        sum_sales=Sum("sales"),
        avg_cost=Avg("cost"),
        avg_price=Avg("sales_price"),
        avg_unit_profit=Avg("unit_profit"),
        avg_ppc=Avg("profit_per_click"),
    ).order_by("-sum_profit")

    labels = [r[key] for r in agg]
    profit = [float(r["sum_profit"] or 0) for r in agg]
    click  = [int(r["sum_click"] or 0) for r in agg]
    sales  = [int(r["sum_sales"] or 0) for r in agg]

    rows = []
    for r in agg:
        rows.append({
            "label": r[key],
            "sum_profit": float(r["sum_profit"] or 0),
            "sum_click": int(r["sum_click"] or 0),
            "sum_sales": int(r["sum_sales"] or 0),
            "avg_cost": float(r["avg_cost"] or 0),
            "avg_price": float(r["avg_price"] or 0),
            "avg_unit_profit": float(r["avg_unit_profit"] or 0),
            "avg_ppc": float(r["avg_ppc"] or 0),
        })

    return labels, profit, click, sales, rows

def _cum_pct(values: List[float]) -> List[float]:
    total = fsum(values) or 1.0
    run = 0.0
    out = []
    for v in values:
        run += v
        out.append(run/total * 100.0)
    return out

def _threshold_index(cum_pct: List[float], threshold=80) -> int:
    for i, v in enumerate(cum_pct):
        if v >= threshold:
            return i
    return len(cum_pct) - 1 if cum_pct else -1

def _df_from_rows(rows: List[Dict[str, Any]]):
    if pd is None:
        return None
    return pd.DataFrame(rows)

def _numpy_hist(vals: List[float], bins=10):
    if np is not None:
        hist, edges = np.histogram(vals, bins=bins)
        return hist.tolist(), edges.tolist()
    # sade Python fallback
    if not vals:
        return [], []
    mn, mx = min(vals), max(vals)
    if mx == mn:
        return [len(vals)], [mn, mx]
    step = (mx - mn) / bins
    edges = [mn + i * step for i in range(bins + 1)]
    hist = [0] * bins
    for v in vals:
        k = min(int((v - mn) / step), bins - 1)
        hist[k] += 1
    return hist, edges

# --------------------- temel pareto ---------------------
@require_GET
def pareto_api(request):
    try:
        labels, profit, click, sales, rows = _filtered_qs(request)
        cum = _cum_pct(profit)
        _, _, _, _, _, = _get_params(request)
        threshold = int(request.GET.get("threshold") or 80)
        idx = _threshold_index(cum, threshold)

        resp = {
            "success": True,
            "labels": labels,
            "profit": profit,
            "cum_pct": [round(x, 2) for x in cum],
            "sum_profit": round(fsum(profit), 2),
            "idx_threshold": idx,
            "table": {
                "columns": ["label", "sum_profit", "sum_click", "sum_sales", "avg_cost", "avg_price", "avg_unit_profit", "avg_ppc"],
                "rows": rows,
            },
        }
        return JsonResponse(resp)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)

@require_GET
def pareto_topn(request):
    try:
        n = int(request.GET.get("n") or 10)
        labels, profit, *_ = _filtered_qs(request)
        labels = labels[:n]
        profit = profit[:n]
        total = fsum(profit) or 1.0
        share = [round(p/total*100.0, 2) for p in profit]
        return JsonResponse({"success": True, "labels": labels, "profit": profit, "share_pct": share})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)

# --------------------- ABC sınıflandırma ---------------------
@require_GET
def pareto_abc(request):
    """
    A: ilk %T (default 80)
    B: sonraki %15 (80-95)
    C: kalan
    """
    try:
        labels, profit, *_ = _filtered_qs(request)
        cum = _cum_pct(profit)
        thr = int(request.GET.get("threshold") or 80)
        thr_b = int(request.GET.get("threshold_b") or 95)

        total = fsum(profit) or 1.0
        out = []
        for i, (lab, p, c) in enumerate(zip(labels, profit, cum)):
            if c <= thr:
                cls = "A"
            elif c <= thr_b:
                cls = "B"
            else:
                cls = "C"
            out.append({"label": lab, "profit": p, "cum_pct": round(c,2), "class": cls})

        # özet
        a_profit = fsum([r["profit"] for r in out if r["class"] == "A"])
        b_profit = fsum([r["profit"] for r in out if r["class"] == "B"])
        c_profit = fsum([r["profit"] for r in out if r["class"] == "C"])
        summary = {
            "A": {"count": len([1 for r in out if r["class"] == "A"]), "sum": round(a_profit,2), "share_pct": round(a_profit/total*100,2)},
            "B": {"count": len([1 for r in out if r["class"] == "B"]), "sum": round(b_profit,2), "share_pct": round(b_profit/total*100,2)},
            "C": {"count": len([1 for r in out if r["class"] == "C"]), "sum": round(c_profit,2), "share_pct": round(c_profit/total*100,2)},
            "total": round(total,2),
        }

        return JsonResponse({"success": True, "items": out, "summary": summary, "thresholds": {"A": thr, "B": thr_b}})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)

# --------------------- Lorenz + Gini ---------------------
@require_GET
def pareto_lorenz(request):
    """
    Lorenz eğrisi (ürün sayısı birikimli payı vs kâr birikimli payı) ve Gini katsayısı.
    """
    try:
        labels, profit, *_ = _filtered_qs(request)
        n = len(profit)
        if n == 0:
            return JsonResponse({"success": True, "x": [], "y": [], "gini": 0.0})

        # kâr küçükten büyüğe
        idx = sorted(range(n), key=lambda i: profit[i])
        sorted_profit = [profit[i] for i in idx]
        total = fsum(sorted_profit) or 1.0

        cum_profit = [0.0]
        run = 0.0
        for p in sorted_profit:
            run += p
            cum_profit.append(run / total)
        # x ekseni: birikimli ürün oranı
        x = [i / n for i in range(0, n+1)]
        y = cum_profit  # 0..1

        # Gini (trapez yaklaşımı)
        area = 0.0
        for i in range(n):
            area += (y[i] + y[i+1]) / 2 * (x[i+1] - x[i])
        gini = 1 - 2 * area
        return JsonResponse({"success": True, "x": x, "y": y, "gini": round(gini, 4)})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)

# --------------------- Scatter paketleri ---------------------
@require_GET
def pareto_scatter(request):
    """
    Çeşitli saçılım grafikleri: 
      - click vs profit
      - sales vs profit
      - profit_per_click vs click (ortalama)
      - unit_profit vs sales (ortalama)
    """
    try:
        labels, profit, clicks, sales, rows = _filtered_qs(request)
        # ortalamalar tabloda
        avg_ppc = [r["avg_ppc"] for r in rows]
        avg_unit = [r["avg_unit_profit"] for r in rows]

        sets = {
            "click_profit": [{"x": int(c), "y": float(p), "label": lab} for lab, c, p in zip(labels, clicks, profit)],
            "sales_profit": [{"x": int(s), "y": float(p), "label": lab} for lab, s, p in zip(labels, sales, profit)],
            "ppc_click":    [{"x": float(ap), "y": int(c), "label": lab} for lab, ap, c in zip(labels, avg_ppc, clicks)],
            "unit_sales":   [{"x": float(au), "y": int(s), "label": lab} for lab, au, s in zip(labels, avg_unit, sales)],
        }
        return JsonResponse({"success": True, "sets": sets})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)

# --------------------- Histogram ---------------------
@require_GET
def pareto_hist(request):
    """
    Histogram: profit_per_click (ortalama) ve unit_profit (ortalama)
    """
    try:
        *_a, rows = _filtered_qs(request)
        v_ppc = [float(r["avg_ppc"]) for r in rows if r["avg_ppc"] is not None]
        v_unit = [float(r["avg_unit_profit"]) for r in rows if r["avg_unit_profit"] is not None]

        bins = int(request.GET.get("bins") or 10)
        h1, e1 = _numpy_hist(v_ppc, bins=bins)
        h2, e2 = _numpy_hist(v_unit, bins=bins)

        return JsonResponse({"success": True, "ppc": {"hist": h1, "edges": e1}, "unit": {"hist": h2, "edges": e2}})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)

# --------------------- Treemap (ABC hiyerarşi) ---------------------
@require_GET
def pareto_treemap(request):
    """
    Treemap için hiyerarşik çıktı. Üst düzeyde ABC sınıfı, altında ürünler.
    """
    try:
        labels, profit, *_ = _filtered_qs(request)
        cum = _cum_pct(profit)
        thr = int(request.GET.get("threshold") or 80)
        thr_b = int(request.GET.get("threshold_b") or 95)

        nodes = {"A": [], "B": [], "C": []}
        for lab, p, c in zip(labels, profit, cum):
            if c <= thr: cls = "A"
            elif c <= thr_b: cls = "B"
            else: cls = "C"
            nodes[cls].append({"name": str(lab), "value": round(float(p), 2)})

        data = [{"name": k, "children": v} for k, v in nodes.items()]
        return JsonResponse({"success": True, "root": {"name": "ABC", "children": data}})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)

# --------------------- What-If ---------------------
@require_GET
def pareto_whatif(request):
    """
    price_delta_pct (%): satış fiyatına uygulanır -> yeni unit_profit = (price*(1+p) - cost_ortalama)
    sales_uplift_pct (%): satış adedine uygulanır
    'selected' = "A,B,C" veya id’ler (groupby paramına göre)
    """
    try:
        date_from, date_to, search, groupby, _ = _get_params(request)
        price_delta = _safe_float(request.GET.get("price_delta_pct"), 0.0) / 100.0
        sales_uplift = _safe_float(request.GET.get("sales_uplift_pct"), 0.0) / 100.0
        selected = (request.GET.get("selected") or "").split(",")
        selected = [s.strip() for s in selected if s.strip()]

        labels, profit, clicks, sales, rows = _filtered_qs(request)
        key_is_name = (groupby == "name")
        # seçili etiketleri bul
        selected_set = set(selected)
        sim_profit_map: Dict[str, float] = {}

        for lab, p, c, s, r in zip(labels, profit, clicks, sales, rows):
            # sadece seçili ürünlerde değiştir
            if selected_set and (str(lab) not in selected_set):
                sim_profit_map[str(lab)] = float(p)
                continue
            avg_price = float(r["avg_price"] or 0)
            avg_cost  = float(r["avg_cost"] or 0)
            new_unit  = (avg_price * (1.0 + price_delta)) - avg_cost
            new_sales = s * (1.0 + sales_uplift)
            new_total = new_unit * new_sales
            sim_profit_map[str(lab)] = float(new_total)

        # komple dizi
        sim_profit = [sim_profit_map[str(lab)] for lab in labels]
        cum = _cum_pct(sim_profit)
        return JsonResponse({"success": True, "labels": labels, "profit": sim_profit, "cum_pct": [round(x,2) for x in cum]})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)

# --------------------- CSV dışa aktarım ---------------------
@require_GET
def pareto_export(request):
    try:
        _, _, _, groupby, _ = _get_params(request)
        labels, profit, clicks, sales, rows = _filtered_qs(request)
        cum = _cum_pct(profit)

        # csv
        import csv
        resp = HttpResponse(content_type="text/csv; charset=utf-8")
        filename = f"pareto_export_{groupby}.csv"
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        writer = csv.writer(resp)
        writer.writerow(["Label", "Total Profit", "Cumulative %", "Clicks", "Sales", "Avg Cost", "Avg Price", "Avg Unit Profit", "Avg Profit/Click"])
        for r, c in zip(rows, cum):
            writer.writerow([
                r["label"], round(r["sum_profit"],2), round(c,2),
                r["sum_click"], r["sum_sales"], round(r["avg_cost"],2), round(r["avg_price"],2),
                round(r["avg_unit_profit"],2), round(r["avg_ppc"],2)
            ])
        return resp
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)
