from django import forms
from .models import Offer


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ["title", "offer_type", "description", "categories", "discount_value",
                  "minimum_purchase", "maximum_discount", "start_date", "end_date", "is_active"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 2}),
            "categories": forms.CheckboxSelectMultiple,
        }
