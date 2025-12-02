from django.db.models.functions import Cast, Coalesce
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.db.models import Count, Avg, Sum, Q, Value
from django.shortcuts import render, redirect
from django.utils.text import slugify
from brasilonline.core.obdlib.standardsession import ObdSession
from brasilonline.core.obdlib.fixturing import Fixturing
from brasilonline.dashboards.administrators.divisions.models import Division
from brasilonline.dashboards.administrators.enviroments.models import Enviroment
from brasilonline.dashboards.administrators.leagues.forms import NewLeagueForm
from brasilonline.dashboards.administrators.leagues.models import League
from brasilonline.dashboards.administrators.results.models import Result
from brasilonline.dashboards.players.profiles.models import Profile
from brasilonline.dashboards.administrators.fixtures.models import Fixture
from brasilonline.dashboards.administrators.champions.models import Champion
from brasilonline.core.obdlib.fixturing import Fixturing
import datetime

from brasilonline.dashboards.players.stats.models import Stat


@login_required()
@permission_required('profiles.has_admin_role', raise_exception=True)
def index(request):
    if request.method == 'POST':
        return createnewleague(request)
    else:
        return createleaguepage(request)


@login_required()
@permission_required('profiles.has_admin_role', raise_exception=True)
def viewplayersonleague(request, slug):
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
    )

    divisions = list(divisions)
    averages = list(averages)
    database = zip(divisions, averages)

    context = {'league': league,
              'total_divs': range(10),
              'database': database}

    return render(request, 'admin_players_leagues.html', context)


@login_required()
@permission_required('profiles.has_admin_role', raise_exception=True)
def manageleagues(request, alert='alert-success'):
    opens = League.objects.filter(status=True, phase=0)
    formations = League.objects.filter(status=True, phase=1)
    starts = League.objects.filter(status=True, phase=2)
    playoffs = League.objects.filter(status=True, phase=3)
    ends = League.objects.filter(status=True, phase=4)
    finals = League.objects.filter(status=True, phase=6)
    inactives = League.objects.filter(status=False, phase=5)
    div = Division.objects.filter(league__status=True, league__phase__lt=2)
    return render(request, 'admin_adm_leagues.html', {'divisions': div,
                                                      'opens': opens,
                                                      'formations': formations,
                                                      'starts': starts,
                                                      'playoffs': playoffs,
                                                      'finals': finals,
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

    #At the moment, there's only one div "FORMATION" created.
    formation_division = Division.objects.get(league=league, formation=0)
    formation_players = formation_division.players.all()

    #Gathering the total of leagues to be created
    div_set = {player.stat.bcmDiv for player in formation_players}

    if formation_players.count() < league.enviroment.leagueMinPlayers:
        messages.success(request, f'A liga {league.name} não atingiu a quantidade mínima de {league.enviroment.leagueMinPlayers} jogadores para ser iniciada.')
        return manageleagues(request, alert='alert-danger')

    # Set of letters for each number league: A=1, B=2, ..., J=10
    label = '0ABCDEFGHIJ'
    for div in div_set:
        newdivision = Division()
        newdivision.league = league
        newdivision.name = f'Divisão {label[div]} {league.name}'
        newdivision.description = f'Divisão {label[div]} criada automaticamente por {request.user.first_name} {request.user.last_name}.'
        newdivision.slug = slugify(newdivision.name)
        newdivision.formation = div
        newdivision.status = True
        newdivision.phase = 2
        newdivision.save()
        champs = Champion()
        champs.league = league
        champs.division = newdivision
        champs.save()

    # Saving players on their new league division and remove them from formation league
    for player in formation_players:
        #Add players based on their bcmDiv status
        set_to_division = Division.objects.get(league=league, formation=player.stat.bcmDiv)
        set_to_division.players.add(player)

    #Remove old formation division.
    formation_division.delete()

    #Creating Fixtures for current divisions
    all_divisions = league.division_set.all()
    for division in all_divisions:
        members = division.players.all()
        sort = [member.id for member in members]
        config = Fixturing()
        config.oneround(sort)
        for dueto in config.matches:
            fixture = Fixture()
            fixture.division = division
            fixture.save()
            fixture.players.add(User.objects.get(id=dueto[0]))
            fixture.players.add(User.objects.get(id=dueto[1]))

            for player in fixture.players.all():
                result = Result()
                result.fixture = fixture
                result.player = player
                result.enabled = False
                result.validation = 4
                result.final = 4
                result.save()

    #Saving update on current league.
    league.save()
    messages.success(request, f'Agora é pra valer! Liga {league.name} iniciada!')
    return manageleagues(request, alert='alert-success')


@login_required()
@permission_required('profiles.has_admin_role', raise_exception=True)
def setplayoffs(request, slug):
    league = League.objects.get(slug=slug)
    enviroments = league.enviroment.retrieve()
    divisions = league.division_set.filter(phase=2)

    # Sort all divisions which have playoffs and define the top4 players.
    for division in divisions:

        pendding = Fixture.objects.filter(division=division, status=0).count()
        has_playoffs = enviroments['leagueplayoffs'][division.formation]

        if has_playoffs:
            if pendding == 0:
                results = Result.objects.filter(fixture__division=division, enabled=True, validation=1, average__gt=0)
                # Set the Q queries to build the ranking player data for division(slug).
                members = Count('created_at')
                points = Sum('points')
                difference = Sum('legs_diff')
                legs = Sum('legs')
                wins = Count('final', filter=Q(final=1))
                avg = Avg('average')

                ranking = results.values('player').annotate(
                    points=points,
                    difference=difference,
                    legs=legs,
                    wins=wins,
                    average=avg,
                    members=members
                ).order_by('-points', '-difference', '-legs', '-wins', '-average')

                # Getting P1 to P4
                p1 = User.objects.get(id=ranking[0]['player'])
                p2 = User.objects.get(id=ranking[1]['player'])
                p3 = User.objects.get(id=ranking[2]['player'])
                p4 = User.objects.get(id=ranking[3]['player'])

                #Adding players to playoffs group
                division.playoffs.add(p1)
                division.playoffs.add(p2)
                division.playoffs.add(p3)
                division.playoffs.add(p4)

                division.phase = 3
                division.save()

                #Creating game 1
                fixture_1 = Fixture()
                fixture_1.division = division
                fixture_1.type = 4
                fixture_1.comment = 'Game 01 - Playoffs.'
                fixture_1.save()
                fixture_1.players.add(p1)
                fixture_1.players.add(p4)

                for player in fixture_1.players.all():
                    result = Result()
                    result.fixture = fixture_1
                    result.player = player
                    result.save()

                # Creating game 2
                fixture_2 = Fixture()
                fixture_2.division = division
                fixture_2.type = 4
                fixture_2.comment = 'Game 02 - Playoffs.'
                fixture_2.save()
                fixture_2.players.add(p2)
                fixture_2.players.add(p3)

                for player in fixture_2.players.all():
                    result = Result()
                    result.fixture = fixture_2
                    result.player = player
                    result.save()
            else:
                messages.success(request, f'Ainda existe {pendding} jogos pendentes na divisão {division.name}')
                return manageleagues(request, alert='alert-danger')
        else:
            if pendding == 0:
                division.phase = 4
                division.save()

    league.phase = 3
    league.save()
    messages.success(request, f'Agora é tudo ou nada! Playoffs da liga {league.name} em andamento!')
    return manageleagues(request, alert='alert-success')


@login_required()
@permission_required('profiles.has_admin_role', raise_exception=True)
def finishleague(request, slug):
    league = League.objects.get(slug=slug)
    enviroments = league.enviroment.retrieve()

    bonus_1 = int(league.enviroment.meritChampionBonus)
    bonus_2 = int(league.enviroment.meritSecondBonus)
    bonus_3 = int(league.enviroment.meritThirdBonus)

    for division in league.division_set.all():
        if division.phase == 4:
            continue
        else:
            messages.success(request, f'Liga {league.name} não pode ser finalizada. A divisão {division.get_formation_display()} possui jogos pendentes.')
            return manageleagues(request, alert='alert-danger')

    for division in league.division_set.all():
        champs = Champion.objects.get(division=division)
        has_playoffs = enviroments['leagueplayoffs'][division.formation]
        if has_playoffs and (division.formation == 1):

            ply1 = champs.p1
            ply1.stat.bcmPoints = ply1.stat.bcmPoints + bonus_1
            ply1.stat.save()

            ply2 = champs.p2
            ply2.stat.bcmPoints = ply2.stat.bcmPoints + bonus_2
            ply2.stat.save()

            ply3 = champs.p3
            ply3.stat.bcmPoints = ply3.stat.bcmPoints + bonus_3
            ply3.stat.save()

        else:
            results = Result.objects.filter(fixture__division=division, enabled=True, validation=1, average__gt=0)
            # Set the Q queries to build the ranking player data for division(slug).
            members = Count('created_at')
            points = Sum('points')
            difference = Sum('legs_diff')
            legs = Sum('legs')
            wins = Count('final', filter=Q(final=1))
            avg = Avg('average')

            ranking = results.values('player').annotate(
                points=points,
                difference=difference,
                legs=legs,
                wins=wins,
                average=avg,
                members=members
            ).order_by('-points', '-difference', '-legs', '-wins', '-average')

            # Getting P1 to P4 and applying BCM champion bonus
            ply1 = User.objects.get(id=ranking[0]['player'])
            champs.p1 = ply1

            ply2 = User.objects.get(id=ranking[1]['player'])
            champs.p2 = ply2

            ply3 = User.objects.get(id=ranking[2]['player'])
            champs.p3 = ply3

            champs.save()

            #Calculating BONUS points for OBD MERITS RANKING
            if division.formation == 1:
                ply1.stat.bcmPoints = ply1.stat.bcmPoints + bonus_1
                ply2.stat.bcmPoints = ply2.stat.bcmPoints + bonus_2
                ply3.stat.bcmPoints = ply3.stat.bcmPoints + bonus_3
                ply1.stat.save()
                ply2.stat.save()
                ply3.stat.save()

            division.save()

    players = User.objects.all()

    #Calculating PLayer CLASS based on AVG
    for player in players:
        avg = player.stat.bcmAvg
        p = league.enviroment.meritPmin
        a = league.enviroment.meritAmin
        b = league.enviroment.meritBmin
        c = league.enviroment.meritCmin
        d = league.enviroment.meritDmin
        r = league.enviroment.meritRmin

        if avg < d:
            player.stat.bcmClass = 99

        if avg > d and avg < c:
            player.stat.bcmClass = 5

        if avg > c and avg < b:
            player.stat.bcmClass = 4

        if avg > b and avg < a:
            player.stat.bcmClass = 3

        if avg > a and avg < p:
            player.stat.bcmClass = 2

        if avg > p:
            player.stat.bcmClass = 1

        player.stat.save()


    league.phase = 4
    league.save()
    messages.success(request, f'Liga {league.name} finalizada com sucesso. Parabéns aos campeões e até a próxima!')
    return manageleagues(request, alert='alert-success')


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
def setdivision(request, slug, pin, bcmDiv):
    player = Profile.objects.get(pin=pin)
    player.user.stat.bcmDiv = bcmDiv
    player.user.stat.save()
    return redirect(f'/dashboard/admin/league/{slug}/players', alert='alert-success')


@login_required()
@permission_required('profiles.has_admin_role', raise_exception=True)
def createnewleague(request):
    form = NewLeagueForm(request.POST)
    if not form.is_valid():
        return render(request, 'create_league.html', {'form': form})

    #Create new League if form is okay/clean
    enviroment = Enviroment.objects.first()
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
    formation.phase = 1
    formation.name = 'Divisão de Formação ' + league.name
    formation.description = 'Divisão criada automáticamente para cadastro de novos inscritos.'
    formation.slug = slugify(formation.name)
    formation.formation = 0
    formation.status = True
    formation.save()

    messages.success(request, f'Liga {league.name} cadastrada com sucesso! Clique aqui para exibir os detalhes')
    slug = league.slug
    token = ObdSession().startSession()
    return render(request, 'create_league.html', {'form': form, 'token': token, 'link': slug, 'alert': 'alert-success'})


@login_required()
@permission_required('profiles.has_admin_role', raise_exception=True)
def createleaguepage(request):
    form = NewLeagueForm()
    token = ObdSession().startSession()
    env = Enviroment.objects.first()
    return render(request, 'create_league.html', {'form': form, 'token': token, 'enviroment': env})

@login_required()
@permission_required('profiles.has_admin_role', raise_exception=True)
def walkover(request, match, win, los):

    game = Fixture.objects.get(id=match)
    rules = game.division.league.enviroment
    division = game.division

    game.status = 1
    game.submited_by = f'{request.user.first_name} {request.user.last_name}'
    game.on_date = datetime.datetime.today()
    game.server = 'WO'
    game.enabled = True
    game.comment = 'Aplicado WO'
    game.validation = 1
    game.save()

    winner = User.objects.get(id=win)
    loser = User.objects.get(id=los)

    winner_result = Result.objects.get(fixture=game, player=win)
    winner_result.validation = 1
    winner_result.enabled = True
    winner_result.on_date = datetime.datetime.today()
    winner_result.final = 1
    winner_result.walkover = False
    winner_result.points = game.division.league.enviroment.matchWinPoints
    winner_result.sets = 1
    winner_result.legs = rules.retrieve()['leaguefirstto'][game.division.formation]
    winner_result.legs_diff = 1
    winner_result.average = winner.stat.bcmAvg
    winner_result.comment = 'Resultado por WO'
    winner_result.save()

    loser_result = Result.objects.get(fixture=game, player=los)
    loser_result.validation = 1
    loser_result.enabled = True
    loser_result.on_date = datetime.datetime.today()
    loser_result.final = 0
    loser_result.points = 0
    loser_result.sets = 0
    loser_result.legs = 0
    loser_result.walkover = True
    loser_result.legs_diff = -(rules.retrieve()['leaguefirstto'][game.division.formation])
    loser_result.average = loser.stat.bcmAvg
    loser_result.comment = 'Resultado por WO'
    loser_result.save()

    loser_walkover = Result.objects.filter(fixture__division=division, player=los, walkover=True).count()
    if loser_walkover > rules.allowAutoBye:
        loser_fixtures = Fixture.objects.filter(division=game.division, players=loser)

        for wo in loser_fixtures.all():

            wo.status = 1
            wo.submited_by = f'{request.user.first_name} {request.user.last_name}'
            wo.on_date = datetime.datetime.today()
            wo.server = 'WO'
            wo.enabled = True
            wo.comment = 'Aplicado WO'
            wo.validation = 1

            if wo.result_set.first().player == loser:
                result = wo.result_set.first()

                if result.walkover:
                    continue
                else:
                    result.validation = 1
                    result.enabled = True
                    result.on_date = datetime.datetime.today()
                    result.final = 0
                    result.points = 0
                    result.sets = 0
                    result.legs = 0
                    result.walkover = True
                    result.legs_diff = -(rules.retrieve()['leaguefirstto'][game.division.formation])
                    result.average = loser.stat.bcmAvg
                    result.comment = 'Resultado por WO'
                    result.save()

                    result = wo.result_set.last()
                    if not result.walkover:
                        result.validation = 1
                        result.enabled = True
                        result.walkover = False
                        result.on_date = datetime.datetime.today()
                        result.final = 1
                        result.points = game.division.league.enviroment.matchWinPoints
                        result.sets = 1
                        result.legs = rules.retrieve()['leaguefirstto'][game.division.formation]
                        result.legs_diff = 1
                        result.average = winner.stat.bcmAvg
                        result.comment = 'Resultado por WO'
                        result.save()

                    wo.save()
            else:
                result = wo.result_set.last()

                if result.walkover:
                    continue
                else:
                    result.validation = 1
                    result.enabled = True
                    result.on_date = datetime.datetime.today()
                    result.final = 0
                    result.points = 0
                    result.sets = 0
                    result.legs = 0
                    result.walkover = True
                    result.legs_diff = -(rules.retrieve()['leaguefirstto'][game.division.formation])
                    result.average = loser.stat.bcmAvg
                    result.comment = 'Resultado por WO'
                    result.save()

                    result = wo.result_set.first()
                    if not result.walkover:
                        result.validation = 1
                        result.enabled = True
                        result.on_date = datetime.datetime.today()
                        result.final = 1
                        result.points = game.division.league.enviroment.matchWinPoints
                        result.sets = 1
                        result.legs = rules.retrieve()['leaguefirstto'][game.division.formation]
                        result.walkover = False
                        result.legs_diff = 1
                        result.average = winner.stat.bcmAvg
                        result.comment = 'Resultado por WO'
                        result.save()

                    wo.save()

    messages.success(request, f'WO aplicado com sucesso para o jogador {loser.first_name} {loser.last_name}')
    return redirect(f'/dashboard/admin/results/{game.division.slug}/ranking/show/byadmin', {'alert': 'alert-danger'})

def orderofmerit(request):
    players = Stat.objects.all().order_by('-bcmPoints', '-bcmWin', '-bcmAvg', '-bcmTon80')
    divisions = Division.objects.filter(formation__gt=0).all().order_by('-league__created_at', 'formation')
    response = {'players': players,
                'divisions': divisions}
    return render(request, 'user_public_order_of_merit.html', response)


@login_required()
@permission_required('profiles.has_admin_role', raise_exception=True)
def draw(request, match):
    game = Fixture.objects.get(id=match)
    if game.validation == 1:
        messages.success(request, f'Não foi possível aplicar empate pois a partida #{match} já foi finalizada previamente.')
        return redirect(f'/dashboard/admin/results/{game.division.slug}/ranking/show/byadmin', {'alert': 'alert-danger'})
    else:
        rules = game.division.league.enviroment
        game.status = 1
        game.submited_by = f'{request.user.first_name} {request.user.last_name}'
        game.on_date = datetime.datetime.today()
        game.server = 'OTH'
        game.enabled = True
        game.comment = 'Aplicado empate técnico.'
        game.validation = 1

        result_p1 = game.result_set.first()
        result_p2 = game.result_set.last()

        result_p1.validation = 1
        result_p1.enabled = True
        result_p1.walkover = False
        result_p1.on_date = datetime.datetime.today()
        result_p1.final = 2
        result_p1.points = game.division.league.enviroment.matchDrawPoints
        result_p1.sets = 0
        result_p1.legs = rules.retrieve()['leaguefirstto'][game.division.formation] - 1
        result_p1.legs_diff = 0
        result_p1.average = result_p1.player.stat.bcmAvg
        result_p1.comment = 'Aplicado empate técnico.'

        result_p2.validation = 1
        result_p2.enabled = True
        result_p2.walkover = False
        result_p2.on_date = datetime.datetime.today()
        result_p2.final = 2
        result_p2.points = game.division.league.enviroment.matchDrawPoints
        result_p2.sets = 0
        result_p2.legs = rules.retrieve()['leaguefirstto'][game.division.formation] - 1
        result_p2.legs_diff = 0
        result_p2.average = result_p2.player.stat.bcmAvg
        result_p2.comment = 'Aplicado empate técnico.'

        result_p1.save()
        result_p2.save()
        game.save()

        messages.success(request, f'Empate técnico aplicado com sucesso para a partida #{match}')
        return redirect(f'/dashboard/admin/results/{game.division.slug}/ranking/show/byadmin', {'alert': 'alert-success'})

