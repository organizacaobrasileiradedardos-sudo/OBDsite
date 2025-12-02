from django.test import TestCase
from obd.dashboards.administrators.enviroments.forms import EnviromentForm


class EnviromentsTest(TestCase):

    def setUp(self):
        self.resp = self.client.get('/dashboard/admin/enviroment')
        self.form = self.resp.context['form']

    def test_get(self):
        """Get /enviroment must return status code 200."""
        self.assertEqual(200, self.resp.status_code)

    def test_template(self):
        """ /enviroment must use a template/enviroment.html"""
        self.assertTemplateUsed(self.resp, 'enviroment.html')

    def test_has_form(self):
        """/enviroment Context must have enviromentForm"""
        self.assertIsInstance(self.form, EnviromentForm)

    def test_csrf(self):
        """/enviroment HTML must contain a CSRF key"""
        self.assertContains(self.resp, 'csrfmiddlewaretoken')

    def test_html(self):
        """HTML on Enviroment must contain input tags."""
        self.assertContains(self.resp, '<form')
        self.assertContains(self.resp, '<input', 37)
        self.assertContains(self.resp, 'type="number"', 34)
