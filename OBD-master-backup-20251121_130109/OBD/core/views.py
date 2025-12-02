from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.db.models.functions import Cast, Coalesce
from brasilonline.dashboards.administrators.divisions.models import Division
from brasilonline.dashboards.administrators.fixtures.models import Fixture
from brasilonline.dashboards.administrators.leagues.models import League
from brasilonline.dashboards.administrators.results.models import Result
from django.db.models import Avg, Sum, Min, Count, Q, Max, F, Value

from brasilonline.dashboards.players.stats.models import Stat


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

    stats = Stat.objects.all()

    stats_out = stats.order_by('-bcmOut')[:5]
    stats_180 = stats.order_by('-bcmTon80')[:5]
    stats_avg = stats.order_by('-bcmAvg')[:5]

    matches = Fixture.objects.filter(status=1).order_by('-on_date')[:6]

    server = Fixture.objects.filter(status=1).values('server').aggregate(
        webcamdarts=Count('server', filter=Q(server='WED')),
        nakka=Count('server', filter=Q(server='N01')),
        manual=Count('server', filter=Q(server='OTH'))
    )

    members = User.objects.all().count()

    opens = int(League.objects.filter(status=True, phase=0).count())
    formations = int(League.objects.filter(status=True, phase=1).count())
    starts = int(League.objects.filter(status=True, phase=2).count())
    playoffs = int(League.objects.filter(status=True, phase=3).count())
    ends = int(League.objects.filter(status=True, phase=4).count())
    finals = int(League.objects.filter(status=True, phase=6).count())
    inactives = int(League.objects.filter(status=False, phase=5).count())

    total = opens + \
            formations + \
            starts + \
            playoffs + \
            ends + \
            finals + \
            inactives

    response = {'matches': matches,
                'boa': boa,
                'stats_out': stats_out,
                'stats_180': stats_180,
                'stats_avg': stats_avg,
                'server': server,
                'total': total,
                'members': members,
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
    results = Result.objects.filter(fixture__division__league=league, enabled=True, validation=1, walkover=False)

    matches = Count('created_at')
    completed = Count('created_at', filter=Q(status=1))
    validated = Count('created_at', filter=Q(status=1, validation=1))
    hold = Count('validation', filter=Q(status=1, validation=0))
    pending = Count('created_at', filter=Q(status=0, validation=0))
    avg = Coalesce(Avg('average', filter=Q(average__gt=0)), Value(0))

    divisions = fixtures.values('division').annotate(
        matches=matches,
        completed=completed,
        pending=pending,
        validated=validated,
        hold=hold
    ).order_by('-division')

    averages = results.values('fixture__division').annotate(
        avg=avg
    ).order_by('-fixture__division')

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
    results = Result.objects.filter(fixture__division=division, validation=1, enabled=True)
    finished = Fixture.objects.filter(division=division, validation=1).order_by('-on_date')
    pending = Fixture.objects.filter(division=division, validation=0).order_by('-on_date')
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

    indice = int(len(ranking))
    for line in range(indice):
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


def public_result(request, slug, match):

    division = Division.objects.get(slug=slug)
    game = Fixture.objects.get(id=match)
    p1 = game.result_set.first()
    p2 = game.result_set.last()

    response = {'division': division,
                'game': game,
                'p1': p1,
                'p2': p2}

    return render(request, 'user_public_match_result.html', response)

def public_audit(request):
    pass


# New views for Events, News, and Documents
from .models import Event, News, Document
from django.utils import timezone


def events_list(request):
    """Display upcoming and past events"""
    now = timezone.now()
    upcoming_events = Event.objects.filter(is_active=True, event_date__gte=now).order_by('event_date')
    past_events = Event.objects.filter(is_active=True, event_date__lt=now).order_by('-event_date')[:10]
    
    context = {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
    }
    return render(request, 'events.html', context)


def news_list(request):
    """Display news articles"""
    featured_news = News.objects.filter(is_active=True, is_featured=True).order_by('-published_date')[:3]
    all_news = News.objects.filter(is_active=True).order_by('-published_date')[:20]
    
    context = {
        'featured_news': featured_news,
        'all_news': all_news,
    }
    return render(request, 'news.html', context)


def documents_list(request):
    """Display official documents organized by category"""
    documents_by_category = {}
    categories = Document.CATEGORY_CHOICES
    
    for category_code, category_name in categories:
        docs = Document.objects.filter(category=category_code, is_active=True).order_by('-publish_date')
        if docs.exists():
            documents_by_category[category_name] = docs
    
    context = {
        'documents_by_category': documents_by_category,
    }
    return render(request, 'documents.html', context)