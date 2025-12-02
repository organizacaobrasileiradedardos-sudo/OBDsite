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
    webcamdarts = forms.CharField(label='Webcamdarts', required=True)
    nakka = forms.CharField(label='Nakka', required=True)
    lidarts = forms.CharField(label='Lidarts', required=False)
    dartconnect = forms.CharField(label='DartConnect', required=False)
    godartspro = forms.CharField(label='GoDartsPro', required=False)
    nationalfederation = forms.CharField(label='ID Federação Nacional', required=False)
    localfederation = forms.CharField(label='ID Federação Local', required=False)



    # Checking if ID already is use on WEBCADARTS
    def clean_webcamdarts(self):
        webcamdarts = self.cleaned_data['webcamdarts']

        link = config('MEMBER_STATS_WEBCAMDARTS')+webcamdarts.replace(' ', '%20')
        if requests.get(link).status_code == 500:
            raise forms.ValidationError(f'O usuário "{webcamdarts}" não foi encontrado na base do WEBCAMDARTS.')

        if len(webcamdarts.strip()):
            try:
                p = Profile.objects.get(webcamdarts__iexact=webcamdarts)
            except Profile.DoesNotExist:
                return webcamdarts
            else:
                current = self.cleaned_data['current']
                u = User.objects.get(username=current)
                if webcamdarts == u.profile.webcamdarts:
                    return webcamdarts
                else:
                    raise forms.ValidationError(u'ID "%s" usada por outro jogador em Webcamdarts.' % webcamdarts)
        else:
            return webcamdarts

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

    # Checking if ID already is use on LIDARTS
    def clean_lidarts(self):
        lidarts = self.cleaned_data['lidarts']
        if len(lidarts.strip()):
            try:
                p = Profile.objects.get(lidarts__iexact=lidarts)
            except Profile.DoesNotExist:
                return lidarts
            else:
                current = self.cleaned_data['current']
                u = User.objects.get(username=current)
                if lidarts == u.profile.lidarts:
                    return lidarts
                else:
                    raise forms.ValidationError(u'ID "%s" usada por outro jogador no Lidarts.' % lidarts)
        else:
            return lidarts

    # Checking if ID already is use on DARTCONNECT
    def clean_dartconnect(self):
        dartconnect = self.cleaned_data['dartconnect']
        if len(dartconnect.strip()):
            try:
                p = Profile.objects.get(dartconnect__iexact=dartconnect)
            except Profile.DoesNotExist:
                return dartconnect
            else:
                current = self.cleaned_data['current']
                u = User.objects.get(username=current)
                if dartconnect == u.profile.dartconnect:
                    return dartconnect
                else:
                    raise forms.ValidationError(u'ID "%s" usada por outro jogador no DartConnetc.' % dartconnect)
        else:
            return dartconnect

    # Checking if ID already is use on GODARTSPRO
    def clean_godartspro(self):
        godartspro = self.cleaned_data['godartspro']
        if len(godartspro.strip()):
            try:
                p = Profile.objects.get(godartspro__iexact=godartspro)
            except Profile.DoesNotExist:
                return godartspro
            else:
                current = self.cleaned_data['current']
                u = User.objects.get(username=current)
                if godartspro == u.profile.godartspro:
                    return godartspro
                else:
                    raise forms.ValidationError(u'ID "%s" usada por outro jogador no GoDartsPro.' % godartspro)
        else:
            return godartspro