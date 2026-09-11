from collections import OrderedDict

from django.shortcuts import render

from obd.core.tournament_categories import CATEGORIAS, OUTROS, adivinhar_categoria, chave_do_evento
from obd.dashboards.administrators.champions.models import Champion


def champions(request):
    # Importado aqui dentro para não criar dependência circular: o robô de captura,
    # em core/, já importa os utilitários de campeão.
    from obd.core.models import TournamentResult

    base = Champion.objects.select_related(
        'league', 'division', 'p1', 'p2', 'p3', 'p4'
    ).order_by('-league__start_date', 'league__name', 'division__formation')

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
        (slug, {'slug': slug, 'label': cfg['label'], 'icone': cfg['icone'], 'cor': cfg['cor'],
                'anos': OrderedDict(), 'total': 0, 'torneios': set()})
        for slug, cfg in CATEGORIAS.items()
    )

    def categoria_de(league):
        """O tipo gravado na própria liga.

        Guardar na liga, e não no torneio, é o que torna a classificação imune a
        renomeações: o robô reescreve o nome do torneio a cada captura, e a liga
        continua com o nome antigo. O palpite pelo nome só entra se o valor do banco
        for de uma categoria que não existe mais.
        """
        slug = getattr(league, 'category', None)
        if slug in grupos:
            return slug
        return adivinhar_categoria(league.name if league else '')

    # A consulta já vem ordenada por data decrescente e, dentro da mesma data, por nome
    # da liga — o que deixa as divisões de uma etapa lado a lado, na ordem A, B, C, D.
    # Então anos e etapas entram em ordem sem precisar reordenar depois.
    for champ in champs:
        nome_liga = champ.league.name if champ.league else ''
        grupo = grupos[categoria_de(champ.league)]
        ano = champ.league.start_date.year if champ.league and champ.league.start_date else None
        etapas = grupo['anos'].setdefault(ano, OrderedDict())
        etapas.setdefault(chave_do_evento(nome_liga), []).append(champ)
        grupo['total'] += 1
        # Na Liga Nacional cada divisão tem seu campeão, então um mesmo torneio rende
        # vários títulos. Guardar os dois números evita ler "títulos" como "torneios".
        grupo['torneios'].add(nome_liga)

    def em_blocos(anos):
        return [
            {'ano': ano, 'etapas': [{'nome': nome, 'campeoes': lista} for nome, lista in etapas.items()]}
            for ano, etapas in anos.items()
        ]

    def tem_divisoes(anos):
        """A categoria tem alguma etapa com mais de um campeão (ou seja, com divisões)?

        É o que decide o formato da grade: categorias com divisões mostram 4 cards por
        linha e quebram a linha a cada etapa, para uma etapa nunca dividir espaço com
        outra. As demais, com um campeão por torneio, seguem em grade normal.
        """
        return any(len(lista) > 1 for etapas in anos.values() for lista in etapas.values())

    categorias = [
        {**grupo,
         'torneios': len(grupo['torneios']),
         'por_etapa': tem_divisoes(grupo['anos']),
         'anos': em_blocos(grupo['anos'])}
        for slug, grupo in grupos.items()
        # As três categorias da OBD aparecem sempre, mesmo vazias, para a tela ter uma
        # estrutura previsível. "Outros" só aparece quando há algo nela.
        if slug != OUTROS or grupo['total']
    ]

    # Todas as categorias abrem fechadas: quem escolhe o que ver é o usuário. A contagem
    # no cabeçalho já mostra o que existe dentro de cada uma.

    response = {
        'categorias': categorias,
        'total_geral': sum(c['total'] for c in categorias),
        'available_years': available_years,
        'selected_year': selected_year,
    }

    return render(request, 'user_public_all_champs.html', response)
