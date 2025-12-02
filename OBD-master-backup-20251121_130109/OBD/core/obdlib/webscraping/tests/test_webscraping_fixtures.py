from django.test import TestCase
import re
from brasilonline.dashboards.webscraping.scraping import AutoScoreScraping

class ValidLinkTest(TestCase):

    def setUp(self):
        self.pattern = {'nakka': re.compile('^(https?:\/\/|www|nakka).*\/n01\/online\/.*mid=.*'),
                   'webcamdarts': re.compile('(https?:\/\/|www|webcamdarts).*.GameOn\/Game\/MatchResult\/[0-9]{6,}'),
                   'lidarts': re.compile('(http.|www|lidarts).*lidarts.[0-9]*'),
                   'dartconnect': '',
                   'godartspro': ''}

        self.scrap = AutoScoreScraping()

        self.link_nakka = ['https://nakka.com/n01/online/n01_view.html?mid=NldcXpuA_1613752131149',
                      'http://nakka.com/n01/online/n01_view.html?mid=NldcXpuA_1613752131149',
                      'www.nakka.com/n01/online/n01_view.html?mid=NldcXpuA_1613752131149',
                      'nakka.com/n01/online/n01_view.html?mid=NldcXpuA_1613752131149']

        self.link_webcamdarts = ['https://www.webcamdarts.com/GameOn/Game/MatchResult/1702305',
                            'http://www.webcamdarts.com/GameOn/Game/MatchResult/1702305',
                            'www.webcamdarts.com/GameOn/Game/MatchResult/1702305',
                            'webcamdarts.com/GameOn/Game/MatchResult/1702305']

        self.link_lidarts = []

    def test_nakka_link_match(self):
        """ Test for NAKKA ER patterns"""
        for link in self.link_nakka:
            with self.subTest():
                self.assertNotEqual(None, self.pattern['nakka'].match(link))

    def test_nakka_not_valid(self):
        self.assertEqual(None, self.pattern['nakka'].match('n01_view.html?mid=NldcXpuA_1613752131149'))


    def test_webcamdarts_link_match(self):
        """ Test for NAKKA ER patterns"""
        for link in self.link_webcamdarts:
            with self.subTest():
                self.assertNotEqual(None, self.pattern['webcamdarts'].match(link))

    def test_webcamdarts_not_valid(self):
        self.assertEqual(None, self.pattern['webcamdarts'].match('Game/MatchResult/1702305'))


    def test_lidarts_link_match(self):
        pass
