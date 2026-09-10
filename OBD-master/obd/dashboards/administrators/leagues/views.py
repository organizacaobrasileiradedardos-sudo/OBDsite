from django.shortcuts import render
from obd.dashboards.administrators.leagues.models import League
from decimal import Decimal
from obd.dashboards.administrators.leagues.models import OrderOfMeritEntry
from obd.dashboards.administrators.leagues.models import NationalRankingEntry

def orderofmerit(request):
    # Etapas que já tiveram alguma importação, em ordem cronológica
    etapas = League.objects.filter(
        order_of_merit_entries__isnull=False
    ).distinct().order_by('start_date')

    entries = OrderOfMeritEntry.objects.select_related('player', 'player__profile', 'league')

    player_data = {}
    for entry in entries:
        pid = entry.player_id
        if pid not in player_data:
            player_data[pid] = {
                'player': entry.player,
                'values_by_league': {},
                'total': Decimal('0'),
            }
        player_data[pid]['values_by_league'][entry.league_id] = entry.value
        player_data[pid]['total'] += entry.value

    ranking = []
    for data in player_data.values():
        values = [data['values_by_league'].get(etapa.id) for etapa in etapas]
        ranking.append({
            'player': data['player'],
            'values': values,
            'total': data['total'],
        })

    ranking.sort(key=lambda x: (-x['total'], x['player'].first_name.lower(), x['player'].last_name.lower()))

    # Calcula a posição considerando empates (ex: 1º, 2º, 2º, 4º)
    rank = 0
    prev_total = None
    for idx, row in enumerate(ranking, start=1):
        if row['total'] != prev_total:
            rank = idx
        row['position'] = rank
        prev_total = row['total']

    context = {
        'etapas': etapas,
        'ranking': ranking,
    }
    return render(request, 'user_public_order_of_merit.html', context)


NATIONAL_RANKING_BEST_OF = 8


def national_ranking(request):
    etapas = League.objects.filter(
        national_ranking_entries__isnull=False
    ).distinct().order_by('start_date')

    entries = NationalRankingEntry.objects.select_related('player', 'player__profile', 'league')

    player_data = {}
    for entry in entries:
        pid = entry.player_id
        if pid not in player_data:
            player_data[pid] = {
                'player': entry.player,
                'values_by_league': {},
            }
        player_data[pid]['values_by_league'][entry.league_id] = entry.points

    ranking = []
    for data in player_data.values():
        values_by_league = data['values_by_league']

        # A partir da 9ª participação, só os 8 maiores resultados contam no total.
        counted_league_ids = {
            league_id
            for league_id, _ in sorted(
                values_by_league.items(), key=lambda item: item[1], reverse=True
            )[:NATIONAL_RANKING_BEST_OF]
        }
        total = sum(
            points for league_id, points in values_by_league.items()
            if league_id in counted_league_ids
        )

        values = [
            {
                'value': values_by_league.get(etapa.id),
                'counted': etapa.id in counted_league_ids,
            }
            for etapa in etapas
        ]

        ranking.append({
            'player': data['player'],
            'values': values,
            'total': total,
        })

    ranking.sort(key=lambda x: (-x['total'], x['player'].first_name.lower(), x['player'].last_name.lower()))

    # Calcula a posição considerando empates (ex: 1º, 2º, 2º, 4º)
    rank = 0
    prev_total = None
    for idx, row in enumerate(ranking, start=1):
        if row['total'] != prev_total:
            rank = idx
        row['position'] = rank
        prev_total = row['total']

    context = {
        'etapas': etapas,
        'ranking': ranking,
    }
    return render(request, 'user_public_national_ranking.html', context)
