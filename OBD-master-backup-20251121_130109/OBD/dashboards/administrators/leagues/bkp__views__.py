from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from django.utils.text import slugify
from brasilonline.core.boalib.standardsession import BoaSession
from brasilonline.dashboards.administrators.divisions.models import Division
from brasilonline.dashboards.administrators.enviroments.models import Enviroment
from brasilonline.dashboards.administrators.leagues.forms import NewLeagueForm
from brasilonline.dashboards.administrators.leagues.models import League
from brasilonline.dashboards.players.profiles.models import Profile


@login_required()
@permission_required('profiles.has_admin_role', raise_exception=True)
def index(request):
    if request.method == 'POST':
        return createnewleague(request)
    else:
        return createleaguepage(request)

@login_required()
@permission_required('profiles.has_admin_role', raise_exception=True)
def manageleagues(request, alert='alert-success'):
    opens = League.objects.filter(status=True, phase=0)
    formations = League.objects.filter(status=True, phase=1)
    starts = League.objects.filter(status=True, phase=2)
    playoffs = League.objects.filter(status=True, phase=3)
    ends = League.objects.filter(status=True, phase=4)
    inactives = League.objects.filter(status=False, phase=5)
    div = Division.objects.filter(league__status=True, league__phase__lt=2)
    return render(request, 'admin_adm_leagues.html', {'divisions': div,
                                                      'opens': opens,
                                                      'formations': formations,
                                                      'starts': starts,
                                                      'playoffs': playoffs,
                                                      'ends': ends,
                                                      'inactives': inactives,
                                                      'alert': alert})


@login_required()
@permission_required('profiles.has_admin_role', raise_exception=True)
def setsubscription(request, slug):
    league = League.objects.get(slug=slug)
    league.phase = 0
    league.save()
    messages.success(request, f'Liga {league.name} agora com inscrições abertas!')
    return manageleagues(request, alert='alert-success')


@login_required()
@permission_required('profiles.has_admin_role', raise_exception=True)
def setformation(request, slug):
    league = League.objects.get(slug=slug)
    league.phase = 1
    league.save()
    messages.success(request, f'Liga {league.name} configurada para FORMAÇÃO com sucesso!')
    return manageleagues(request, alert='alert-success')


@login_required()
@permission_required('profiles.has_admin_role', raise_exception=True)
def startleague(request, slug):
    league = League.objects.get(slug=slug)
    league.phase = 2
    league.save()

    #At the moment, there's only one div "FORMATION" created.
    division = Division.objects.get(league=league)
    players = division.players.all()

    #Gathering the total of leagues to be created
    div_set = {player.stat.bcmDiv for player in players}

    # Set of letters for each number league: A=1, B=2, ..., J=10
    label = 'ABCDEFGHIJ'
    for div in div_set:
        division = Division()
        division.league = league
        division.name = f'Divisão {label[div]} {league.name}'
        division.description = f'Divisão {label[div]} criada automaticamente por {request.user.first_name} {request.user.last_name}.'
        division.slug = slugify(division.name)
        division.formation = div
        division.status = True
        division.save()

    # Saving players on their new league division and remove them from formation league
    for player in players:
        #Old formation division league = remove player & remove league
        olddiv = Division.objects.get(league=league, formation=0)
        olddiv.players.remove(player)

        #Add players based on their bcmDiv status
        newdiv = Division.objects.get(league=league, formation=player.stat.bcmDiv)
        newdiv.players.add(player)

    #Creating Fixtures


    #Remove old formation div.
    olddiv.delete()

    messages.success(request, f'Agora é pra valer! Liga {league.name} iniciada!')
    return manageleagues(request, alert='alert-success')


@login_required()
@permission_required('profiles.has_admin_role', raise_exception=True)
def setplayoffs(request, slug):
    league = League.objects.get(slug=slug)
    league.phase = 3
    league.save()
    messages.success(request, f'Agora é tudo ou nada! Playoffs da liga {league.name} formado!')
    return manageleagues(request, alert='alert-success')


@login_required()
@permission_required('profiles.has_admin_role', raise_exception=True)
def finishleague(request, slug):
    league = League.objects.get(slug=slug)
    league.phase = 4
    league.save()
    messages.success(request, f'Liga {league.name} finalizada com sucesso!')
    return manageleagues(request, alert='alert-danger')


@login_required()
@permission_required('profiles.has_admin_role', raise_exception=True)
def inactiveleague(request, slug):
    league = League.objects.get(slug=slug)
    league.status = False
    league.phase = 5
    league.save()
    messages.success(request, f'Liga {league.name} foi desabilitada!')
    return manageleagues(request, alert='alert-danger')


@login_required()
@permission_required('profiles.has_admin_role', raise_exception=True)
def deleteleague(request, slug):
    league = League.objects.get(slug=slug)
    league.delete()
    messages.success(request, f'Liga {league.name} excluída com sucesso!')
    return manageleagues(request, alert='alert-danger')


@login_required()
@permission_required('profiles.has_admin_role', raise_exception=True)
def viewplayersonleague(request, slug):
    league = League.objects.get(slug=slug)
    return render(request, 'admin_players_leagues.html', {'league': league, 'total_divs': range(10)})


@login_required()
@permission_required('profiles.has_admin_role', raise_exception=True)
def updateleague(request, slug):
    pass

@login_required()
@permission_required('profiles.has_admin_role', raise_exception=True)
def setdivision(request, slug, pin, bcmDiv):
    player = Profile.objects.get(pin=pin)
    player.user.stat.bcmDiv = bcmDiv
    player.user.stat.save()
    return redirect(f'/dashboard/admin/league/{slug}/players', alert='alert-success')

def createnewleague(request):
    form = NewLeagueForm(request.POST)
    if not form.is_valid():
        return render(request, 'create_league.html', {'form': form})

    #Create new League if form is okay/clean
    enviroment = Enviroment.objects.last()
    league = League()
    league.enviroment = enviroment
    league.created_by = request.user
    league.name = form.cleaned_data['name']
    league.description = form.cleaned_data['description']
    league.add_info = form.cleaned_data['add_info']
    league.slug = slugify(form.cleaned_data['name'])
    league.start_date = form.cleaned_data['start_date']
    league.end_date = form.cleaned_data['end_date']
    league.runoff = form.cleaned_data['runoff']
    league.phase = form.cleaned_data['phase']
    league.scope = form.cleaned_data['scope']
    league.status = True
    league.save()

    # Creating auto formation DIV for LEAGUE to be used as base for new participants
    formation = Division()
    formation.league = league
    formation.name = 'Divisão de Formação ' + league.name
    formation.description = 'Divisão criada automáticamente para cadastro de novos inscritos.'
    formation.slug = slugify(formation.name)
    formation.formation = 0
    formation.status = True
    formation.save()

    messages.success(request, f'Liga {league.name} cadastrada com sucesso! Clique aqui para exibir os detalhes')
    slug = league.slug
    token = BoaSession().startSession()
    return render(request, 'create_league.html', {'form': form, 'token': token, 'link': slug, 'alert': 'alert-success'})


def createleaguepage(request):
    form = NewLeagueForm()
    token = BoaSession().startSession()
    return render(request, 'create_league.html', {'form': form, 'token': token})
