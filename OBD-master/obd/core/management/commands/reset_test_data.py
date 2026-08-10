from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from obd.core.models import TournamentResult, PlayerTournamentStat
from obd.dashboards.administrators.leagues.models import OrderOfMeritEntry, NationalRankingEntry
from obd.dashboards.administrators.champions.models import Champion


class Command(BaseCommand):
    help = 'Apaga todos os dados de teste (torneios, rankings, campeões e jogadores não-admin), mantendo apenas superusuários.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirma a execução (obrigatório, evita exclusão acidental).',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(self.style.ERROR(
                'Nada foi apagado. Rode novamente com --confirm para executar de verdade.'
            ))
            return

        self.stdout.write('Apagando PlayerTournamentStat...')
        self.stdout.write(str(PlayerTournamentStat.objects.all().delete()))

        self.stdout.write('Apagando TournamentResult...')
        self.stdout.write(str(TournamentResult.objects.all().delete()))

        self.stdout.write('Apagando OrderOfMeritEntry...')
        self.stdout.write(str(OrderOfMeritEntry.objects.all().delete()))

        self.stdout.write('Apagando NationalRankingEntry...')
        self.stdout.write(str(NationalRankingEntry.objects.all().delete()))

        self.stdout.write('Apagando Champion...')
        self.stdout.write(str(Champion.objects.all().delete()))

        self.stdout.write('Apagando Users (exceto superusuário)...')
        self.stdout.write(str(User.objects.filter(is_superuser=False).delete()))

        self.stdout.write(self.style.SUCCESS('--- Confirmação final ---'))
        self.stdout.write(f'TournamentResult: {TournamentResult.objects.count()}')
        self.stdout.write(f'PlayerTournamentStat: {PlayerTournamentStat.objects.count()}')
        self.stdout.write(f'OrderOfMeritEntry: {OrderOfMeritEntry.objects.count()}')
        self.stdout.write(f'NationalRankingEntry: {NationalRankingEntry.objects.count()}')
        self.stdout.write(f'Champion: {Champion.objects.count()}')
        self.stdout.write(f'Users restantes: {list(User.objects.values_list("username", flat=True))}')

        self.stdout.write(self.style.SUCCESS('Dados de teste apagados com sucesso!'))