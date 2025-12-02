from django.test import TestCase


# Create your tests here.
class HomeTest(TestCase):

    def setUp(self):
        self.response = self.client.get('/dashboard/admin/')

    def test_get(self):
        """ GET/admin must result status code 200"""
        self.assertEqual(200, self.response.status_code)

    def test_template(self):
        """ GET/admin must result status template dashadmin.html"""
        self.assertTemplateUsed(self.response, 'dashadmin.html')