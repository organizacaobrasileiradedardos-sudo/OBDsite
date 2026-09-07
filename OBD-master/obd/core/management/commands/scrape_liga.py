from django.core.management.base import BaseCommand

from obd.core.obdlib.webscraping.n01 import refresh_tournaments
from obd.core.views import _current_national_league_stage


class Command(BaseCommand):
    help = 'Recaptura as divisões da etapa em andamento da Liga Nacional (para agendamento)'

    def handle(self, *args, **options):
        # Só faz sentido atualizar a etapa em disputa: as concluídas não mudam mais.
        stage_name, divisions = _current_national_league_stage()

        if not divisions:
            self.stdout.write(self.style.WARNING(
                'Nenhuma etapa da Liga Nacional em andamento. Nada a fazer.'
            ))
            return

        self.stdout.write(f'Atualizando "{stage_name}" ({len(divisions)} divisão(ões))...')
        updated, failed = refresh_tournaments(divisions)

        if updated:
            self.stdout.write(self.style.SUCCESS(f'{updated} divisão(ões) atualizada(s).'))
        for name, error in failed:
            self.stdout.write(self.style.ERROR(f'Falha em "{name}": {error}'))
