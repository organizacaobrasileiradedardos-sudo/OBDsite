from django.core import mail
from django.test import TestCase
from obd.subscriptions.forms import SubscriptionForm


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
        self.email = mail.outbox[0]

    def test_subscription_email_subject(self):
        expect = 'Confirmação de Associação ao OBD'
        self.assertEqual(expect, self.email.subject)

    def test_subscription_email_from(self):
        expect = 'noreply@obdassociacao.com.br'
        self.assertEqual(expect, self.email.from_email)

    def test_subscription_email_to(self):
        expect = ['noreply@obdassociacao.com.br', 'woliv88@outlook.com']
        self.assertEqual(expect, self.email.to)

    def test_subscription_email_body(self):
        contents = ['Walisson',
                   'Oliveira',
                   'woliv88@outlook.com',
                   'TheKabra']
        for content in contents:
            with self.subTest():
                self.assertIn(content, self.email.body)




