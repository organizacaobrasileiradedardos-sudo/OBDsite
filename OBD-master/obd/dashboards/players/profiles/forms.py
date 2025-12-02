from django import forms
from django.contrib.auth.models import User
from obd.dashboards.players.profiles.models import Profile
import requests
from decouple import config


class ProfileForm(forms.Form):

    current = forms.CharField(widget=forms.HiddenInput())
    photo = forms.ImageField(label='Foto do Perfil', required=False)
    birthdate = forms.DateField(label='Aniversário', required=False)
    country = forms.CharField(label='País de Origem', required=False)
    state = forms.CharField(label='Estado/Província', required=False)
    bio = forms.CharField(label='Sobre o Jogador', required=False)
    nickname = forms.CharField(label='Apelido', required=False)
    darts = forms.CharField(label='Dardos/Modelo', required=False)
    facebook = forms.CharField(label='Facebook', required=False)
    social = forms.CharField(label='Outra rede social', required=False)
    site = forms.CharField(label='Site', required=False)


    nakka = forms.CharField(label='Nakka', required=True)





    # Checking if ID already is use on NAKKA
    def clean_nakka(self):
        nakka = self.cleaned_data['nakka']
        if len(nakka.strip()):
            try:
                p = Profile.objects.get(nakka__iexact=nakka)
            except Profile.DoesNotExist:
                return nakka
            else:
                current = self.cleaned_data['current']
                u = User.objects.get(username=current)
                if nakka == u.profile.nakka:
                    return nakka
                else:
                    raise forms.ValidationError(u'ID "%s" usada por outro jogador no Nakka.' % nakka)
        else:
            return nakka
