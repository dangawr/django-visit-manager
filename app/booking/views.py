from django.views.generic import ListView, CreateView, UpdateView
from .models import Visit, Client
from django.utils import timezone
import datetime
from .forms import VisitFilterForm
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin


class IndexView(ListView):
    template_name = 'booking/index.html'
    model = Visit

    # def get_queryset(self):
    #     today = datetime.datetime.today()
    #     year = today.year
    #     month = today.month
    #     day = today.day
    #
    #     return Visit.objects.filter(date__year=year, date__month=month, date__day=day)

    def get_context_data(self, *, object_list=None, **kwargs):
        today = datetime.datetime.today()
        year = today.year
        month = today.month
        day = today.day

        date = datetime.date.today()

        queryset = object_list if object_list is not None else self.object_list

        if self.request.user.is_authenticated:
            queryset = queryset.filter(client__user=self.request.user)
        else:
            queryset = []

        form = VisitFilterForm(self.request.GET or None)
        if form.is_valid() and queryset:
            date = form.cleaned_data.get('date', '')
            # start_date = form.cleaned_data['start_date']
            # end_date = form.cleaned_data['end_date']
            # category = form.cleaned_data['category']
            # sort = form.cleaned_data['sorting']
            if date:
                queryset = queryset.filter(
                    date__year=date.year,
                    date__month=date.month,
                    date__day=date.day
                    ).order_by('date__time')
        if not any(form.data.dict()) and queryset:
            queryset = queryset.filter(
                date__year=year,
                date__month=month,
                date__day=day
                ).order_by('date__time')
            # if start_date and end_date:
            #     queryset = queryset.filter(date__range=[start_date, end_date])
            # if category:
            #     queryset = queryset.filter(category__id__in=category)
            # if sort:
            #     if sort == 'neutral':
            #         pass
            #     else:
            #         queryset = queryset.order_by(sort)

        return super().get_context_data(
            form=form,
            object_list=queryset,
            display_date=date,
            **kwargs)


class UpdateVisitView(LoginRequiredMixin, UpdateView):
    model = Visit
    fields = ['client', 'date', 'notes']
    template_name_suffix = '_update_form'
    success_url = '/'


class CreateVisitView(LoginRequiredMixin, CreateView):
    model = Visit
    fields = ['client', 'date', 'notes']
    template_name = 'booking/visit_update_form.html'
    success_url = '/'


class CreateClientView(LoginRequiredMixin, CreateView):
    model = Client
    fields = ['first_name', 'last_name', 'phone_number']
    template_name = 'booking/client_create.html'
    success_url = '/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ClientsView(ListView):
    model = Client
    template_name = 'booking/clients.html'

    def get_context_data(self, *, object_list=None, **kwargs):

        queryset = object_list if object_list is not None else self.object_list

        if self.request.GET.get('table-search'):
            queryset = queryset.filter(first_name=self.request.GET.get('table-search'))

        return super().get_context_data(
            object_list=queryset,
            **kwargs)


class SignInView(CreateView):
    form_class = UserCreationForm
    template_name = 'booking/sign_in.html'
    success_url = reverse_lazy('index')


