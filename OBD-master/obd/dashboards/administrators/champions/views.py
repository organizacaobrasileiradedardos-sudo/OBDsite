import re
import unicodedata
from collections import OrderedDict

from django.shortcuts import render
from obd.dashboards.administrators.champions.models import Champion


def _sem_acento(texto):
    """Minúsculas e sem acento, para comparar nomes sem depender de como foram digitados."""
    decomposto = unicodedata.normalize('NFKD', texto or '')
    return ''.join(c for c in decomposto if not unicodedata.combining(c)).lower()


# As categorias do Hall dos Campeões. A ordem deste dicionário é a ordem em que elas
# aparecem na tela; `prioridade` define qual vence quando um nome casa com mais de um
# padrão — "liga nacional" e "circuito nacional" são mais específicas que "tour".
#
# A classificação sai do nome da liga porque é o único vínculo que o campeão tem com o
# torneio de origem. Não existe campo de tipo no banco.
CATEGORIAS_CAMPEOES = OrderedDict([
    ('liga-nacional', {
        'label': 'Liga Nacional OBD',
        'icone': 'bi-trophy-fill',
        'padrao': re.compile(r'liga\s+nacional'),
        'prioridade': 1,
    }),
    ('tour', {
        'label': 'Tour OBD',
        'icone': 'bi-globe2',
        'padrao': re.compile(r'\btour\b'),
        'prioridade': 3,
    }),
    ('circuito-nacional', {
        'label': 'Circuito Nacional OBD',
        'icone': 'bi-geo-alt-fill',
        'padrao': re.compile(r'circuito\s+nacional'),
        'prioridade': 2,
    }),
])

# Quem não casa com nenhum padrão cai aqui, para que nenhum campeão suma da tela.
# Esta categoria só aparece se tiver alguém dentro.
CATEGORIA_OUTROS = 'outros'
LABEL_OUTROS = 'Outros Torneios'


def categorizar_liga(nome_liga):
    """Devolve o identificador da categoria a que o nome da liga pertence."""
    texto = _sem_acento(nome_liga)
    ordenadas = sorted(CATEGORIAS_CAMPEOES.items(), key=lambda item: item[1]['prioridade'])
    for slug, cfg in ordenadas:
        if cfg['padrao'].search(texto):
            return slug
    return CATEGORIA_OUTROS


def champions(request):
    base = Champion.objects.select_related(
        'league', 'division', 'p1', 'p2', 'p3', 'p4'
    ).order_by('-league__start_date', 'league__name', 'division__formation')

    available_years = sorted(
        {c.league.start_date.year for c in base if c.league and c.league.start_date},
        reverse=True,
    )

    selected_year = request.GET.get('ano')
    champs = base.filter(league__start_date__year=selected_year) if selected_year else base

    grupos = OrderedDict(
        (slug, {'slug': slug, 'label': cfg['label'], 'icone': cfg['icone'], 'anos': OrderedDict(), 'total': 0})
        for slug, cfg in CATEGORIAS_CAMPEOES.items()
    )
    grupos[CATEGORIA_OUTROS] = {
        'slug': CATEGORIA_OUTROS,
        'label': LABEL_OUTROS,
        'icone': 'bi-star-fill',
        'anos': OrderedDict(),
        'total': 0,
    }

    # A consulta já vem ordenada por data decrescente, então os anos entram em ordem
    # dentro de cada categoria sem precisar reordenar depois.
    for champ in champs:
        grupo = grupos[categorizar_liga(champ.league.name if champ.league else '')]
        ano = champ.league.start_date.year if champ.league and champ.league.start_date else None
        grupo['anos'].setdefault(ano, []).append(champ)
        grupo['total'] += 1

    categorias = [
        {**grupo, 'anos': [{'ano': ano, 'campeoes': lista} for ano, lista in grupo['anos'].items()]}
        for slug, grupo in grupos.items()
        # As três categorias da OBD aparecem sempre, mesmo vazias, para a tela ter uma
        # estrutura previsível. "Outros" só aparece quando há algo nela.
        if slug != CATEGORIA_OUTROS or grupo['total']
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
