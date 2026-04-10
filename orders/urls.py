from django.urls import path

from .views import (
    ClientCreateView,
    ClientListView,
    ClientUpdateView,
    DashboardView,
    OrderCreateView,
    OrderDetailView,
    OrderListView,
    OrderStatusUpdateView,
    OrderUpdateView,
    UserLoginView,
    UserLogoutView,
)
# Define URL patterns for the orders appALL URLS IN THIS APP START WITH /orders/ OR /clients/ OR /login/ OR /logout/ OR /dashboard/ 
urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("orders/", OrderListView.as_view(), name="order_list"),
    path("orders/new/", OrderCreateView.as_view(), name="order_create"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order_detail"),
    path("orders/<int:pk>/edit/", OrderUpdateView.as_view(), name="order_update"),
    path("orders/<int:pk>/status/", OrderStatusUpdateView.as_view(), name="order_status_update"),
    path("clients/", ClientListView.as_view(), name="client_list"),
    path("clients/new/", ClientCreateView.as_view(), name="client_create"),
    path("clients/<int:pk>/edit/", ClientUpdateView.as_view(), name="client_update"),
]
