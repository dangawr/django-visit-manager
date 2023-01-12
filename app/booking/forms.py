from django import forms
from .models import Visit
import datetime
from django.utils.translation import gettext as _


MONTHS = {
    1:_('jan'), 2:_('feb'), 3:_('mar'), 4:_('apr'),
    5:_('may'), 6:_('jun'), 7:_('jul'), 8:_('aug'),
    9:_('sep'), 10:_('oct'), 11:_('nov'), 12:_('dec')
}


class VisitFilterForm(forms.ModelForm):

    class Meta:
        model = Visit
        fields = ('date',)
        widgets = {'date': forms.SelectDateWidget(months=MONTHS)}
        labels = {'date': 'Select date'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].initial = datetime.datetime.now()


class VisitsCancelForm(forms.Form):
    from_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    to_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    send_sms = forms.BooleanField(required=False, label='Send SMS')
    text_message = forms.CharField(widget=forms.Textarea, required=False, label='Message')
