from django.views.generic import ListView, CreateView, UpdateView, FormView, DeleteView
from .models import Visit, Client
import datetime
from .forms import VisitFilterForm, VisitsCancelForm, UserRegisterForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.forms import widgets
from .tasks import send_sms_visit_cancelled
from django.core.exceptions import PermissionDenied


class IndexView(ListView):
    """
    Main view. For managing visits.
    """

    template_name = 'booking/index.html'
    model = Visit

    def get_context_data(self, *, object_list=None, **kwargs):
        today = datetime.date.today()

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
                    date=date
                    ).order_by('time')
        if not any(form.data.dict()):    # Default visit filter by today's date if no data in search form
            queryset = queryset.filter(
                date=today
                ).order_by('time')

        return super().get_context_data(
            form=form,
            object_list=queryset,
            display_date=today,
            **kwargs)


class UpdateVisitView(LoginRequiredMixin, UpdateView):
    model = Visit
    fields = '__all__'
    template_name_suffix = '_update_form'
    success_url = '/'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.client.user != self.request.user:
            raise PermissionDenied
        return obj

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['date'].widget = widgets.DateInput(attrs={'type': 'date'})
        form.fields['time'].widget = widgets.TimeInput(attrs={'type': 'time'})
        return form


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


class DeleteVisitView(LoginRequiredMixin, DeleteView):
    model = Visit
    success_url = reverse_lazy('booking:index')
    template_name = 'booking/generic_delete.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.client.user != self.request.user:
            raise PermissionDenied
        return obj


class CancelVisitsView(LoginRequiredMixin, FormView):
    template_name = 'booking/cancel_visits.html'
    form_class = VisitsCancelForm
    success_url = '/'

    def form_valid(self, form):
        user = self.request.user
        from_date = form.cleaned_data.get('from_date')
        to_date = form.cleaned_data.get('to_date')
        visits = Visit.objects.filter(
            client__user=self.request.user,
            date__gte=from_date,
            date__lte=to_date
            )
        if not visits:
            form.add_error(None, 'No visits found for this period')
            return self.form_invalid(form)
        else:
            if form.cleaned_data['send_sms'] and user.sms_remainder:
                if form.cleaned_data['text_message'] == '':
                    form.add_error('text_message', 'This field is required')
                    return self.form_invalid(form)
                if user.balance >= user.sms_price * visits.count():
                    send_sms_visit_cancelled.delay(
                        visits_pk=[visit.pk for visit in visits],
                        text=form.cleaned_data['text_message'],
                        user=user
                        )
                else:
                    form.add_error(None, 'Not enough money on your account')
                    return self.form_invalid(form)
            if form.cleaned_data['send_sms'] and not user.sms_remainder:
                form.add_error(None, 'You have not set up sms remainder')
                return self.form_invalid(form)
            visits.delete()
            return super().form_valid(form)


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

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj


class DeleteClientView(LoginRequiredMixin, DeleteView):
    model = Client
    success_url = reverse_lazy('booking:clients')
    template_name = 'booking/generic_delete.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj


class ClientsView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'booking/clients.html'
    context_object_name = 'clients'
    paginate_by = 20
    ordering = ['-first_name']

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        query = self.request.GET.get("search")
        if query and len(query.split(' ')) == 1:
            queryset = queryset.filter(
                Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(phone_number__icontains=query)
            )
        elif query and len(query.split(' ')) == 2:
            queryset = queryset.filter(
                Q(first_name__icontains=query.split(' ')[0]) & Q(last_name__icontains=query.split(' ')[1]) |
                Q(first_name__icontains=query.split(' ')[1]) & Q(last_name__icontains=query.split(' ')[0])
            )
        return queryset


class SignInView(CreateView):
    form_class = UserRegisterForm
    template_name = 'booking/sign_in.html'
    success_url = reverse_lazy('booking:index')



