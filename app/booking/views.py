from django.views.generic import ListView, CreateView, UpdateView
from .models import Visit
from django.utils import timezone
import datetime
from .forms import VisitFilterForm
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy


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

        queryset = object_list if object_list is not None else self.object_list.filter(
            date__year=year,
            date__month=month,
            date__day=day
        ).order_by('date__time')

        form = VisitFilterForm(self.request.GET or None)
        if form.is_valid():
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
                    )
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


class UpdateVisitView(UpdateView):
    model = Visit
    fields = ['client', 'date', 'notes']
    template_name_suffix = '_update_form'
    success_url = '/'


class SignInView(CreateView):
    form_class = UserCreationForm
    template_name = 'booking/sign_in.html'
    success_url = reverse_lazy('index')


