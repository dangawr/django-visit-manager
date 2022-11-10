from django import forms
from .models import Visit
import datetime
from django.utils.translation import gettext as _


SORTING_CHOICES = (
    ('neutral', '-------'),
    ('category', 'Category - ascending'),
    ('-category', 'Category - descending'),
    ('date', 'Date - ascending'),
    ('-date', 'Date - descending'),
)
MONTHS = {
    1:_('jan'), 2:_('feb'), 3:_('mar'), 4:_('apr'),
    5:_('may'), 6:_('jun'), 7:_('jul'), 8:_('aug'),
    9:_('sep'), 10:_('oct'), 11:_('nov'), 12:_('dec')
}

class DateInput(forms.DateInput):
    input_type = 'date'


class VisitFilterForm(forms.ModelForm):
    # start_date = forms.DateField(widget=DateInput())
    # end_date = forms.DateField(widget=DateInput())
    # sorting = forms.ChoiceField(choices=SORTING_CHOICES)
    # date = forms.DateField(widget=forms.SelectDateWidget)

    class Meta:
        model = Visit
        fields = ('date',)
        widgets = {'date': forms.SelectDateWidget(months=MONTHS)}
        labels = {'date': 'Select date'}


    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['name'].required = False
    #     self.fields['start_date'].required = False
    #     self.fields['end_date'].required = False
    #     self.fields['category'].required = False
    #     self.fields['sorting'].required = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].initial = datetime.datetime.now()
