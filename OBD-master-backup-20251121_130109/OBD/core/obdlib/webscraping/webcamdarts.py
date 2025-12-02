import json
import ssl
import copy
import requests
import re
from decouple import config


class WebcamdartsScraping:
    """ This class is a collection of attributes and methods for WEBSCRAP results from
     score = WebcamdartsScraping()
     print(score.start_by(name='The Kabra'))
    WEBCAMDARTS"""

    url_boa = config('OBD_URL')
    webcamdarts_url = config('HTML_WEBCAMDARTS_LINK')
    pattern = re.compile(r'(https?://|www|webcamdarts).*.GameOn/Game/MatchResult/[0-9]{6,}')

    def __init__(self):

        self.match = {'general': {
            'date': '',
            'server': '',
            'winner': '',
            'drawn': '',
            'html_link': '',
            'user_link': '',
            'id': ''
        },
            'p1': {
                'name': '',
                'sets': 0,
                'legs': 0,
                'first9': 0,
                'average': 0,
                'single_average': 0,
                'highest_out': 0,
                'best_leg': 0,
                'tons': 0,
                'ton40': 0,
                'ton70': 0,
                'ton80': 0
            },
            'p2': {
                'name': '',
                'sets': 0,
                'legs': 0,
                'first9': 0,
                'average': 0,
                'single_average': 0,
                'highest_out': 0,
                'best_leg': 0,
                'tons': 0,
                'ton40': 0,
                'ton70': 0,
                'ton80': 0
            }
        }

        # [0] to [2] for auto scrap, [3] for url/link scrap.
        self.matches = [{}, {}, {}, {}]

        ssl._create_default_https_context = ssl._create_unverified_context

    def __str__(self):
        return self.url_boa

    def validade_user(self, name):
        link = config('MEMBER_STATS_WEBCAMDARTS')+str(name).replace(' ', '%20')
        status = requests.get(link).status_code
        if status == 200:
            return True
        else:
            return False

    def start_by(self, auto_only=True, link='', name=''):
        """fromUrl(link) will receive the link from players and call correct method for
        game stats resolution"""

        if not self.validade_user(name):
            return False

        if auto_only is not False:
            self.get_results(auto_only=True, name=name, page_max=15)
            return self.matches
        else:
            if auto_only is False:
                if self.pattern.match(link):
                    self.match['general']['server'] = 'WEBCAMDARTS'
                    self.get_results(auto_only=False, link=link, name=name, page_max=30)
                    return self.matches[3]
                else:
                    return False

    def get_results(self, auto_only, page_max, link='', name=''):

        filter_name = "AnyPlayer~eq~'" + str(name) + "'"

        payload = {
            'sort': 'GameResultId-desc',
            'page': '1',
            'pageSize': page_max,
            'group': '',
            'filter': filter_name,
        }

        # Start connection to WEBCAMDARTS using POST and PAYLOAD DATA method.
        content = requests.post(self.webcamdarts_url, data=payload).text

        # Saving content from WEBCAMDARTS to OBD JSON STATS
        webcamdarts_stats = json.loads(content)

        # If data by link, need to get the right ID for index at dict
        if auto_only == False:
            match_id = link.split('MatchResult/')[1]
            for page in range(page_max):
                self.retrieve_data(index=page, data=webcamdarts_stats)
                if int(webcamdarts_stats['Data'][page]['GameResultId']) == int(match_id):
                    self.matches[3] = copy.deepcopy(self.match)
                    return self.matches[3]
        else:
            if auto_only:
                for page in range(page_max):
                    self.retrieve_data(index=page, data=webcamdarts_stats)
                    self.matches[page] = copy.deepcopy(self.match)

    def retrieve_data(self, index, data):
        players = data['Data'][index]['Title'].split(' Vs ')
        game = data['Data'][index]
        p1 = game['Stats'][players[0]]
        p2 = game['Stats'][players[1]]

        # Data for GENERAL or Winner Set Definition
        self.match['general']['date'] = game['MatchDate']
        self.match['general']['server'] = 'WEBCAMDARTS'
        self.match['general']['winner'] = game['Winner']
        self.match['general']['drawn'] = game['Drawn']
        self.match['general']['html_link'] = self.webcamdarts_url
        self.match['general']['id'] = game['GameResultId']
        self.match['general']['user_link'] = config('USER_WEBCAMDARTS_LINK')+str(self.match['general']['id'])

        p1_score = int(p1['Legs'])
        p2_score = int(p2['Legs'])

        if p1_score == p2_score:
            self.match['p1']['sets'] = 0
            self.match['p2']['sets'] = 0
        else:
            if p1_score > p2_score:
                self.match['p1']['sets'] = 1
                self.match['p2']['sets'] = 0
            else:
                self.match['p1']['sets'] = 0
                self.match['p2']['sets'] = 1

        # Data for P1 Stats
        self.match['p1']['name'] = p1['User']
        self.match['p1']['legs'] = p1['Legs']
        self.match['p1']['average'] = p1['ThreeDartAverage']
        self.match['p1']['single_average'] = p1['OneDartAverage']
        self.match['p1']['highest_out'] = p1['HighestOut']
        self.match['p1']['best_leg'] = p1['BestLeg']
        self.match['p1']['tons'] = p1['Tons']
        self.match['p1']['ton40'] = p1['TonForty']
        self.match['p1']['ton70'] = p1['TonSeventy']
        self.match['p1']['ton80'] = p1['Maximums']

        # Data for P2 Stats
        self.match['p2']['name'] = p2['User']
        self.match['p2']['legs'] = p2['Legs']
        self.match['p2']['average'] = p2['ThreeDartAverage']
        self.match['p2']['single_average'] = p2['OneDartAverage']
        self.match['p2']['highest_out'] = p2['HighestOut']
        self.match['p2']['best_leg'] = p2['BestLeg']
        self.match['p2']['tons'] = p2['Tons']
        self.match['p2']['ton40'] = p2['TonForty']
        self.match['p2']['ton70'] = p2['TonSeventy']
        self.match['p2']['ton80'] = p2['Maximums']

    def serialize(self, form):
        pass

