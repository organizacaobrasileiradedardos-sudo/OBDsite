from django.test import TestCase


# Create your tests here.
class DashBoardPlayerTest(TestCase):

    def setUp(self):
        self.response = self.client.get('/dashboard/player/')

    def test_get(self):
        """ GET/user must result status code 200"""
        self.assertEqual(200, self.response.status_code)

    def test_template(self):
        """ GET/User must result status template dashuser.html"""
        self.assertTemplateUsed(self.response, 'dashuser.html')