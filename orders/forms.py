from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Client, Order, OrderStatus


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Login",
        widget=forms.TextInput(attrs={"placeholder": "np. admin", "autofocus": True}),
    )
    password = forms.CharField(
        label="Hasło",
        strip=False,
        widget=forms.PasswordInput(attrs={"placeholder": "Twoje hasło"}),
    )


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["name", "company_name", "email", "phone", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 4}),
        }


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "kind",
            "title",
            "service_name",
            "client",
            "status",
            "scheduled_for",
            "quantity",
            "total_price",
            "notes",
            "internal_notes",
        ]
        widgets = {
            "scheduled_for": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={"type": "datetime-local"},
            ),
            "notes": forms.Textarea(attrs={"rows": 4}),
            "internal_notes": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].queryset = OrderStatus.objects.order_by("sort_order", "name")

        scheduled_for = self.initial.get("scheduled_for") or getattr(self.instance, "scheduled_for", None)
        if scheduled_for:
            self.initial["scheduled_for"] = scheduled_for.strftime("%Y-%m-%dT%H:%M")


class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["status"]
