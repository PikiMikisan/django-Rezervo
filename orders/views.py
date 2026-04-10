from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q, Sum
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView

from .forms import ClientForm, LoginForm, OrderForm, StatusUpdateForm
from .models import Client, Order, OrderStatus


class UserLoginView(LoginView):
    authentication_form = LoginForm
    template_name = "registration/login.html"
    redirect_authenticated_user = True


class UserLogoutView(LogoutView):
    pass


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "orders/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stats"] = {
            "orders_total": Order.objects.count(),
            "orders_open": Order.objects.filter(status__is_closed=False).count(),
            "orders_closed": Order.objects.filter(status__is_closed=True).count(),
            "clients_total": Client.objects.count(),
            "revenue_total": Order.objects.aggregate(total=Sum("total_price"))["total"] or 0,
        }
        context["status_summary"] = OrderStatus.objects.annotate(total=Count("orders"))
        context["recent_orders"] = Order.objects.select_related("client", "status").order_by("-created_at")[:6]
        context["upcoming_orders"] = (
            Order.objects.select_related("client", "status")
            .filter(scheduled_for__isnull=False, status__is_closed=False)
            .order_by("scheduled_for")[:6]
        )
        return context


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "orders/order_list.html"
    context_object_name = "orders"
    paginate_by = 12

    def get_queryset(self):
        queryset = Order.objects.select_related("client", "status", "created_by")
        query = self.request.GET.get("q", "").strip()
        selected_status = self.request.GET.get("status", "").strip()
        selected_kind = self.request.GET.get("kind", "").strip()

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(service_name__icontains=query)
                | Q(client__name__icontains=query)
                | Q(client__company_name__icontains=query)
            )
        if selected_status:
            queryset = queryset.filter(status__slug=selected_status)
        if selected_kind:
            queryset = queryset.filter(kind=selected_kind)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statuses"] = OrderStatus.objects.all()
        context["selected_status"] = self.request.GET.get("status", "")
        context["selected_kind"] = self.request.GET.get("kind", "")
        context["query"] = self.request.GET.get("q", "")
        context["kinds"] = Order.Kind.choices
        return context


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "orders/order_detail.html"
    context_object_name = "order"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_form"] = StatusUpdateForm(instance=self.object)
        return context


class OrderCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = "orders/order_form.html"
    success_message = "Zapisano nowe zgłoszenie."

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class OrderUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = "orders/order_form.html"
    success_message = "Zmiany zostały zapisane."

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class OrderStatusUpdateView(LoginRequiredMixin, UpdateView):
    model = Order
    form_class = StatusUpdateForm
    http_method_names = ["post"]

    def form_valid(self, form):
        order = form.save(commit=False)
        order.updated_by = self.request.user
        order.save(update_fields=["status", "updated_by", "updated_at"])
        messages.success(self.request, "Status został zaktualizowany.")
        return redirect(order.get_absolute_url())

    def form_invalid(self, form):
        messages.error(self.request, "Nie udało się zmienić statusu.")
        return redirect("order_detail", pk=self.object.pk)


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "orders/client_list.html"
    context_object_name = "clients"
    paginate_by = 12

    def get_queryset(self):
        queryset = Client.objects.all()
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query)
                | Q(company_name__icontains=query)
                | Q(email__icontains=query)
                | Q(phone__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        return context


class ClientCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "orders/client_form.html"
    success_url = reverse_lazy("client_list")
    success_message = "Dodano nowego klienta."


class ClientUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "orders/client_form.html"
    success_url = reverse_lazy("client_list")
    success_message = "Dane klienta zostały zapisane."
