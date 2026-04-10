from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Client, Order, OrderStatus


class OrdersViewsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="admin", password="haslo12345")
        self.client.force_login(self.user)
        self.status = OrderStatus.objects.get(slug="nowe")
        self.customer = Client.objects.create(
            name="Jan Kowalski",
            company_name="Firma Test",
            email="jan@example.com",
            phone="123456789",
        )

    def test_dashboard_is_available_for_logged_user(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Panel firmy")

    def test_order_can_be_created(self):
        response = self.client.post(
            reverse("order_create"),
            {
                "kind": Order.Kind.ORDER,
                "title": "Montaż zestawu",
                "service_name": "Pakiet premium",
                "client": self.customer.pk,
                "status": self.status.pk,
                "scheduled_for": "2026-04-09T14:00",
                "quantity": 2,
                "total_price": "399.99",
                "notes": "Klient prosi o kontakt rano.",
                "internal_notes": "Priorytet VIP.",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.count(), 1)
