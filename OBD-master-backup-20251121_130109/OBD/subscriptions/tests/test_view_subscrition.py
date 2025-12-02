from django.core import mail
from django.test import TestCase
from brasilonline.subscriptions.forms import SubscriptionUserForm
from django.contrib.auth.models import User


class SubscribeGet(TestCase):

    def setUp(self):
        self.resp = self.client.get('/subscribe/')
        self.form = self.resp.context['form']

    def test_get(self):
        """Get /subscribe must return status code 200."""
        self.assertEqual(200, self.resp.status_code)

    def test_template(self):
        """ Must use a template/subscriptions.html"""
        self.assertTemplateUsed(self.resp, 'subscription.html')

    def test_html(self):
        """HTML must contain input tags."""
        self.assertContains(self.resp, '<form')
        self.assertContains(self.resp, '<input', 10)
        self.assertContains(self.resp, 'type="text"', 3)
        self.assertContains(self.resp, 'type="email"', 1)
        self.assertContains(self.resp, 'type="password"', 2)

    def test_csrf(self):
        """HTML must contain a CSRF key"""
        self.assertContains(self.resp, 'csrfmiddlewaretoken')

    def test_has_form(self):
        """Context must have subscription form"""
        self.assertIsInstance(self.form, SubscriptionUserForm)

    def test_form_has_fields(self):
        """Form must have 6 fields"""
        self.assertSequenceEqual(['username',
                                  'email',
                                  'password',
                                  'password2',
                                  'first_name',
                                  'last_name'],
                                 list(self.form.fields))


class SubscribePostValid(TestCase):

    def setUp(self):
        data = dict(username='TheKabra',
                    email='woliv88@outlook.com',
                    password='mykey',
                    password2='mykey',
                    first_name='Walisson',
                    last_name='Oliveira'
                    )
        self.resp = self.client.post('/subscribe/', data)


    def test_post(self):
        """Valid Post should redirect to /subscribe/"""
        self.assertEqual(302, self.resp.status_code)

    def test_send_subscribe_email(self):
        """Valid Post should send email to new member"""
        self.assertEqual(1, len(mail.outbox))

    def test_save_subscription(self):
        """Valid Post should save a User Model Instance"""
        self.assertTrue(User.objects.exists())


class SubscribePostInvalid(TestCase):
    def setUp(self):
        self.resp = self.client.post('/subscribe/', {})

    def test_post(self):
        """Invalid POST should not redirect to"""
        self.assertEqual(200, self.resp.status_code)

    def test_template(self):
        self.assertTemplateUsed(self.resp, 'subscription.html')

    def test_has_form(self):
        form = self.resp.context['form']
        self.assertIsInstance(form, SubscriptionUserForm)

    def test_form_has_error(self):
        form = self.resp.context['form']
        self.assertTrue(form.errors)

    def test_dont_save_subscription(self):
        """Invalid Post should not save a  User Model Instance"""
        self.assertFalse(User.objects.exists())


class SubscribeSuccessMessage(TestCase):
    def test_message(self):
        data = dict(username='TheKabra',
                    email='woliv88@outlook.com',
                    password='mykey',
                    password2='mykey',
                    first_name='Walisson',
                    last_name='Oliveira'
                    )
        response = self.client.post('/subscribe/', data, follow=True)
        self.assertContains(response, 'Associação realizada com sucesso!')





