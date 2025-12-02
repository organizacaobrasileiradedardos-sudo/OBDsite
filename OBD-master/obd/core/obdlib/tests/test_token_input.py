from django.test import TestCase
from obd.core.obdlib.token import HashObd


class SubscriptionTokenTest(TestCase):
    def setUp(self):
        self.email = 'walisson@ymail.com'
        self.username = 'TheKabra'
        self.first_name = 'Walisson'

    def test_tokenLenEncript(self):
        """Token must return a string with len() equal to 8."""
        u = HashObd(self.email, self.username, self.first_name)
        size = len(u.encript())
        self.assertEquals(8, size)
