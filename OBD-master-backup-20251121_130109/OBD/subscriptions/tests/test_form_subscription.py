from django.core import mail
from django.test import TestCase
from brasilonline.subscriptions.forms import SubscriptionUserForm


class SubscriptionUserFormTest(TestCase):
    def setUp(self):
        self.form = SubscriptionUserForm()

    def test_form_has_fields(self):
        expected = ['username', 'email', 'password', 'password2', 'first_name', 'last_name']
        self.assertSequenceEqual(expected, list(self.form.fields))
