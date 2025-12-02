from django.test import TestCase


# Create your tests here.
class UpdateTest(TestCase):
    def setUp(self):
        self.response = self.client.get('/updates/')

    def test_get(self):
        """ GET /update/ must result status code 200"""
        self.assertEqual(200, self.response.status_code)

    def test_template(self):
        """ GET /update/ must result status template subscription.html"""
        self.assertTemplateUsed(self.response, 'update.html')
