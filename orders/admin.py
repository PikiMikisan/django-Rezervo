from django.contrib import admin

from .models import Client, Order, OrderStatus


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "company_name", "email", "phone", "created_at")
    search_fields = ("name", "company_name", "email", "phone")


@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order", "is_closed", "color")
    list_editable = ("sort_order", "is_closed", "color")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "client", "status", "scheduled_for", "total_price", "created_at")
    list_filter = ("kind", "status", "scheduled_for")
    search_fields = ("title", "service_name", "client__name", "client__company_name")
    autocomplete_fields = ("client", "status", "created_by", "updated_by")
