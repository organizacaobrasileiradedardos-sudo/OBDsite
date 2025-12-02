from django.test import TestCase


class profileTest(TestCase):

    def setUp(self):
        self.resp = self.client.get('/dashboard/player/profile/view/')

    def test_profile_view(self):
        """GET/profile/view must return status code 200"""
        self.assertEqual(200, self.resp.status_code)

    def test_profile_has_template(self):
        """GET/profile/view must has a template profile_view.html"""
        self.assertTemplateUsed(self.resp, 'profile_view.html')
