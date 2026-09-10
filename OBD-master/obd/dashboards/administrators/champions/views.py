from collections import OrderedDict

from django.shortcuts import render

from obd.core.tournament_categories import CATEGORIAS, OUTROS, adivinhar_categoria
from obd.dashboards.administrators.champions.models import Champion


def champions(request):
    # Importado aqui dentro para não criar dependência circular: o robô de captura,
    # em core/, já importa os utilitários de campeão.
    from obd.core.models import TournamentResult

    base = Champion.objects.select_related(
        'league', 'division', 'p1', 'p2', 'p3', 'p4'
    ).order_by('-league__start_date', 'league__name', 'division__formation')

    # A liga criada a partir de uma captura leva exatamente o nome do torneio
    # (get_or_create_league), então é por aí que campeão e torneio se encontram.
    torneios = dict(TournamentResult.objects.values_list('name', 'category'))
    em_andamento = TournamentResult.objects.filter(in_progress=True).values_list('name', flat=True)

    # Etapa em disputa não tem campeão, só líder do momento.
    base = base.exclude(league__name__in=list(em_andamento))

    available_years = sorted(
        {c.league.start_date.year for c in base if c.league and c.league.start_date},
        reverse=True,
    )

    selected_year = request.GET.get('ano')
    champs = base.filter(league__start_date__year=selected_year) if selected_year else base

    grupos = OrderedDict(
        (slug, {'slug': slug, 'label': cfg['label'], 'icone': cfg['icone'],
                'anos': OrderedDict(), 'total': 0, 'torneios': set()})
        for slug, cfg in CATEGORIAS.items()
    )

    def categoria_de(nome_liga):
        """O tipo gravado no torneio. O palpite pelo nome é só uma rede de segurança
        para o caso de não existir torneio com aquele nome (ou de o valor no banco ser
        de uma categoria que não existe mais)."""
        slug = torneios.get(nome_liga)
        if slug in grupos:
            return slug
        return adivinhar_categoria(nome_liga)

    # A consulta já vem ordenada por data decrescente, então os anos entram em ordem
    # dentro de cada categoria sem precisar reordenar depois.
    for champ in champs:
        nome_liga = champ.league.name if champ.league else ''
        grupo = grupos[categoria_de(nome_liga)]
        ano = champ.league.start_date.year if champ.league and champ.league.start_date else None
        grupo['anos'].setdefault(ano, []).append(champ)
        grupo['total'] += 1
        # Na Liga Nacional cada divisão tem seu campeão, então um mesmo torneio rende
        # vários títulos. Guardar os dois números evita ler "títulos" como "torneios".
        grupo['torneios'].add(nome_liga)

    categorias = [
        {**grupo,
         'torneios': len(grupo['torneios']),
         'anos': [{'ano': ano, 'campeoes': lista} for ano, lista in grupo['anos'].items()]}
        for slug, grupo in grupos.items()
        # As três categorias da OBD aparecem sempre, mesmo vazias, para a tela ter uma
        # estrutura previsível. "Outros" só aparece quando há algo nela.
        if slug != OUTROS or grupo['total']
    ]

    # Deixa aberta a primeira categoria que tenha campeões, para a página não abrir
    # inteiramente fechada e parecer vazia.
    for categoria in categorias:
        categoria['aberta'] = False
    primeira = next((c for c in categorias if c['total']), None)
    if primeira:
        primeira['aberta'] = True

    response = {
        'categorias': categorias,
        'total_geral': sum(c['total'] for c in categorias),
        'available_years': available_years,
        'selected_year': selected_year,
    }

    return render(request, 'user_public_all_champs.html', response)
