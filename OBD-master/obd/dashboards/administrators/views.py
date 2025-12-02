from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from obd.core.models import TournamentResult
from obd.core.obdlib.webscraping.n01 import N01TournamentScraper
from obd.dashboards.administrators.enviroments.models import Enviroment
from obd.dashboards.administrators.fixtures.models import Fixture
from obd.dashboards.administrators.leagues.models import League


@login_required()
@permission_required('profiles.has_admin_role', raise_exception=True)
def dashboard(request):
    opens = League.objects.filter(status=True, phase=0)
    formations = League.objects.filter(status=True, phase=1)
    starts = League.objects.filter(status=True, phase=2)
    playoffs = League.objects.filter(status=True, phase=3)
    ends = League.objects.filter(status=True, phase=4)
    finals = League.objects.filter(status=True, phase=6)
    inactives = League.objects.filter(status=False, phase=5)
    pending = Fixture.objects.filter(status=1, validation=0)


    total = opens.count() + \
            formations.count() + \
            starts.count() + \
            playoffs.count() + \
            ends.count() + \
            finals.count() + \
            inactives.count()

    context = {'total': total,
               'opens': opens,
               'formations': formations,
               'starts': starts,
               'playoffs': playoffs,
               'finals': finals,
               'ends': ends,
               'canceled': inactives,
               'pending': pending}

    return render(request, 'dashadmin.html', context)

def members(request):
    players = User.objects.all()
    return render(request, 'admin_user_list.html', {'players': players})

def logoutAdm(request):
    pass


@login_required
@permission_required('profiles.has_admin_role', raise_exception=True)
def scraping_dashboard(request):
    tournaments = TournamentResult.objects.all().order_by('-created_at')
    return render(request, 'scraping_dashboard.html', {'tournaments': tournaments})


@login_required
@permission_required('profiles.has_admin_role', raise_exception=True)
def run_capture(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        if url:
            scraper = N01TournamentScraper(url)
            success, message = scraper.run()
            if success:
                messages.success(request, message)
            else:
                messages.error(request, f"Erro: {message}")
        else:
            messages.error(request, "URL não fornecida.")
    
    return redirect('administrators:scraping_dashboard')




