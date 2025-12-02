from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.shortcuts import render
from brasilonline.dashboards.administrators.enviroments.models import Enviroment
from brasilonline.dashboards.administrators.fixtures.models import Fixture
from brasilonline.dashboards.administrators.leagues.models import League


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




