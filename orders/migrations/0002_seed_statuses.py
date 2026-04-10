from django.db import migrations


def seed_statuses(apps, schema_editor):
    OrderStatus = apps.get_model("orders", "OrderStatus")

    default_statuses = [
        {"name": "Nowe", "slug": "nowe", "color": "#2563eb", "sort_order": 1, "is_closed": False},
        {"name": "W trakcie", "slug": "w-trakcie", "color": "#f59e0b", "sort_order": 2, "is_closed": False},
        {"name": "Oczekuje na klienta", "slug": "oczekuje-na-klienta", "color": "#7c3aed", "sort_order": 3, "is_closed": False},
        {"name": "Zrealizowane", "slug": "zrealizowane", "color": "#15803d", "sort_order": 4, "is_closed": True},
        {"name": "Anulowane", "slug": "anulowane", "color": "#b91c1c", "sort_order": 5, "is_closed": True},
    ]

    for status in default_statuses:
        OrderStatus.objects.update_or_create(slug=status["slug"], defaults=status)


def remove_statuses(apps, schema_editor):
    OrderStatus = apps.get_model("orders", "OrderStatus")
    OrderStatus.objects.filter(
        slug__in=[
            "nowe",
            "w-trakcie",
            "oczekuje-na-klienta",
            "zrealizowane",
            "anulowane",
        ]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_statuses, remove_statuses),
    ]
