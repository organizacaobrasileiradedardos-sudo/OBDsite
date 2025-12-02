from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.db.models.functions import Cast, Coalesce
from brasilonline.dashboards.administrators.divisions.models import Division
from brasilonline.dashboards.administrators.fixtures.models import Fixture
from brasilonline.dashboards.administrators.leagues.models import League
from brasilonline.dashboards.administrators.results.models import Result
from django.db.models import Avg, Sum, Min, Count, Q, Max, F, Value


def index(request):

    server = ('WED', 'N01', 'OTH',)
    games = Fixture.objects.filter(validation=1, server__in=server).count()

    matches = Count('enabled', filter=Q(validation=1))
    legs = Sum('legs', filter=Q(validation=1, walkover=False))
    avg = Avg('average', filter=Q(validation=1, average__gt=0))
    ton = Sum('ton', filter=Q(validation=1))
    ton40 = Sum('ton40', filter=Q(validation=1))
    ton70 = Sum('ton70', filter=Q(validation=1))
    ton80 = Sum('ton80', filter=Q(validation=1))
    total = Sum((F('ton') + F('ton40') + F('ton70') + F('ton80')))

    results = Result.objects.filter(enabled=True, walkover=False)

    boa = results.aggregate(
        matches=matches,
        legs=legs,
        ton=ton,
        ton40=ton40,
        ton70=ton70,
        ton80=ton80,
        average=avg,
    )

    players = results.values('player').annotate(
        average=avg,
        matches=matches,
        ton80=ton80
    )

    paverage = list(players.order_by('-average')[:5])
    pton80 = list(players.order_by('-ton80')[:5])
    ptotal = list(results.values('player').annotate(total=total).order_by('-total')[:5])

    database = [paverage, ptotal, pton80]

    for data in database:
        for line in data:
            u = User.objects.get(id=line['player'])
            line['player'] = u

    matches = Fixture.objects.filter(status=1).order_by('-on_date')[:6]

    server = Fixture.objects.filter(status=1).values('server').aggregate(
        webcamdarts=Count('server', filter=Q(server='WED')),
        nakka=Count('server', filter=Q(server='N01')),
        lidarts=Count('server', filter=Q(server='LID')),
        godartspro=Count('server', filter=Q(server='GOP')),
        dartconnect=Count('server', filter=Q(server='DAC')),
    )

    members = User.objects.all().count()

    opens = League.objects.filter(status=True, phase=0)
    formations = League.objects.filter(status=True, phase=1)
    starts = League.objects.filter(status=True, phase=2)
    playoffs = League.objects.filter(status=True, phase=3)
    ends = League.objects.filter(status=True, phase=4)
    finals = League.objects.filter(status=True, phase=6)
    inactives = League.objects.filter(status=False, phase=5)

    total = opens.count() + \
            formations.count() + \
            starts.count() + \
            playoffs.count() + \
            ends.count() + \
            finals.count() + \
            inactives.count()

    response = {'matches': matches,
                'boa': boa,
                'ptotal': ptotal,
                'pton80': pton80,
                'paverage': paverage,
                'server': server,
                'members': members,
                'total': total,
                'opens': opens,
                'formations': formations,
                'starts': starts,
                'playoffs': playoffs,
                'finals': finals,
                'ends': ends,
                'canceled': inactives,
                'games': games
                }

    return render(request, 'index.html', response)


def brdardos(request):
    brdardos = 'https://brdardos.mercadoshops.com.br/lista/jogos-salao-jogo-dardos/'
    link = brdardos + request.GET['brsearch']
    return redirect(link)


def public_players(request):
    players = User.objects.all().order_by('first_name', 'last_name')
    return render(request, 'user_public_players.html', {'players': players})

def public_leagues(request):
    leagues = League.objects.all().order_by('-created_at')
    return render(request, 'user_public_leagues.html', {'leagues': leagues})

def public_league_view(request, slug):
    league = League.objects.get(slug=slug)
    fixtures = Fixture.objects.filter(division__league=league)
    results = Result.objects.filter(fixture__division__league=league)

    matches = Count('created_at')
    completed = Count('created_at', filter=Q(status=1))
    validated = Count('created_at', filter=Q(status=1, validation=1))
    hold = Count('validation', filter=Q(status=1, validation=0))
    pending = Count('created_at', filter=Q(status=0, validation=0))
    avg = Avg('average', filter=Q(enabled=True, validation=1))

    divisions = fixtures.values('division').annotate(
        matches=matches,
        completed=completed,
        pending=pending,
        validated=validated,
        hold=hold
    ).order_by('-division')

    averages = results.values('fixture__division').annotate(
        avg=avg
    )

    divisions = list(divisions)
    averages = list(averages)
    database = zip(divisions, averages)

    context = {'league': league,
               'total_divs': range(10),
               'database': database}

    return render(request, 'user_public_players_leagues.html', context)

def public_division_view(request, slug):
    # Collecting all results for "division".
    division = Division.objects.get(slug=slug)
    results = Result.objects.filter(fixture__division=division, validation=1)
    finished = Fixture.objects.filter(division=division, validation=1)
    pending = Fixture.objects.filter(division=division, validation=0)
    playoffs = Fixture.objects.filter(division=division, type=4)
    finals = Fixture.objects.filter(division=division, type=2)

    # Set the Q queries to build the ranking player data for division(slug).
    points = Coalesce(Sum('points'), Value(0))
    difference = Coalesce(Sum('legs_diff'), Value(0))
    legs = Coalesce(Sum('legs'), Value(0))
    matches = Coalesce(Count('enabled'), Value(0))
    wins = Coalesce(Count('final', filter=Q(final=1)), Value(0))
    losses = Count('final', filter=Q(final=0))
    walkover = Count('walkover', filter=Q(walkover=True))
    draws = Count('final', filter=Q(final=2))
    avg = Coalesce(Avg('average', filter=Q(average__gt=0)), Value(0))
    best = Min('best_leg', filter=Q(best_leg__gt=0))
    out = Max('highest_out')
    ton = Sum('ton')
    ton40 = Sum('ton40')
    ton70 = Sum('ton70')
    ton80 = Sum('ton80')

    ranking = results.values('player').annotate(
        matches=matches,
        points=points,
        difference=difference,
        legs=legs,
        wins=wins,
        losses=losses,
        draws=draws,
        walkover=walkover,
        average=avg,
        best=best,
        out=out,
        ton=ton,
        ton40=ton40,
        ton70=ton70,
        ton80=ton80
    ).order_by('-points', '-difference', '-legs', '-wins', '-average')

    for line in range(len(ranking)):
        u = User.objects.get(id=ranking[line]['player'])
        ranking[line]['player'] = u

    database = list(ranking)

    response = {'database': database,
                'division': division,
                'finished': finished,
                'pending': pending,
                'playoffs': playoffs,
                'finals': finals}

    return render(request, 'user_public_ranking_show.html', response)



