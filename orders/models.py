from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Client(TimestampedModel):
    name = models.CharField("Imię i nazwisko", max_length=120)
    company_name = models.CharField("Firma", max_length=150, blank=True)
    email = models.EmailField("E-mail")
    phone = models.CharField("Telefon", max_length=30)
    notes = models.TextField("Notatki", blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Klient"
        verbose_name_plural = "Klienci"

    def __str__(self):
        if self.company_name:
            return f"{self.name} ({self.company_name})"
        return self.name


class OrderStatus(models.Model):
    name = models.CharField("Nazwa", max_length=60)
    slug = models.SlugField("Slug", unique=True)
    color = models.CharField("Kolor", max_length=7, default="#1d4ed8")
    sort_order = models.PositiveSmallIntegerField("Kolejność", default=1)
    is_closed = models.BooleanField("Zamknięty", default=False)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Status"
        verbose_name_plural = "Statusy"

    def __str__(self):
        return self.name


class Order(TimestampedModel):
    class Kind(models.TextChoices):
        RESERVATION = "reservation", "Rezerwacja"
        ORDER = "order", "Zamówienie"

    kind = models.CharField("Typ", max_length=20, choices=Kind.choices, default=Kind.RESERVATION)
    title = models.CharField("Tytuł", max_length=150)
    service_name = models.CharField("Usługa / produkt", max_length=150)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="orders", verbose_name="Klient")
    status = models.ForeignKey(OrderStatus, on_delete=models.PROTECT, related_name="orders", verbose_name="Status")
    scheduled_for = models.DateTimeField("Termin", blank=True, null=True)
    quantity = models.PositiveIntegerField("Ilość", default=1)
    total_price = models.DecimalField("Kwota", max_digits=10, decimal_places=2, default=0)
    notes = models.TextField("Uwagi od klienta", blank=True)
    internal_notes = models.TextField("Notatki wewnętrzne", blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_orders",
        blank=True,
        null=True,
        verbose_name="Dodał",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="updated_orders",
        blank=True,
        null=True,
        verbose_name="Ostatnio zmienił",
    )

    class Meta:
        ordering = ["status__sort_order", "-created_at"]
        verbose_name = "Zamówienie / rezerwacja"
        verbose_name_plural = "Zamówienia / rezerwacje"

    def __str__(self):
        return f"{self.get_kind_display()} - {self.title}"

    def get_absolute_url(self):
        return reverse("order_detail", kwargs={"pk": self.pk})

    @property
    def is_overdue(self):
        if not self.scheduled_for or self.status.is_closed:
            return False
        return self.scheduled_for < timezone.now()
