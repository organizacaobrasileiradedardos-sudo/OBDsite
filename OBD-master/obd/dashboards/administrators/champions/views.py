from django.shortcuts import render
from obd.dashboards.administrators.champions.models import Champion


def champions(request):
    champs = Champion.objects.select_related(
        'league', 'division', 'p1', 'p2', 'p3', 'p4'
    ).order_by('-league__start_date', 'league__name', 'division__formation')

    available_years = sorted(
        {c.league.start_date.year for c in champs if c.league and c.league.start_date},
        reverse=True,
    )

    selected_year = request.GET.get('ano')
    if selected_year:
        champs = champs.filter(league__start_date__year=selected_year)

    response = {
        'champions': champs,
        'available_years': available_years,
        'selected_year': selected_year,
    }

    return render(request, 'user_public_all_champs.html', response)