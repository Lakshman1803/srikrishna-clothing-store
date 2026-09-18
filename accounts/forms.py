from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class EmployeeForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False,
                                help_text="Leave blank to keep current password when editing.")

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "phone", "role",
                  "is_active_employee", "date_joined_shop"]
        widgets = {
            "date_joined_shop": forms.DateInput(attrs={"type": "date"}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        pwd = self.cleaned_data.get("password")
        if pwd:
            user.set_password(pwd)
        elif not user.pk:
            user.set_password(User.objects.make_random_password())
        if commit:
            user.save()
        return user
