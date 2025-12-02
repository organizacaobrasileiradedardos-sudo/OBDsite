from django.shortcuts import render
from brasilonline.dashboards.administrators.champions.models import Champion


def champions(request):
    champs = Champion.objects.all().order_by('-created_at', 'league', 'division__formation')
    response = {'champions': champs}

    return render(request, 'user_public_all_champs.html', response)