import requests
from bs4 import BeautifulSoup
from django.utils import timezone
from obd.core.models import TournamentResult, PlayerTournamentStat
import re
import json

class N01TournamentScraper:
    def __init__(self, url):
        self.url = url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
            'Origin': 'https://n01darts.com',
            'Referer': 'https://n01darts.com/'
        })

    def get_tournament_id(self):
        # Extract ID from URL (e.g., id=t_pllv_2222)
        match = re.search(r'id=([^&]+)', self.url)
        return match.group(1) if match else None

    def fetch_html(self):
        try:
            response = self.session.get(self.url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching HTML: {e}")
            return None

    def get_api_base(self, html):
        # Try to find the PHP endpoint in the HTML (n01_data object)
        # Look for: phpTournamentStats: "//tk2-..."
        match = re.search(r'phpTournamentStats\s*:\s*["\']([^"\']+)["\']', html)
        if match:
            url = match.group(1)
            if url.startswith('//'):
                url = 'https:' + url
            return url
        # Fallback to the one we found
        return 'https://tk2-228-23746.vs.sakura.ne.jp/n01/tournament/n01_stats_t.php'

    def get_entry_list_url(self, html):
        # Look for: phpTournament: "//tk2-..."
        match = re.search(r'phpTournament\s*:\s*["\']([^"\']+)["\']', html)
        if match:
            url = match.group(1)
            if url.startswith('//'):
                url = 'https:' + url
            return url
        # Fallback
        return 'https://tk2-228-23746.vs.sakura.ne.jp/n01/tournament/n01_tournament.php'

    def run(self):
        tdid = self.get_tournament_id()
        if not tdid:
            return False, "Could not extract Tournament ID from URL"

        html = self.fetch_html()
        if not html:
            return False, "Failed to fetch tournament page"

        # Get API endpoints
        stats_url = self.get_api_base(html)
        entry_url = self.get_entry_list_url(html)

        # 0. Fetch Tournament Metadata (to get name)
        tournament_name = f"Tournament {tdid}"
        try:
            # The get_data command is sent to the entry_url (n01_tournament.php)
            response = self.session.post(entry_url, params={'cmd': 'get_data'}, data=json.dumps({'tdid': tdid}))
            response.raise_for_status()
            meta_data = response.json()
            if meta_data and 'title' in meta_data:
                tournament_name = meta_data['title']
        except Exception as e:
            print(f"Failed to fetch tournament metadata: {e}")
            # Fallback to title tag if API fails
            soup = BeautifulSoup(html, 'html.parser')
            title_tag = soup.find('title')
            if title_tag:
                tournament_name = title_tag.text.strip().replace(" (Competiton stats)", "")

        # 1. Fetch Entry List (to get names)
        try:
            response = self.session.post(entry_url, params={'cmd': 'get_entry_list', 'tdid': tdid})
            response.raise_for_status()
            entry_list = response.json()
        except Exception as e:
            return False, f"Failed to fetch entry list: {e}"

        # Map ID -> Name
        # entry_list is a list of objects: [{"tpid": "...", "name": "..."}]
        player_map = {p['tpid']: p['name'] for p in entry_list if 'tpid' in p}

        # 2. Fetch Stats
        # Try 'stats_list' (Team) first, if empty try 'player_stats_list'
        # But based on JS, it depends on 'team' flag. Let's try both or check which one returns data.
        stats_data = {}
        try:
            # Try stats_list first
            response = self.session.post(stats_url, params={'cmd': 'stats_list', 'tdid': tdid})
            data = response.json()
            if data and isinstance(data, dict) and len(data) > 0 and 'result' not in data:
                 stats_data = data
            else:
                 # Try player_stats_list
                 response = self.session.post(stats_url, params={'cmd': 'player_stats_list', 'tdid': tdid})
                 data = response.json()
                 if data and isinstance(data, dict):
                     stats_data = data
        except Exception as e:
            return False, f"Failed to fetch stats: {e}"

        if not stats_data:
            return False, "No stats data found"

        # 3. Save Data
        tournament, created = TournamentResult.objects.update_or_create(
            source_url=self.url,
            defaults={
                'name': tournament_name,
                'date': timezone.now().date()
            }
        )

        PlayerTournamentStat.objects.filter(tournament=tournament).delete()
        
        count = 0
        for pid, stat in stats_data.items():
            if pid not in player_map:
                continue
                
            name = player_map[pid]
            
            # Calculate averages
            # 3 Dart Avg = (score / darts) * 3
            avg3 = 0.0
            if stat.get('darts', 0) > 0:
                avg3 = (stat.get('score', 0) / stat.get('darts', 0)) * 3
            
            # 1 Dart Avg
            avg1 = avg3 / 3
            
            # First 9 Avg
            avg9 = 0.0
            if stat.get('f9Darts', 0) > 0:
                avg9 = (stat.get('f9Score', 0) / stat.get('f9Darts', 0)) * 3

            # Win Rates
            matches_played = stat.get('match', 0)
            matches_won = stat.get('winMatch', 0)
            wr_match = f"{(matches_won/matches_played)*100:.1f}%" if matches_played > 0 else "0.0%"
            
            legs_played = stat.get('leg', 0)
            legs_won = stat.get('winLeg', 0)
            wr_leg = f"{(legs_won/legs_played)*100:.1f}%" if legs_played > 0 else "0.0%"

            PlayerTournamentStat.objects.create(
                tournament=tournament,
                player_name=name,
                rank=stat.get('rank', 0) if stat.get('rank', 0) > 0 else 999, # 0 usually means unranked or not finished
                matches_played=matches_played,
                matches_won=matches_won,
                legs_played=legs_played,
                legs_won=legs_won,
                legs_diff=legs_won - (legs_played - legs_won), # Approximate diff
                count_100_plus=stat.get('ton00', 0),
                count_140_plus=stat.get('ton40', 0),
                count_170_plus=stat.get('ton70', 0),
                count_180=stat.get('ton80', 0),
                high_finish=stat.get('highOut', 0),
                count_100_plus_finish=stat.get('highOutCount', 0),
                best_leg=stat.get('best', 0),
                worst_leg=stat.get('worst', 0),
                win_rate_matches=wr_match,
                win_rate_legs=wr_leg,
                average_3_dart=round(avg3, 2),
                average_1_dart=round(avg1, 2),
                first_9_average=round(avg9, 2)
            )
            count += 1

        return True, f"Successfully captured {count} player stats for '{tournament_name}'"
