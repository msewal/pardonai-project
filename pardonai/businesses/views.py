# pardonai/businesses/views.py

from __future__ import annotations

from datetime import date, datetime
from io import BytesIO
from typing import Dict, List, Tuple
from .forms import BusinessCoreForm, BusinessProfileForm, ContactFormSet, DocumentFormSet

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import BusinessContact, BusinessDocument, BusinessProfile
from pardonai.dashboard.models import (
    Businesses as CoreBusinesses,
    BusinessType,          # enum: "restaurant, cafe, hotel, beach, bar" vb.
    ServiceDuration,
    ServiceType,
    Status,
)


# -------------------------------------------------------------------
# Yardımcılar
# -------------------------------------------------------------------

def _get_user_businesses(request):
    """
    Kullanıcının erişebildiği işletmeler.
    Varsa accounts.BusinessMembership kullanır; yoksa tümünü döner.
    """
    try:
        from accounts.models import BusinessMembership
        if request.user.is_authenticated:
            return (
                CoreBusinesses.objects
                .filter(memberships__user=request.user, memberships__is_active=True)
                .distinct()
            )
    except Exception:
        pass
    return CoreBusinesses.objects.all()


def _is_trendyol(b: CoreBusinesses) -> bool:
    return (b.business_name or "").strip().lower() == "trendyol"


def _is_cafe_or_restaurant(b: CoreBusinesses) -> bool:
    return b.business_type in {BusinessType.CAFE, BusinessType.RESTAURANT}


# -------------------------------------------------------------------
# Liste – Büyük butonlar (başlıklarla)
# -------------------------------------------------------------------

def business_list(request):
    """
    Butonlar sayfası için context:
      - businesses: bütün erişilebilir işletmeler (order by name)
      - branch_counts: {business_id: şube sayısı}  (BusinessContact.contact_type='address')
      - ecommerce_names: e-ticaret başlığında gösterilecek isimler
        (subject/notes keyword + bilinen markalar)
    """
    qs = _get_user_businesses(request).order_by("business_name")

    # Şube sayıları (address kayıtları)
    addr = (
        BusinessContact.objects.filter(contact_type="address", business_id__in=qs.values("business_id"))
        .values("business_id")
        .annotate(n=Count("id"))
    )
    branch_counts = {row["business_id"]: row["n"] for row in addr}

    # E-ticaret isimleri (dinamik): subject/notes içinde keyword geçenler + bilinenler
    ecommerce_names = set(
        qs.filter(
            Q(subject__iregex=r"e-?ticaret|ecommerce|online")
            | Q(notes__iregex=r"e-?ticaret|ecommerce|online")
        ).values_list("business_name", flat=True)
    )
    # bilinen eklemeler
    ecommerce_names.update({"Trendyol"})

    context = {
        "businesses": qs,
        "branch_counts": branch_counts,
        "ecommerce_names": sorted(ecommerce_names),
    }
    return render(request, "businesses/business_list.html", context)


# -------------------------------------------------------------------
# Detay – Türüne göre içerik
# -------------------------------------------------------------------

@login_required
def business_detail(request, business_id: int):
    """
    - Trendyol: ürün bazlı hesap (şimdilik placeholder)
    - Cafe/Restaurant: şubeler listesi + ekleme
    - Diğerleri: özet (profil/iletişim/belgeler)
    """
    business = get_object_or_404(_get_user_businesses(request), business_id=business_id)

    if _is_trendyol(business):
        return render(
            request,
            "businesses/business_detail.html",
            {"business": business, "mode": "trendyol"},
        )

    if _is_cafe_or_restaurant(business):
        branches = (
            BusinessContact.objects.filter(business=business, contact_type="address")
            .order_by("-is_primary", "id")
        )
        return render(
            request,
            "businesses/business_detail.html",
            {"business": business, "mode": "branches", "branches": branches},
        )

    profile = getattr(business, "profile", None)
    contacts = business.contacts.exclude(contact_type="address")
    documents = business.documents.order_by("-upload_date")[:10]
    return render(
        request,
        "businesses/business_detail.html",
        {
            "business": business,
            "mode": "summary",
            "profile": profile,
            "contacts": contacts,
            "documents": documents,
        },
    )


# -------------------------------------------------------------------
# Şube işlemleri (Cafe/Restaurant)
# -------------------------------------------------------------------

@login_required
@require_http_methods(["POST"])
def branch_add(request, business_id: int):
    business = get_object_or_404(_get_user_businesses(request), business_id=business_id)

    if not _is_cafe_or_restaurant(business):
        messages.error(request, "Bu işletme türü için şube eklenemez.")
        return redirect("businesses:business_detail", business_id=business_id)

    contact_value = (request.POST.get("contact_value") or "").strip()
    is_primary = bool(request.POST.get("is_primary"))
    notes = (request.POST.get("notes") or "").strip()

    if not contact_value:
        messages.error(request, "Adres alanı zorunludur.")
        return redirect("businesses:business_detail", business_id=business_id)

    branch = BusinessContact.objects.create(
        business=business,
        contact_type="address",
        contact_value=contact_value,
        is_primary=is_primary,
        notes=notes,
    )

    if is_primary:
        BusinessContact.objects.filter(
            business=business, contact_type="address", is_primary=True
        ).exclude(pk=branch.pk).update(is_primary=False)

    messages.success(request, "Şube eklendi.")
    return redirect("businesses:business_detail", business_id=business_id)


@login_required
def branch_make_primary(request, business_id: int, contact_id: int):
    business = get_object_or_404(_get_user_businesses(request), business_id=business_id)
    contact = get_object_or_404(
        BusinessContact, pk=contact_id, business=business, contact_type="address"
    )

    BusinessContact.objects.filter(
        business=business, contact_type="address", is_primary=True
    ).exclude(pk=contact.pk).update(is_primary=False)

    contact.is_primary = True
    contact.save(update_fields=["is_primary"])
    messages.success(request, "Ana şube güncellendi.")
    return redirect("businesses:business_detail", business_id=business_id)


# -------------------------------------------------------------------
# Aktif işletme (session'a yaz)
# -------------------------------------------------------------------

@login_required
def activate_business(request, business_id: int):
    business = get_object_or_404(_get_user_businesses(request), business_id=business_id)
    request.session["current_business_id"] = business.business_id
    messages.success(request, f"Aktif işletme: {business.business_name}")
    return redirect("businesses:business_list")


# -------------------------------------------------------------------
# Genel metrikler – bayilerden toplam kâr marjı
# -------------------------------------------------------------------

@login_required
def general_metrics(request):
    """
    Toplam kâr marjı:
      - Öncelik: DealerCommission.commission_amount toplamı
      - Değilse: Dealers.monthly_net_income toplamı
    """
    total_margin = 0
    try:
        from dealers.models import DealerCommission
        total_margin = DealerCommission.objects.aggregate(s=Sum("commission_amount"))["s"] or 0
    except Exception:
        try:
            from dealers.models import Dealers
            total_margin = Dealers.objects.aggregate(s=Sum("monthly_net_income"))["s"] or 0
        except Exception:
            total_margin = 0

    return render(request, "businesses/general_metrics.html", {"total_margin": total_margin})


# -------------------------------------------------------------------
# Excel içe aktarma
# -------------------------------------------------------------------

class ImportExcelForm(forms.Form):
    file = forms.FileField(label="Excel dosyası (.xlsx)")


def _parse_date(val):
    if not val:
        return None
    if isinstance(val, (datetime, date)):
        return val if isinstance(val, date) else val.date()
    s = str(val).strip()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    # tanınmazsa bugünün tarihi
    return date.today()


HEADER_MAP: Dict[str, List[str]] = {
    "business_name": ["işletme adı", "firma adı", "name", "business", "title"],
    "business_address": ["adres", "address", "business address"],
    "owner_first_name": ["sahip adı", "owner first name", "owner name", "first name"],
    "owner_last_name": ["sahip soyadı", "owner last name", "last name"],
    "business_phone": ["işletme telefon", "telefon", "phone"],
    "owner_phone": ["sahip telefon", "owner phone"],
    "interest_solutions": ["ilgi çözümler", "çözüm ilgi", "solutions"],
    "subject": ["konu", "subject"],
    "interest_products": ["ilgi ürünler", "products"],
    "email": ["e-posta", "mail", "email"],
    "notes": ["notlar", "açıklama", "notes", "description"],
    "qr_code_url": ["qr", "qr url", "qr_code_url"],
    "service_type": ["hizmet tipi", "service type"],
    "service_duration": ["hizmet süresi", "service duration"],
    "service_start_date": ["hizmet başlangıç", "service start"],
    "service_end_date": ["hizmet bitiş", "service end"],
    "pos_system_status": ["pos durumu", "pos"],
    "pos_duration": ["pos süresi", "pos duration"],
    "pos_start_date": ["pos başlangıç", "pos start"],
    "pos_end_date": ["pos bitiş", "pos end"],
    "tax_number": ["vergi no", "tax number", "vkn"],
    "business_type": ["işletme türü", "iş türü", "business type"],
    "status": ["durum", "status"],
}


def _normalize(s: str) -> str:
    return (s or "").strip().lower()


def _resolve_field_map(headers: List[str]) -> Dict[int, str]:
    """
    headers: Excel başlıkları
    return: {excel_index: core_field}
    """
    mapping: Dict[int, str] = {}
    for idx, h in enumerate(headers):
        h_norm = _normalize(h)
        for core_field, aliases in HEADER_MAP.items():
            if h_norm == core_field or h_norm in [_normalize(a) for a in aliases]:
                mapping[idx] = core_field
                break
    return mapping


def _iter_excel_rows(xlsx_file) -> Tuple[List[str], List[List[object]]]:
    """
    .xlsx dosyasını openpyxl ile okur, (headers, rows) döner.
    """
    try:
        import openpyxl
    except ImportError:
        raise RuntimeError("openpyxl gerekli: pip install openpyxl")

    wb = openpyxl.load_workbook(filename=BytesIO(xlsx_file.read()), data_only=True)
    ws = wb.active
    rows = list(ws.rows)
    if not rows:
        return [], []
    headers = [
        (cell.value or "").strip() if isinstance(cell.value, str) else cell.value for cell in rows[0]
    ]
    data_rows: List[List[object]] = []
    for r in rows[1:]:
        data_rows.append([cell.value for cell in r])
    return headers, data_rows


@login_required
def import_excel(request):
    """
    Excel içe aktarma:
      - Başlıkları HEADER_MAP ile core alanlara eşler
      - email veya tax_number'a göre get_or_create
      - Enum/string alanlarda lower-case normalize
    """
    if request.method == "POST":
        form = ImportExcelForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                headers, rows = _iter_excel_rows(form.cleaned_data["file"])
            except Exception as e:
                messages.error(request, f"Dosya okunamadı: {e}")
                return render(request, "businesses/import_excel.html", {"form": form})

            field_map = _resolve_field_map(headers)
            if not field_map:
                messages.error(request, "Başlıklar eşleşmedi. Lütfen şablona uygun başlıklar kullanın.")
                return render(
                    request,
                    "businesses/import_excel.html",
                    {"form": form, "headers": headers},
                )

            created, updated, skipped = 0, 0, 0

            with transaction.atomic():
                for row in rows:
                    data = {}
                    for idx, core_field in field_map.items():
                        val = row[idx] if idx < len(row) else None
                        if core_field.endswith("_date"):
                            val = _parse_date(val)
                        data[core_field] = val

                    # normalize string/enum alanları
                    for fld in [
                        "service_type",
                        "service_duration",
                        "pos_system_status",
                        "pos_duration",
                        "business_type",
                        "status",
                    ]:
                        if data.get(fld):
                            data[fld] = str(data[fld]).lower()

                    # kimlik: email > tax_number
                    uniq_filters = {}
                    if data.get("email"):
                        uniq_filters["email"] = data["email"]
                    elif data.get("tax_number"):
                        uniq_filters["tax_number"] = data["tax_number"]

                    if not uniq_filters:
                        skipped += 1
                        continue

                    obj, created_flag = CoreBusinesses.objects.get_or_create(
                        defaults=data, **uniq_filters
                    )
                    if created_flag:
                        created += 1
                    else:
                        # güncelle
                        for k, v in data.items():
                            if v not in (None, ""):
                                setattr(obj, k, v)
                        obj.save()
                        updated += 1

            messages.success(
                request,
                f"Excel içe aktarma tamamlandı. Oluşturulan: {created}, Güncellenen: {updated}, Atlanan: {skipped}",
            )
            return redirect("businesses:business_list")
    else:
        form = ImportExcelForm()

    return render(request, "businesses/import_excel.html", {"form": form})


# -------------------------------------------------------------------
# CRUD – İşletme ekleme/düzenleme/silme (basit form)
# -------------------------------------------------------------------

class InlineBusinessForm(forms.ModelForm):
    class Meta:
        model = CoreBusinesses
        fields = [
            "business_name",
            "business_address",
            "owner_first_name",
            "owner_last_name",
            "email",
            "tax_number",
            "business_type",
            # isteğe bağlı; formda göstermek istersen aşağıdakileri de ekleyebilirsin
            # "subject", "notes", "service_type", "service_duration", "status",
        ]

    def save(self, commit=True):
        obj = super().save(commit=False)
        # Güvenli varsayılanlar (şemayı bozmadan)
        obj.business_phone = obj.business_phone or "+90 000 000 00 00"
        obj.owner_phone = obj.owner_phone or "+90 000 000 00 00"
        obj.interest_solutions = obj.interest_solutions or "Standart"
        obj.subject = obj.subject or "Yeni Kayıt"
        obj.interest_products = obj.interest_products or "Standart"
        obj.qr_code_url = obj.qr_code_url or ""
        obj.service_type = obj.service_type or ServiceType.BASIC
        obj.service_duration = obj.service_duration or ServiceDuration.MONTHLY
        obj.service_start_date = obj.service_start_date or date.today()
        obj.pos_system_status = obj.pos_system_status or "none"
        obj.pos_duration = obj.pos_duration or "monthly"
        obj.status = obj.status or Status.ACTIVE
        obj.registration_date = obj.registration_date or timezone.now()
        if commit:
            obj.save()
        return obj


@login_required
@transaction.atomic
def business_create(request):
    """
    Tek sayfada:
      - CoreBusinesses (işletme)
      - BusinessProfile (profil)
      - BusinessContact (n adet)
      - BusinessDocument (n adet, dosya yüklemeli)
    """
    # QueryString ipuçları (opsiyonel başlangıç değerleri)
    initial = {}
    bt_hint = (request.GET.get("business_type") or "").strip().lower()
    if bt_hint in {"cafe", "restaurant"}:
        initial["business_type"] = bt_hint
    if (request.GET.get("hint") or "").lower() in {"ecommerce", "e-ticaret", "eticaret"}:
        initial.setdefault("subject", "E-ticaret")
        initial.setdefault("notes", "Online satış / e-ticaret kanalı")

    if request.method == "POST":
        core_form = BusinessCoreForm(request.POST)
        profile_form = BusinessProfileForm(request.POST, request.FILES)
        contact_fs = ContactFormSet(request.POST, prefix="c")
        doc_fs = DocumentFormSet(request.POST, request.FILES, prefix="d")

        if core_form.is_valid() and profile_form.is_valid() and contact_fs.is_valid() and doc_fs.is_valid():
            business = core_form.save()  # CoreBusinesses

            # Profil (boş değilse kaydet)
            profile_data = profile_form.cleaned_data
            has_profile_data = any(profile_data.get(k) for k in ["logo", "description", "website", "social_media", "operating_hours", "special_features"])
            if has_profile_data:
                BusinessProfile.objects.update_or_create(
                    business=business,
                    defaults=profile_form.cleaned_data
                )

            # İletişimler
            primaries = []  # address için kontrol
            for f in contact_fs.cleaned_data:
                if f and not f.get("DELETE", False):
                    BusinessContact.objects.create(
                        business=business,
                        contact_type=f["contact_type"],
                        contact_value=f["contact_value"],
                        is_primary=f.get("is_primary", False),
                        notes=f.get("notes", ""),
                    )
                    if f["contact_type"] == "address" and f.get("is_primary"):
                        primaries.append("address")

            # Aynı türde birden çok primary varsa normalize et (en son eklenen primary kalsın)
            if "address" in primaries:
                last_primary = BusinessContact.objects.filter(business=business, contact_type="address", is_primary=True).order_by("-id").first()
                BusinessContact.objects.filter(business=business, contact_type="address", is_primary=True).exclude(pk=last_primary.pk).update(is_primary=False)

            # Belgeler
            for f in doc_fs.cleaned_data:
                if f and not f.get("DELETE", False):
                    BusinessDocument.objects.create(
                        business=business,
                        document_type=f["document_type"],
                        title=f["title"],
                        description=f.get("description", ""),
                        file=f["file"],
                    )

            # (Opsiyonel) Üyelik bağlama (accounts.BusinessMembership varsa)
            try:
                from accounts.models import BusinessMembership, BusinessRole
                BusinessMembership.objects.get_or_create(
                    user=request.user, business=business,
                    defaults={"role": getattr(BusinessRole, "OWNER", "owner")}
                )
            except Exception:
                pass

            messages.success(request, "İşletme ve ilgili bilgiler başarıyla oluşturuldu.")
            return redirect("businesses:business_detail", business_id=business.business_id)
        else:
            messages.error(request, "Lütfen form hatalarını düzeltin.")
    else:
        core_form = BusinessCoreForm(initial=initial)
        profile_form = BusinessProfileForm()
        contact_fs = ContactFormSet(prefix="c")
        doc_fs = DocumentFormSet(prefix="d")

    return render(request, "businesses/business_form_full.html", {
        "core_form": core_form,
        "profile_form": profile_form,
        "contact_fs": contact_fs,
        "doc_fs": doc_fs,
    })


@login_required
def business_edit(request, business_id: int):
    business = get_object_or_404(_get_user_businesses(request), business_id=business_id)
    if request.method == "POST":
        form = InlineBusinessForm(request.POST, instance=business)
        if form.is_valid():
            form.save()
            messages.success(request, "İşletme güncellendi.")
            return redirect("businesses:business_detail", business_id=business_id)
    else:
        form = InlineBusinessForm(instance=business)
    return render(request, "businesses/business_form.html", {"form": form, "business": business})


@login_required
@require_http_methods(["POST"])
def business_delete(request, business_id: int):
    business = get_object_or_404(_get_user_businesses(request), business_id=business_id)
    name = business.business_name
    business.delete()
    messages.success(request, f"İşletme silindi: {name}")
    return redirect("businesses:business_list")


def ecommerce_platform_detail(request, platform_name):
    # platform_name ör: Trendyol
    qs = _get_user_businesses(request).order_by("business_name")
    # Manuel eklenenler: platform_name hariç, subject/notes içinde e-ticaret geçenler
    manual_ecommerce = qs.exclude(business_name=platform_name).filter(
        Q(subject__icontains="e-ticaret") | Q(subject__icontains="ecommerce") | Q(subject__icontains="online") |
        Q(notes__icontains="e-ticaret") | Q(notes__icontains="ecommerce") | Q(notes__icontains="online")
    )
    context = {
        "platform_name": platform_name,
        "manual_ecommerce": manual_ecommerce,
    }
    return render(request, "businesses/ecommerce_platform_detail.html", context)


def ecommerce_business_add(request, platform_name):
    initial = {
        "subject": f"E-ticaret ({platform_name})",
        "notes": f"{platform_name} üzerinden online satış yapan işletme."
    }
    # QueryString ipuçları ile birleştir
    bt_hint = (request.GET.get("business_type") or "").strip().lower()
    if bt_hint in {"cafe", "restaurant"}:
        initial["business_type"] = bt_hint
    if (request.GET.get("hint") or "").lower() in {"ecommerce", "e-ticaret", "eticaret"}:
        initial.setdefault("subject", "E-ticaret")
        initial.setdefault("notes", "Online satış / e-ticaret kanalı")

    if request.method == "POST":
        core_form = BusinessCoreForm(request.POST)
        profile_form = BusinessProfileForm(request.POST, request.FILES)
        contact_fs = ContactFormSet(request.POST, prefix="c")
        doc_fs = DocumentFormSet(request.POST, request.FILES, prefix="d")

        if core_form.is_valid() and profile_form.is_valid() and contact_fs.is_valid() and doc_fs.is_valid():
            business = core_form.save()
            profile_data = profile_form.cleaned_data
            has_profile_data = any(profile_data.get(k) for k in ["logo", "description", "website", "social_media", "operating_hours", "special_features"])
            if has_profile_data:
                BusinessProfile.objects.update_or_create(
                    business=business,
                    defaults=profile_form.cleaned_data
                )
            primaries = []
            for f in contact_fs.cleaned_data:
                if f and not f.get("DELETE", False):
                    BusinessContact.objects.create(
                        business=business,
                        contact_type=f["contact_type"],
                        contact_value=f["contact_value"],
                        is_primary=f.get("is_primary", False),
                        notes=f.get("notes", ""),
                    )
                    if f["contact_type"] == "address" and f.get("is_primary"):
                        primaries.append("address")
            if "address" in primaries:
                last_primary = BusinessContact.objects.filter(business=business, contact_type="address", is_primary=True).order_by("-id").first()
                BusinessContact.objects.filter(business=business, contact_type="address", is_primary=True).exclude(pk=last_primary.pk).update(is_primary=False)
            for f in doc_fs.cleaned_data:
                if f and not f.get("DELETE", False):
                    BusinessDocument.objects.create(
                        business=business,
                        document_type=f["document_type"],
                        title=f["title"],
                        description=f.get("description", ""),
                        file=f["file"],
                    )
            # Üyelik bağlama kaldırıldı (login gereksinimi yok)
            messages.success(request, "E-ticaret işletmesi eklendi.")
            return redirect("businesses:ecommerce_platform_detail", platform_name=platform_name)
        else:
            messages.error(request, "Lütfen form hatalarını düzeltin.")
    else:
        core_form = BusinessCoreForm(initial=initial)
        profile_form = BusinessProfileForm()
        contact_fs = ContactFormSet(prefix="c")
        doc_fs = DocumentFormSet(prefix="d")

    return render(request, "businesses/business_form_full.html", {
        "core_form": core_form,
        "profile_form": profile_form,
        "contact_fs": contact_fs,
        "doc_fs": doc_fs,
        "platform_name": platform_name,
        "is_ecommerce": True,
    })
