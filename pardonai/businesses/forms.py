from __future__ import annotations
from datetime import date
import json

from django import forms
from django.forms import formset_factory

from pardonai.dashboard.models import (
    Businesses as CoreBusinesses,
    ServiceType, ServiceDuration, BusinessType, Status,
)
from .models import BusinessProfile, BusinessContact, BusinessDocument  # :contentReference[oaicite:1]{index=1}


# --- 2.1 Çekirdek işletme formu (CoreBusinesses)
class BusinessCoreForm(forms.ModelForm):
    class Meta:
        model = CoreBusinesses
        fields = [
            "business_name", "business_address",
            "owner_first_name", "owner_last_name",
            "business_phone", "owner_phone",
            "email", "tax_number",
            "business_type", "status",
            "subject", "notes",
            "service_type", "service_duration",
            "service_start_date", "service_end_date",
            "pos_system_status", "pos_duration",
            "pos_start_date", "pos_end_date",
        ]
        widgets = {
            "business_address": forms.Textarea(attrs={"rows": 2}),
            "notes": forms.Textarea(attrs={"rows": 2}),
            "service_start_date": forms.DateInput(attrs={"type": "date"}),
            "service_end_date": forms.DateInput(attrs={"type": "date"}),
            "pos_start_date": forms.DateInput(attrs={"type": "date"}),
            "pos_end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def save(self, commit=True):
        obj = super().save(commit=False)
        # makul varsayılanlar (boş kalırsa)
        obj.service_type = obj.service_type or ServiceType.BASIC
        obj.service_duration = obj.service_duration or ServiceDuration.MONTHLY
        obj.status = obj.status or Status.ACTIVE
        if commit:
            obj.save()
        return obj


# --- 2.2 Profil formu (OneToOne)
class BusinessProfileForm(forms.ModelForm):
    # JSON alanlarını kullanıcı dostu hale getirelim (textarea -> dict’e çeviri)
    social_media = forms.CharField(
        required=False, widget=forms.Textarea(attrs={"rows": 2}),
        help_text='JSON örn: {"instagram":"@kafe","facebook":"/kafe"}'
    )
    operating_hours = forms.CharField(
        required=False, widget=forms.Textarea(attrs={"rows": 2}),
        help_text='JSON örn: {"mon":"09:00-22:00","sun":"10:00-20:00"}'
    )

    class Meta:
        model = BusinessProfile
        fields = ["logo", "description", "website", "social_media", "operating_hours", "special_features"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "special_features": forms.Textarea(attrs={"rows": 2}),
        }

    def clean_social_media(self):
        raw = self.cleaned_data.get("social_media") or ""
        if not raw.strip():
            return {}
        try:
            return json.loads(raw)
        except Exception:
            raise forms.ValidationError("Geçerli JSON girin (ör. {'instagram':'@kafe'}).")

    def clean_operating_hours(self):
        raw = self.cleaned_data.get("operating_hours") or ""
        if not raw.strip():
            return {}
        try:
            return json.loads(raw)
        except Exception:
            raise forms.ValidationError("Geçerli JSON girin (ör. {'mon':'09:00-22:00'}).")


# --- 2.3 İletişim formu (tek satır)
class SimpleContactForm(forms.Form):
    contact_type = forms.ChoiceField(choices=[("phone", "Telefon"), ("email", "E-Posta"), ("address", "Adres")])
    contact_value = forms.CharField(max_length=255)
    is_primary = forms.BooleanField(required=False)
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 1}))

ContactFormSet = formset_factory(SimpleContactForm, extra=1, can_delete=True)


# --- 2.4 Belge formu (tek satır)
class SimpleDocumentForm(forms.Form):
    document_type = forms.CharField(max_length=100, label="Belge Türü")
    title = forms.CharField(max_length=255, label="Başlık")
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 1}), label="Açıklama")
    file = forms.FileField(required=True, label="Dosya")

DocumentFormSet = formset_factory(SimpleDocumentForm, extra=1, can_delete=True)
