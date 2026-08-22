from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from obd.core.obdlib.standardsession import ObdSession

# Class Form for Login action
class LoginUserForm(forms.Form):
    username = forms.CharField(label='Usuário', min_length=4, max_length=150, required=False)
    password = forms.CharField(label='Senha', widget=forms.PasswordInput, required=False)
    token = forms.CharField(label='Token', widget=forms.PasswordInput, required=False)
    email = forms.EmailField(label='Email', required=False)


    def clean_password(self):
        if len(self.cleaned_data['username']) < 4:
            raise forms.ValidationError('Nome do usuário inválido!')
        else:
            user = authenticate(username=self.cleaned_data['username'].lower(), password=self.cleaned_data['password'])
            if user is not None:
                return self.cleaned_data['password']
            else:
                raise forms.ValidationError('Usuário ou senha invalido.')

    def clean_token(self):
        token = self.cleaned_data['token']
        pin = ObdSession().startSession()
        if token == pin:
            return token
        else:
            raise forms.ValidationError('O valor do TOKEN "%s" não confere.' % token)


# Class Update Form for User Login Update like username, password, email.
class UpdateLoginForm(forms.Form):
    username = forms.CharField(label='Usuário', min_length=4, max_length=150, required=True)
    password = forms.CharField(label='Senha', widget=forms.PasswordInput, required=True)
    email = forms.EmailField(label='Email', required=True)
    username2 = forms.CharField(label='Novo Usuário', min_length=4, max_length=150, required=False)
    password2 = forms.CharField(label='Nova Senha', widget=forms.PasswordInput, required=False)
    password3 = forms.CharField(label='Confirme a Senha', widget=forms.PasswordInput, required=False)
    email2 = forms.EmailField(label='Novo Email', required=False)

    def clean_password(self):
        user = authenticate(username=self.cleaned_data['username'].lower(), password=self.cleaned_data['password'])
        if user is not None:
            return self.cleaned_data['password']
        else:
            raise forms.ValidationError('Informe corretamente seu usuário e senha atual.')

    def clean_username2(self):
        username2 = self.cleaned_data['username2']
        if len(str(username2).strip()):
            try:
                u = User.objects.get(username__iexact=username2)
            except User.DoesNotExist:
                return username2
            else:
                raise forms.ValidationError(u'Usuário "%s" não disponível.' % username2)
        else:
            return username2

    def clean_password3(self):
        pass2 = str(self.cleaned_data['password2'])
        pass3 = str(self.cleaned_data['password3'])
        if pass2 == pass3:
            return pass3
        else:
            raise forms.ValidationError(u'Erro ao validar a nova senha.')

    def clean_email2(self):
        email2 = self.cleaned_data['email2']
        if len(str(email2).strip()):
            try:
                u = User.objects.get(email__iexact=email2)
            except User.DoesNotExist:
                return email2
            else:
                raise forms.ValidationError(u'Email informado "%s" não disponível.' % email2)
        else:
            return email2


# Class RecoveryPassword Form to request a password reset link by email.
class RecoveryPasswordForm(forms.Form):
    email = forms.EmailField(label='Email', required=True)


# Class for the player to choose a new password after clicking the reset link.
class SetNewPasswordForm(forms.Form):
    password1 = forms.CharField(label='Nova senha', widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label='Confirme a nova senha', widget=forms.PasswordInput, required=True)

    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        validate_password(password1)
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('As senhas informadas não conferem.')
        return password2





