from django import forms
from .models import ShopSettings


class ShopSettingsForm(forms.ModelForm):
    class Meta:
        model = ShopSettings
        exclude = ["last_backup_at"]
        widgets = {"address": forms.Textarea(attrs={"rows": 2})}
