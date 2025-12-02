from django.core.management.base import BaseCommand
from obd.core.obdlib.webscraping.n01 import N01TournamentScraper

class Command(BaseCommand):
    help = 'Captures tournament stats from N01 Darts'

    def add_arguments(self, parser):
        parser.add_argument('url', type=str, help='The URL of the N01 tournament stats page')

    def handle(self, *args, **options):
        url = options['url']
        self.stdout.write(f"Starting capture for {url}...")
        
        scraper = N01TournamentScraper(url)
        success, message = scraper.run()
        
        if success:
            self.stdout.write(self.style.SUCCESS(message))
        else:
            self.stdout.write(self.style.ERROR(f"Error: {message}"))
