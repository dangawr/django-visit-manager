from django.views.generic import ListView, CreateView, UpdateView
from .models import Visit, Client
import datetime
from .forms import VisitFilterForm
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.forms import widgets


class IndexView(ListView):
    template_name = 'booking/index.html'
    model = Visit

    def get_context_data(self, *, object_list=None, **kwargs):
        today = datetime.date.today()
        today_year = today.year
        today_month = today.month
        today_day = today.day

        queryset = object_list if object_list is not None else self.object_list

        if self.request.user.is_authenticated:
            queryset = queryset.filter(client__user=self.request.user)
        else:
            queryset = queryset.none()

        form = VisitFilterForm(self.request.GET or None)
        if form.is_valid():
            date = form.cleaned_data.get('date', '')
            if date:
                queryset = queryset.filter(
                    date__year=date.year,
                    date__month=date.month,
                    date__day=date.day
                    ).order_by('time')
        if not any(form.data.dict()):    # Default filter by today's date if no data in search form
            queryset = queryset.filter(
                date__year=today_year,
                date__month=today_month,
                date__day=today_day
                ).order_by('time')

        return super().get_context_data(
            form=form,
            object_list=queryset,
            display_date=today,
            **kwargs)


class UpdateVisitView(LoginRequiredMixin, UpdateView):
    model = Visit
    fields = ['client', 'date', 'notes']
    template_name_suffix = '_update_form'
    success_url = '/'


class CreateVisitView(LoginRequiredMixin, CreateView):
    model = Visit
    template_name = 'booking/visit_create_form.html'
    fields = '__all__'
    success_url = '/'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['date'].widget = widgets.DateInput(attrs={'type': 'date'})
        form.fields['time'].widget = widgets.TimeInput(attrs={'type': 'time'})
        return form


class CreateClientView(LoginRequiredMixin, CreateView):
    model = Client
    fields = ['first_name', 'last_name', 'phone_number']
    template_name = 'booking/client_create.html'
    success_url = reverse_lazy('booking:clients')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class UpdateClientView(LoginRequiredMixin, UpdateView):
    model = Client
    fields = ['first_name', 'last_name', 'phone_number']
    template_name_suffix = '_update_form'
    success_url = reverse_lazy('booking:clients')
    context_object_name = 'client'


class ClientsView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'booking/clients.html'
    context_object_name = 'clients'
    paginate_by = 20
    ordering = ['-first_name']

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        query = self.request.GET.get("search")
        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(phone_number__icontains=query)
            )
        return queryset


class SignInView(CreateView):
    form_class = UserCreationForm
    template_name = 'booking/sign_in.html'
    success_url = reverse_lazy('index')


