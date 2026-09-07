from django.core.management.base import BaseCommand

from obd.core.obdlib.webscraping.n01 import refresh_tournaments
from obd.core.views import _current_national_league_stage


class Command(BaseCommand):
    help = 'Recaptura todas as divisões da etapa atual da Liga Nacional (para agendamento)'

    def handle(self, *args, **options):
        stage_name, divisions = _current_national_league_stage()

        if not divisions:
            self.stdout.write(self.style.WARNING('Nenhuma etapa da Liga Nacional capturada ainda. Nada a fazer.'))
            return

        self.stdout.write(f'Atualizando "{stage_name}" ({len(divisions)} divisão(ões))...')
        updated, failed = refresh_tournaments(divisions)

        if updated:
            self.stdout.write(self.style.SUCCESS(f'{updated} divisão(ões) atualizada(s).'))
        for name, error in failed:
            self.stdout.write(self.style.ERROR(f'Falha em "{name}": {error}'))
