import datetime
from django import forms
from obd.dashboards.administrators.leagues.models import League
from obd.core.obdlib.standardsession import ObdSession


class NewLeagueForm(forms.Form):
    name = forms.CharField(label='Nome da Liga', required=True)
    description = forms.CharField(label='Descrição', required=True)
    add_info = forms.CharField(label='Informação adicional', required=False)
    start_date = forms.DateField(label='Data Início', required=True)
    end_date = forms.DateField(label='Data Fim', required=True)
    runoff = forms.IntegerField(label='Turnos', required=True)
    phase = forms.IntegerField(label='Fase', required=True)
    scope = forms.IntegerField(label='Abrangência', required=True)
    token = forms.CharField(label='Token', required=True)

    def clean_name(self):
        name = self.cleaned_data['name']
        try:
            n = League.objects.get(name__iexact=name)
        except League.DoesNotExist:
            return name
        else:
            raise forms.ValidationError(f'Já existe uma liga com esse nome "{name}"')

    def clean_start_date(self):
        start = self.cleaned_data['start_date']
        today = datetime.date.today()
        if start < today:
            raise forms.ValidationError(f'A data inicial do evento  não pode ser anterior a data de hoje!')
        else:
            return start

    def clean_end_date(self):
        end = self.cleaned_data['end_date']
        if self.cleaned_data['end_date'] > self.cleaned_data['start_date']:
            return end
        else:
            raise forms.ValidationError(f'A data final da liga deve ser posterior à data inicial!')

    def clean_token(self):
        token = self.cleaned_data['token']
        pin = ObdSession().startSession()
        if token == pin:
            return token
        else:
            raise forms.ValidationError(f'Token informado "{token}" não é válido.')
