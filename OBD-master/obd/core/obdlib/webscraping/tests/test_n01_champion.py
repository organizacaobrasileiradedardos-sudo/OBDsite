from django.test import TestCase
from unittest.mock import MagicMock, patch
from obd.core.obdlib.webscraping.n01 import N01TournamentScraper
from obd.dashboards.administrators.champions.models import Champion
from obd.dashboards.administrators.leagues.models import League
from obd.dashboards.players.profiles.models import Profile
from django.contrib.auth.models import User
import json

class N01ChampionCaptureTest(TestCase):
    def setUp(self):
        self.url = "https://n01darts.com/n01/tournament/comp.php?id=t_test_123"
        self.scraper = N01TournamentScraper(self.url)

    @patch('obd.core.obdlib.webscraping.n01.requests.Session')
    def test_champion_capture(self, mock_session_cls):
        # Setup mock session
        mock_session = mock_session_cls.return_value
        self.scraper.session = mock_session

        # Mock HTML response (get_api_base and get_entry_list_url)
        mock_html = """
        <html>
        <head><title>Test Tournament</title></head>
        <body>
        <script>
        var phpTournamentStats = "https://tk2.example.com/stats.php";
        var phpTournament = "https://tk2.example.com/tournament.php";
        </script>
        </body>
        </html>
        """
        
        # Mock responses
        # 1. fetch_html
        # 2. get_data (metadata)
        # 3. get_entry_list
        # 4. stats_list (or player_stats_list)
        
        # We need to configure side_effect for session.get and session.post
        
        # Mock GET response for fetch_html
        mock_response_html = MagicMock()
        mock_response_html.text = mock_html
        mock_response_html.raise_for_status.return_value = None
        
        mock_session.get.return_value = mock_response_html

        # Mock POST responses
        # Response for get_data
        mock_response_meta = MagicMock()
        mock_response_meta.json.return_value = {'title': 'Campeonato Brasileiro OBD 2025'}
        mock_response_meta.raise_for_status.return_value = None

        # Response for get_entry_list
        mock_response_entry = MagicMock()
        mock_response_entry.json.return_value = [
            {'tpid': 'p1', 'name': 'Roberto Wentz'},
            {'tpid': 'p2', 'name': 'Other Player'},
            {'tpid': 'p3', 'name': 'Third Player'}
        ]
        mock_response_entry.raise_for_status.return_value = None

        # Response for stats_list
        mock_response_stats = MagicMock()
        # Stats data with rank 1 for Roberto Wentz, rank 2 for Runner Up, rank 3 for Third Place
        stats_data = {
            'p1': {
                'rank': 1,
                'match': 10, 'winMatch': 10,
                'leg': 50, 'winLeg': 40,
                'darts': 100, 'score': 5000,
                'ton00': 5, 'ton40': 2, 'ton80': 1
            },
            'p2': {
                'rank': 2,
                'match': 10, 'winMatch': 8,
                'leg': 50, 'winLeg': 35
            },
            'p3': {
                'rank': 3,
                'match': 8, 'winMatch': 5,
                'leg': 40, 'winLeg': 20
            }
        }
        mock_response_stats.json.return_value = stats_data
        mock_response_stats.raise_for_status.return_value = None

        # Configure side_effect for post to return different responses based on params or order
        # The order in run() is:
        # 1. get_data (entry_url)
        # 2. get_entry_list (entry_url)
        # 3. stats_list (stats_url)
        
        mock_session.post.side_effect = [
            mock_response_meta,
            mock_response_entry,
            mock_response_stats
        ]

        # Run scraper
        success, message = self.scraper.run()

        # Assertions
        self.assertTrue(success, f"Scraper failed: {message}")
        
        # Verify Champion created
        champions = Champion.objects.all()
        self.assertEqual(champions.count(), 1)
        
        champion = champions.first()
        self.assertEqual(champion.p1.first_name, "Roberto")
        self.assertEqual(champion.p1.last_name, "Wentz")
        
        # Verify 2nd and 3rd place
        self.assertIsNotNone(champion.p2)
        self.assertEqual(champion.p2.first_name, "Other") # From mock entry list
        
        # We need to ensure 'p3' is in the mock entry list for this to work perfectly, 
        # but the scraper uses the name from player_map.
        # Let's update the mock entry list in the test setup above to include p3.

