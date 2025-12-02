import json
import ssl
import copy
from urllib.request import urlopen
import re
from decouple import config


class NakkaScraping:
    """ This class is a collection of attributes and methods for WEBSCRAP results from
    NAKKA.

    To use this class, do the following:

    results = NakkaScraping()
    results.start_by(auto_only=True, name='Nickname') or;
    results.start_by(auto_only=False, link='http://nakka/match/midd', name='Nickname')
    All results are on self.matches (list) where: [auto][auto][auto][link]
    """

    url_boa = config('OBD_URL')
    html_base_link = config('HTML_NAKKA_LINK')
    nakka_user_link = config('USER_NAKKA_LINK')
    pattern = re.compile(r'^(https?://|www.|)nakka.com/n01/online/history/.*mid=.*$')

    def __init__(self):
        self.match = {'general': {
                    'date': '',
                    'server': 'NAKKA',
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

    def reset(self):
        pass

    def validade_user(self, name):
        name = name.replace(' ', '%20')
        link = config('SEARCH_NAKKA_LINK')+name+'%22'
        con = urlopen(link)
        content = con.read()
        content = json.loads(content)
        if len(content) != 0:
            return True
        else:
            return False

    def start_by(self, auto_only=True, link='', name=''):
        """fromUrl(link) will receive the link from players and call correct method for
        game stats resolution"""

        if auto_only is not False:
            self.get_results(auto_only=True, name=name, page_max=3)
            return self.matches
        else:
            if auto_only is False:
                if self.pattern.match(link):
                    self.match['general']['user_link'] = link
                    self.match['general']['server'] = 'NAKKA'
                    self.get_results(auto_only=False, link=link, page_max=0)
                    if len(self.matches[3]) > 0:
                        return self.matches[3]
                    else:
                        return False
                else:
                    self.match['general']['user_link'] = link
                    return False


    def get_results(self, auto_only, page_max, link='', name=''):

        if auto_only:
            search_for = name.replace(' ', '%20')
            html_search_link = config('SEARCH_NAKKA_LINK')+search_for+'%22'

            # Connecting to Nakka using GET method for first base JSON
            connection = urlopen(html_search_link)
            content = connection.read()
            content = json.loads(content)

            #For the case invalid or wrong link
            if len(content) == 0:
                return False

            # Retrieving CONTENT to get first MID ID MATCH and user links and save basic URLS
            for page in range(page_max):
                backup_match = copy.deepcopy(self.match)
                self.match['general']['id'] = content[page]['mid']
                self.match['general']['html_link'] = self.html_base_link+self.match['general']['id']
                self.match['general']['user_link'] = self.nakka_user_link+self.match['general']['id']
                self.retrieve_data()
                self.matches[page] = copy.deepcopy(self.match)
                self.match = copy.deepcopy(backup_match)

        if auto_only is False:
            # Saving ID and basic URLS for MID match
            self.match['general']['id'] = link.split('mid=')[1]
            self.match['general']['html_link'] = self.html_base_link + str(self.match['general']['id'])
            self.match['general']['user_link'] = self.nakka_user_link + str(self.match['general']['id'])
            if self.retrieve_data():
                self.matches[3] = copy.deepcopy(self.match)
            else:
                return False


    def retrieve_data(self):
        # Retrieving CONTENT to get all MATCH data
        connection = urlopen(self.match['general']['html_link'])
        content = connection.read()
        content = json.loads(content)

        # For the case invalid or wrong link
        if len(content) == 0:
            return False

        # Get basic data like Name, Sets, Legs
        p1 = content['statsData'][0]
        p2 = content['statsData'][1]

        # Empty list for 100, 140, 170 and 180 hits for P1 and P2
        stats = [[0, 0, 0, 0], [0, 0, 0, 0]]
        # Calculating stats for 100, 140, 180
        leg_data = content['legData']
        for k in range(len(stats)):
            for legs in range(len(leg_data)):
                for scores in range(len(leg_data[legs]['playerData'][k])):
                    if leg_data[legs]['playerData'][k][scores]['score'] > 179:
                        stats[k][3] = stats[k][3] + 1
                    else:
                        if (leg_data[legs]['playerData'][k][scores]['score']) > 169:
                            stats[k][2] = stats[k][2] + 1
                        else:
                            if leg_data[legs]['playerData'][k][scores]['score'] > 139:
                                stats[k][1] = stats[k][1] + 1
                            else:
                                if leg_data[legs]['playerData'][k][scores]['score'] > 99:
                                    stats[k][0] = stats[k][0] + 1

        # Saving data for GENERAL dict
        self.match['general']['date'] = content['startTime']
        self.match['general']['server'] = 'NAKKA'

        if p1['winLegs'] == p2['winLegs']:
            self.match['general']['winner'] = ''
            self.match['general']['drawn'] = True
            self.match['p1']['sets'] = 0
            self.match['p2']['sets'] = 0
        else:
            if p1['winLegs'] > p2['winLegs']:
                self.match['general']['winner'] = p1['name']
                self.match['p1']['sets'] = 1
                self.match['p2']['sets'] = 0
            else:
                self.match['general']['winner'] = p2['name']
                self.match['p1']['sets'] = 0
                self.match['p2']['sets'] = 1

        # Calculating Best_Leg and Highest Out for P1 and P2. If set no finished, endFlag=0, must break loop.
        for legs in range(len(leg_data)):
            if leg_data[legs]['endFlag'] == 0:
                break
            winner = leg_data[legs]['winner']
            score_left = leg_data[legs]['playerData'][winner][-2]['left']
            total_darts = (len(leg_data[legs]['playerData'][winner])-2)*3
            all_darts_valid = total_darts + abs(leg_data[legs]['playerData'][winner][-1]['score'])
            if winner == 0:
                if self.match['p1']['best_leg'] > all_darts_valid or self.match['p1']['best_leg'] == 0:
                    self.match['p1']['best_leg'] = all_darts_valid
                if self.match['p1']['highest_out'] < score_left:
                    self.match['p1']['highest_out'] = score_left
            else:
                if winner == 1:
                    if self.match['p2']['best_leg'] > all_darts_valid or self.match['p2']['best_leg'] == 0:
                        self.match['p2']['best_leg'] = all_darts_valid
                    if self.match['p2']['highest_out'] < score_left:
                        self.match['p2']['highest_out'] = score_left

        # Data for P1 Stats
        self.match['p1']['name'] = p1['name']
        self.match['p1']['legs'] = p1['winLegs']
        self.match['p1']['average'] = round((p1['allScore'] / p1['allDarts']) * 3, 2)
        self.match['p1']['single_average'] = round(int(self.match['p1']['average']) / 3, 2)
        self.match['p1']['tons'] = stats[0][0]
        self.match['p1']['ton40'] = stats[0][1]
        self.match['p1']['ton70'] = stats[0][2]
        self.match['p1']['ton80'] = stats[0][3]

        #100+ score correction
        if (self.match['p1']['highest_out'] > 99) and (self.match['p1']['highest_out'] < 140):
            self.match['p1']['tons'] = self.match['p1']['tons'] + 1

        if (self.match['p1']['highest_out'] > 139) and (self.match['p1']['highest_out'] < 169):
            self.match['p1']['ton40'] = self.match['p1']['ton40'] + 1

        if (self.match['p1']['highest_out'] > 169) and (self.match['p1']['highest_out'] < 180):
            self.match['p1']['ton70'] = self.match['p1']['ton70'] + 1


        # Data for P2 Stats
        self.match['p2']['name'] = p2['name']
        self.match['p2']['legs'] = p2['winLegs']
        self.match['p2']['average'] = round((p2['allScore'] / p2['allDarts']) * 3, 2)
        self.match['p2']['single_average'] = round(int(self.match['p2']['average']) / 3, 2)
        self.match['p2']['tons'] = stats[1][0]
        self.match['p2']['ton40'] = stats[1][1]
        self.match['p2']['ton70'] = stats[1][2]
        self.match['p2']['ton80'] = stats[1][3]

        #100+ score correction
        if (self.match['p2']['highest_out'] > 99) and (self.match['p2']['highest_out'] < 140):
            self.match['p2']['tons'] = self.match['p2']['tons'] + 1

        if (self.match['p2']['highest_out'] > 139) and (self.match['p2']['highest_out'] < 169):
            self.match['p2']['ton40'] = self.match['p2']['ton40'] + 1

        if (self.match['p2']['highest_out'] > 169) and (self.match['p2']['highest_out'] < 180):
            self.match['p2']['ton70'] = self.match['p2']['ton70'] + 1

        return True

