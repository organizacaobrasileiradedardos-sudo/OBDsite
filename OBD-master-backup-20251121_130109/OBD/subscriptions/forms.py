from django import forms
from django.contrib.auth.models import User


class SubscriptionUserForm(forms.Form):
    username = forms.CharField(label='Usuário', min_length=4, max_length=150, required=True)
    email = forms.EmailField(label='Email', required=True)
    password = forms.CharField(label='Senha', widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label='Confirmação de senha', widget=forms.PasswordInput, required=True)
    first_name = forms.CharField(label='Nome', required=True)
    last_name = forms.CharField(label='Sobrenome', required=True)

    # Checking if the username is already in use from another User.
    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(u'Usuário "%s" indisponível.' % username)

    # Checking if the email is already in user from another User.
    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return email.lower()
        raise forms.ValidationError(u'Email "%s" já em uso por outro usuário.' % email)

    # Checking if Password1 == Password2
    def clean_password2(self):
        if self.cleaned_data['password'] == self.cleaned_data['password2']:
            return self.cleaned_data['password2']
        else:
            raise forms.ValidationError(u'Senhas informadas nao conferem.')

    def clean_first_name(self):
        return self.cleaned_data['first_name'].lower().capitalize()

    def clean_last_name(self):
        return self.cleaned_data['last_name'].lower().capitalize()
