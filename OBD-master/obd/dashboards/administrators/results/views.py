import copy
import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from obd.dashboards.administrators.divisions.models import Division
from obd.dashboards.administrators.fixtures.models import Fixture
from obd.dashboards.administrators.leagues.models import League
from obd.dashboards.administrators.results.forms import ResultForm
from obd.dashboards.administrators.results.models import Result
from obd.dashboards.administrators.champions.models import Champion
from django.db.models import Avg, Sum, Count, Max, Min, Q, Value
from django.db.models.functions import Cast, Coalesce


import cloudinary
import cloudinary.uploader
import cloudinary.api


# Index View just to rout related method (POST or GET) to respective View (SUBMIT or VIEW)
from obd.dashboards.players.merits.models import Merit


@login_required()
def index(request, slug, match):
    if request.method == 'GET':
        return show(request, slug, match)
    else:
        return submit(request, slug=slug, match=match)


# View just to show the headers of the game/match
@login_required()
def show(request, slug, match):
    try:
        match = Fixture.objects.get(id=match)
    except Fixture.DoesNotExist:
        messages.success(request, f'A partida #{match} foi cancelada ou é inexistente.')
        return redirect('/dashboard/player/view/leagues')
    else:
        if not request.user in match.players.all():
            messages.success(request, f'A partida #{match} não faz parte de sua tabela de jogos. Verifique novamente')
            return redirect('/dashboard/player/view/leagues')
        else:
            if match.validation == 1 and match.enabled:
                u = User.objects.get(username=match.submited_by)
                messages.success(request,
                                 f'A partida #{match}  já foi registrada anteriormente por {u.first_name} {u.last_name} em {match.on_date}.')
                return redirect('/dashboard/player/view/leagues')
            else:
                pass

    division = Division.objects.get(slug=slug)
    form = ResultForm()
    html = {'validated': True, 'required': '', 'text_submit': 'Validar partida!', 'color_submit': 'btn-warning',
            'readonly_server': 'readonly', 'readonly_data': ''}
    return render(request, 'user_result_submit.html',
                  {'division': division, 'match': match, 'form': form, 'html': html})





# Post method to record data into tables: stats, fixture, results.
@login_required()
def submit(request, slug, match, alert='alert-success'):
    form = ResultForm(request.POST, request.FILES)
    division = Division.objects.get(slug=slug)
    league = League.objects.get(id=division.league.id)
    game = Fixture.objects.get(id=match)
    if not form.is_valid():
        html = {'validated': True, 'required': 'required', 'text_submit': 'Validar dados!',
                'color_submit': 'btn-warning'}
        alert = 'alert-danger'
        return render(request, 'user_result_submit.html',
                      {'division': division, 'match': game, 'form': form, 'alert': alert, 'html': html})

    pendding = Fixture.objects.filter(division=division, status=0).count()
    data = game.division.league.enviroment.retrieve()
    bonus = int(division.league.enviroment.meritChampionBonus)
    result_p1 = game.result_set.first()
    p1 = result_p1.player
    result_p2 = game.result_set.last()
    p2 = result_p2.player
    merit_p1 = Merit()
    merit_p2 = Merit()

    # Updating Fixture Table related to Match/Game
    game.status = 1
    game.link = ''
    game.submited_by = request.user.username
    game.on_date = datetime.date.today()
    game.server = 'OTH'

    if form.cleaned_data['photo'] is not None:
        cloudinary_response = cloudinary.uploader.upload(form.cleaned_data['photo'],
                                                         public_id=f'boa/media/uploads/results/{game.division.league.id}/{game.division.id}/{game.id}',
                                                         height='800',
                                                         width='800',
                                                         crop='thumb')
        game.photo = cloudinary_response['url']

    score_1 = int(form.cleaned_data['legs_p1'])
    score_2 = int(form.cleaned_data['legs_p2'])


    # Update P1/P2 in Results regardless final status of the macth: WINNER, LOSER, DRAW.
    if score_1 == score_2:
        p1.stat.bcmPoints = p1.stat.bcmPoints + 1
        p1.stat.leaguePerformance = p1.stat.leaguePerformance[1:4] + 'D'
        result_p1.sets = 0
        result_p1.final = 2
        result_p1.points = game.division.league.enviroment.matchDrawPoints
        p2.stat.bcmPoints = p2.stat.bcmPoints + 1
        p2.stat.leaguePerformance = p2.stat.leaguePerformance[1:4] + 'D'
        result_p2.sets = 0
        result_p2.final = 2
        result_p2.points = game.division.league.enviroment.matchDrawPoints

        #New OBD Order of Merits Points Table

        merit_p1.player = p1
        merit_p1.match = game
        merit_p1.type = 1
        merit_p1.points = 1
        merit_p1.enabled = True

        merit_p2.player = p2
        merit_p2.match = game
        merit_p2.type = 1
        merit_p2.points = 1
        merit_p2.enabled = True

    else:
        if score_1 > score_2:
            p1.stat.bcmPoints = p1.stat.bcmPoints + data['meritpoints'][division.formation]
            p1.stat.leaguePerformance = p1.stat.leaguePerformance[1:4] + 'W'
            p1.stat.bcmWin = p1.stat.bcmWin + 1
            result_p1.sets = 1
            result_p1.final = 1
            result_p1.points = game.division.league.enviroment.matchWinPoints
            p2.stat.bcmPoints = p2.stat.bcmPoints + 1
            p2.stat.leaguePerformance = p2.stat.leaguePerformance[1:4] + 'L'
            result_p2.final = 0
            result_p2.sets = 0
            result_p2.points = 0

            # New OBD Order of Merits Points Table

            merit_p1.player = p1
            merit_p1.match = game
            merit_p1.type = 2
            merit_p1.points = data['meritpoints'][division.formation]
            merit_p1.enabled = True

            merit_p2.player = p2
            merit_p2.match = game
            merit_p2.type = 0
            merit_p2.points = 1
            merit_p2.enabled = True

        else:
            p1.stat.bcmPoints = p1.stat.bcmPoints + 1
            p1.stat.leaguePerformance = p1.stat.leaguePerformance[1:4] + 'L'
            result_p1.final = 0
            result_p1.sets = 0
            result_p1.points = 0
            p2.stat.bcmPoints = p2.stat.bcmPoints + data['meritpoints'][division.formation]
            p2.stat.leaguePerformance = p2.stat.leaguePerformance[1:4] + 'W'
            p2.stat.bcmWin = p2.stat.bcmWin + 1
            result_p2.final = 1
            result_p2.sets = 1
            result_p2.points = game.division.league.enviroment.matchWinPoints


            merit_p1.player = p1
            merit_p1.match = game
            merit_p1.type = 0
            merit_p1.points = 1
            merit_p1.enabled = True

            merit_p2.player = p2
            merit_p2.match = game
            merit_p2.type = 2
            merit_p2.points = data['meritpoints'][division.formation]
            merit_p2.enabled = True


    if (game.server == 'N01') or (game.server == 'LID'):
        game.validation = 1
        result_p1.validation = 1
        result_p2.validation = 1
        game.comment = 'AUTO INSERT'
        # game.save()

    # Updating P1 Stat
    if p1.stat.bcmAvg == 0:
        p1.stat.bcmAvg = round(form.cleaned_data['average_p1'], 2)  # Rounding up 2 decimals values.
    else:
        p1.stat.bcmAvg = round(((p1.stat.bcmAvg + form.cleaned_data['average_p1']) / 2), 2)

    if p1.stat.best3da < p1.stat.bcmAvg:
        p1.stat.best3da = round(p1.stat.bcmAvg, 2)

    p1.stat.bcmMatches = p1.stat.bcmMatches + 1
    p1.stat.bcmTon = p1.stat.bcmTon + form.cleaned_data['ton_p1']
    p1.stat.bcmTon40 = p1.stat.bcmTon40 + form.cleaned_data['ton40_p1']
    p1.stat.bcmTon70 = p1.stat.bcmTon70 + form.cleaned_data['ton70_p1']
    p1.stat.bcmTon80 = p1.stat.bcmTon80 + form.cleaned_data['ton80_p1']

    if p1.stat.bcmLeg == 0:
        p1.stat.bcmLeg = form.cleaned_data['best_leg_p1']
    else:
        if p1.stat.bcmLeg > form.cleaned_data['best_leg_p1']:
            p1.stat.bcmLeg = form.cleaned_data['best_leg_p1']

    if p1.stat.bcmOut < form.cleaned_data['highest_out_p1']:
        p1.stat.bcmOut = form.cleaned_data['highest_out_p1']

    p1.stat.leagueParticipation = p1.stat.leagueParticipation + 1

    # Updating P2 Stat
    if p2.stat.bcmAvg == 0:
        p2.stat.bcmAvg = round(form.cleaned_data['average_p2'], 2)
    else:
        p2.stat.bcmAvg = round(((p2.stat.bcmAvg + form.cleaned_data['average_p2']) / 2), 2)

    if p2.stat.best3da < p2.stat.bcmAvg:
        p2.stat.best3da = round(p2.stat.bcmAvg, 2)

    p2.stat.bcmMatches = p2.stat.bcmMatches + 1
    p2.stat.bcmTon = p2.stat.bcmTon + form.cleaned_data['ton_p2']
    p2.stat.bcmTon40 = p2.stat.bcmTon40 + form.cleaned_data['ton40_p2']
    p2.stat.bcmTon70 = p2.stat.bcmTon70 + form.cleaned_data['ton70_p2']
    p2.stat.bcmTon80 = p2.stat.bcmTon80 + form.cleaned_data['ton80_p2']

    if p2.stat.bcmLeg == 0:
        p2.stat.bcmLeg = form.cleaned_data['best_leg_p2']
    else:
        if p2.stat.bcmLeg > form.cleaned_data['best_leg_p2']:
            p2.stat.bcmLeg = form.cleaned_data['best_leg_p2']

    if p2.stat.bcmOut < form.cleaned_data['highest_out_p2']:
        p2.stat.bcmOut = form.cleaned_data['highest_out_p2']

    p2.stat.leagueParticipation = p2.stat.leagueParticipation + 1

    # Creating Result table for P1
    result_p1.enabled = True
    result_p1.on_date = datetime.date.today()
    result_p1.legs = form.cleaned_data['legs_p1']
    result_p1.legs_diff = form.cleaned_data['legs_p1'] - form.cleaned_data['legs_p2']
    result_p1.highest_out = form.cleaned_data['highest_out_p1']
    result_p1.best_leg = form.cleaned_data['best_leg_p1']
    result_p1.ton = form.cleaned_data['ton_p1']
    result_p1.ton40 = form.cleaned_data['ton40_p1']
    result_p1.ton70 = form.cleaned_data['ton70_p1']
    result_p1.ton80 = form.cleaned_data['ton80_p1']
    result_p1.average = round(form.cleaned_data['average_p1'], 2)
    result_p1.comment = form.cleaned_data['comment']

    # Creating result table for P2
    result_p2.enabled = True
    result_p2.on_date = datetime.date.today()
    result_p2.legs = form.cleaned_data['legs_p2']
    result_p2.legs_diff = form.cleaned_data['legs_p2'] - form.cleaned_data['legs_p1']
    result_p2.highest_out = form.cleaned_data['highest_out_p2']
    result_p2.best_leg = form.cleaned_data['best_leg_p2']
    result_p2.ton = form.cleaned_data['ton_p2']
    result_p2.ton40 = form.cleaned_data['ton40_p2']
    result_p2.ton70 = form.cleaned_data['ton70_p2']
    result_p2.ton80 = form.cleaned_data['ton80_p2']
    result_p2.average = round(form.cleaned_data['average_p2'], 2)
    result_p2.comment = form.cleaned_data['comment']

    champion = Champion.objects.get(division=division)

    # if normal game and last only one game...
    if division.phase == 2 and pendding == 1:
        division.phase = 4

    #if playoffs game
    if division.phase == 3 and game.type == 4:
        result_p1.enabled = False
        result_p2.enabled = False
        if result_p1.final == 1:
            division.finals.add(result_p1.player)
            division.third.add(result_p2.player)

        if result_p2 == 1:
            division.finals.add(result_p2.player)
            division.third.add(result_p1.player)

        if (division.finals.all().count() == 2) and (division.third.all().count() == 2):
            division.phase = 6
            final = Fixture()
            final.division = division
            final.type = 2
            final.comment = 'Jogo Final'
            final.save()
            final.players.add(division.finals.first())
            final.players.add(division.finals.last())

            for player in final.players.all():
                result = Result()
                result.fixture = final
                result.player = player
                result.enabled = False
                result.save()

            third = Fixture()
            third.division = division
            third.type = 3
            third.save()
            third.players.add(division.third.first())
            third.players.add(division.third.last())
            third.comment = 'Disputa Terceiro Lugar'

            for player in third.players.all():
                result = Result()
                result.fixture = third
                result.player = player
                result.enabled = False
                result.save()

    #if final game
    if division.phase == 6 and game.type == 2:
        result_p1.enabled = False
        result_p2.enabled = False

        if result_p1 == 1:
            if division.winners.all().count() == 0:
                division.winners.add(result_p1.player)
                division.winners.add(result_p2.player)

                #Adding new champion table
                champion.p1 = result_p1.player
                champion.p2 = result_p2.player

            else:
                p3 = division.winners.first()
                p4 = division.winners.last()
                division.winners.remove(p3)
                division.winners.remove(p4)
                division.winners.add(result_p1.player)
                division.winners.add(result_p2.player)
                division.winners.add(p3)
                division.phase = 4

                # Adding new champion table
                champion.p1 = result_p1.player
                champion.p2 = result_p2.player
        else:
            if division.winners.all().count() == 0:
                division.winners.add(result_p2.player)
                division.winners.add(result_p1.player)

                # Adding new champion table
                champion.p1 = result_p2.player
                champion.p2 = result_p1.player

            else:
                p3 = division.winners.first()
                p4 = division.winners.last()
                division.winners.remove(p3)
                division.winners.remove(p4)
                division.winners.add(result_p2.player)
                division.winners.add(result_p1.player)
                division.winners.add(p3)
                division.phase = 4

                # Adding new champion table
                champion.p1 = result_p2.player
                champion.p2 = result_p1.player

    #if third game
    if division.phase == 6 and game.type == 3:
        result_p1.enabled = False
        result_p2.enabled = False
        if result_p1 == 1:
            if division.winners.all().count() == 0:
                division.winners.add(result_p1.player)
                division.winners.add(result_p2.player)

                # Adding new champion table
                champion.p3 = result_p1.player
                champion.p4 = result_p2.player

            else:
                division.winners.add(result_p1.player)
                division.winners.add(result_p2.player)
                division.phase = 4

                # Adding new champion table
                champion.p3 = result_p1.player
                champion.p4 = result_p2.player
        else:
            if division.winners.all().count() == 0:
                division.winners.add(result_p2.player)
                division.winners.add(result_p1.player)

                # Adding new champion table
                champion.p3 = result_p2.player
                champion.p4 = result_p1.player

            else:
                division.winners.add(result_p2.player)
                division.winners.add(result_p1.player)
                division.phase = 4

                # Adding new champion table
                champion.p3 = result_p2.player
                champion.p4 = result_p1.player

    # Saving P1 and P2 stats if SERVER is N01 ou LID (Dont need validation).
    if (game.server == 'N01') or (game.server == 'LID'):
        p1.stat.save()
        p2.stat.save()
        champion.save()
        merit_p1.save()
        merit_p2.save()

    result_p1.save()
    result_p2.save()
    division.save()
    link = f'/dashboard/public/result/{game.division.slug}/match/{game.id}/view'
    game.save()

    messages.success(request, f'Jogo #{game.id} registrado com sucesso!')
    return redirect(link)
    '''return render(request, 'user_result_submit.html',
              {'division': division, 'match': game, 'form': form, 'alert': alert})'''


@login_required()
def validate(request, match):
    # Get the respective match for P1 and P2 and check if exists


    try:
        game = Fixture.objects.get(id=match)
    except Fixture.DoesNotExist:
        messages.error(request, f'A partida #{match} não foi encontrada!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    # A set of "players" for further check "in"
    players = (player for player in game.players.all())

    # Get all the division enviroments
    data = game.division.league.enviroment.retrieve()

    p1 = game.result_set.first().player
    p2 = game.result_set.last().player
    result_p1 = game.result_set.first()
    result_p2 = game.result_set.last()
    merit_p1 = Merit()
    merit_p2 = Merit()

    if (request.user in players) and (request.user.username != game.submited_by) or (request.user.has_perm('has_admin_role')):
        game.status = 1
        game.validation = 1
        game.on_date = datetime.datetime.today()
        result_p1.validation = 1
        result_p1.enabled = True
        result_p1.comment = 'Validado por ' + request.user.username + '.'
        result_p1.on_date = datetime.datetime.today()
        result_p2.validation = 1
        result_p2.on_date = datetime.datetime.today()
        result_p2.enabled = True
        result_p2.comment = 'Validado por ' + request.user.username + '.'

         # Update P1/P2 in Results regardless final status of the macth: WINNER, LOSER, DRAW.
        if result_p1.legs == result_p2.legs:
            p1.stat.bcmPoints = p1.stat.bcmPoints + 1
            p1.stat.leaguePerformance = p1.stat.leaguePerformance[1:4] + 'D'
            result_p1.final = 2
            result_p1.sets = 0
            result_p1.points = game.division.league.enviroment.matchDrawPoints
            p2.stat.bcmPoints = p2.stat.bcmPoints + 1
            p2.stat.leaguePerformance = p2.stat.leaguePerformance[1:4] + 'D'
            result_p2.final = 2
            result_p2.sets = 0
            result_p2.points = game.division.league.enviroment.matchDrawPoints

            merit_p1.player = p1
            merit_p1.match = game
            merit_p1.type = 1
            merit_p1.points = 1
            merit_p1.enabled = True

            merit_p2.player = p2
            merit_p2.match = game
            merit_p2.type = 1
            merit_p2.points = 1
            merit_p2.enabled = True


        else:
            if result_p1.legs > result_p2.legs:
                p1.stat.bcmPoints = p1.stat.bcmPoints + data['meritpoints'][game.division.formation]
                p1.stat.leaguePerformance = p1.stat.leaguePerformance[1:4] + 'W'
                p1.stat.bcmWin = p1.stat.bcmWin + 1
                result_p1.final = 1
                result_p1.sets = 1
                result_p1.points = game.division.league.enviroment.matchWinPoints
                p2.stat.bcmPoints = p2.stat.bcmPoints + 1
                p2.stat.leaguePerformance = p2.stat.leaguePerformance[1:4] + 'L'
                result_p2.final = 0
                result_p2.sets = 0
                result_p2.points = 0

                merit_p1.player = p1
                merit_p1.match = game
                merit_p1.type = 2
                merit_p1.points = data['meritpoints'][game.division.formation]
                merit_p1.enabled = True

                merit_p2.player = p2
                merit_p2.match = game
                merit_p2.type = 0
                merit_p2.points = 1
                merit_p2.enabled = True


            else:
                p1.stat.bcmPoints = p1.stat.bcmPoints + 1
                p1.stat.leaguePerformance = p1.stat.leaguePerformance[1:4] + 'L'
                result_p1.final = 0
                result_p1.points = 0
                result_p1.sets = 0
                p2.stat.bcmPoints = p2.stat.bcmPoints + data['meritpoints'][game.division.formation]
                p2.stat.leaguePerformance = p2.stat.leaguePerformance[1:4] + 'W'
                p2.stat.bcmWin = p2.stat.bcmWin + 1
                result_p2.final = 1
                result_p2.sets = 1
                result_p2.points = game.division.league.enviroment.matchWinPoints

                merit_p1.player = p1
                merit_p1.match = game
                merit_p1.type = 0
                merit_p1.points = 1
                merit_p1.enabled = True

                merit_p2.player = p2
                merit_p2.match = game
                merit_p2.type = 2
                merit_p2.points = data['meritpoints'][game.division.formation]
                merit_p2.enabled = True


        # Updating P1 Stat
        if p1.stat.bcmAvg == 0:
            p1.stat.bcmAvg = round(result_p1.average, 2)  # Rounding up 2 decimals values.
        else:
            p1.stat.bcmAvg = round(((p1.stat.bcmAvg + result_p1.average) / 2), 2)

        if p1.stat.best3da < p1.stat.bcmAvg:
            p1.stat.best3da = round(p1.stat.bcmAvg, 2)

        p1.stat.bcmMatches = p1.stat.bcmMatches + 1
        p1.stat.bcmTon = p1.stat.bcmTon + result_p1.ton
        p1.stat.bcmTon40 = p1.stat.bcmTon40 + result_p1.ton40
        p1.stat.bcmTon70 = p1.stat.bcmTon70 + result_p1.ton70
        p1.stat.bcmTon80 = p1.stat.bcmTon80 + result_p1.ton80

        if p1.stat.bcmLeg == 0:
            p1.stat.bcmLeg = result_p1.best_leg
        else:
            if p1.stat.bcmLeg > result_p1.best_leg:
                p1.stat.bcmLeg = result_p1.best_leg

        if p1.stat.bcmOut < result_p1.highest_out:
            p1.stat.bcmOut = result_p1.highest_out

        p1.stat.leagueParticipation = p1.stat.leagueParticipation + 1

        # Updating P2 Stat
        if p2.stat.bcmAvg == 0:
            p2.stat.bcmAvg = round(result_p2.average, 2)
        else:
            p2.stat.bcmAvg = round(((p2.stat.bcmAvg + result_p2.average) / 2), 2)

        if p2.stat.best3da < p2.stat.bcmAvg:
            p2.stat.best3da = round(p2.stat.bcmAvg, 2)

        p2.stat.bcmMatches = p2.stat.bcmMatches + 1
        p2.stat.bcmTon = p2.stat.bcmTon + result_p2.ton
        p2.stat.bcmTon40 = p2.stat.bcmTon40 + result_p2.ton40
        p2.stat.bcmTon70 = p2.stat.bcmTon70 + result_p2.ton70
        p2.stat.bcmTon80 = p2.stat.bcmTon80 + result_p2.ton80

        if p2.stat.bcmLeg == 0:
            p2.stat.bcmLeg = result_p2.best_leg
        else:
            if p2.stat.bcmLeg > result_p2.best_leg:
                p2.stat.bcmLeg = result_p2.best_leg

        if p2.stat.bcmOut < result_p2.highest_out:
            p2.stat.bcmOut = result_p2.highest_out

        p2.stat.leagueParticipation = p2.stat.leagueParticipation + 1

        p1.stat.save()
        p2.stat.save()
        result_p1.save()
        result_p2.save()
        merit_p1.save()
        merit_p2.save()
        link = f'/dashboard/public/result/{game.division.slug}/match/{game.id}/view'
        game.save()

        messages.success(request, f'Sua partida #{match} foi validada com sucesso!')
        #return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        return redirect(link)
    else:
        messages.error(request, f'Não foi possível autenticar a partida #{match} dentro de sua tabela de jogos!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required()
def invalidate(request, match):
    # Get the respective match for P1 and P2 and check if exists
    try:
        game = Fixture.objects.get(id=match)
    except Fixture.DoesNotExist:
        messages.error(request, f'A partida #{match} não foi encontrada!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    # Prevent invalidate after validated.
    if game.validation == 1:
        messages.error(request, f'A partida #{match} já foi validada previamente.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    result_p1 = game.result_set.first()
    result_p2 = game.result_set.last()

    # Reset GAME values
    game.status = 0
    game.photo = 'https://res.cloudinary.com/hvnnhpdtd/image/upload/v1625926909/logo_black_gold_boa_2.png'
    game.submited_by = ''
    game.on_date = None
    game.link = ''
    game.server = 'OTH'
    game.validation = 2
    game.enabled = True
    game.comment = ''
    game.save()

    # Reset P1 data
    result_p1.validation = 0
    result_p1.enabled = False
    result_p1.on_date = None
    result_p1.final = 4
    result_p1.points = 0
    result_p1.sets = 0
    result_p1.legs = 0
    result_p1.legs_diff = 0
    result_p1.highest_out = 0
    result_p1.best_leg = 0
    result_p1.ton = 0
    result_p1.ton40 = 0
    result_p1.ton70 = 0
    result_p1.ton80 = 0
    result_p1.average = 0
    result_p1.darts9 = 0
    result_p1.darts3 = 0
    result_p1.comment = ''
    result_p1.save()

    # Reset P2 data
    result_p2.validation = 0
    result_p2.enabled = False
    result_p2.on_date = None
    result_p2.final = 4
    result_p2.points = 0
    result_p2.sets = 0
    result_p2.legs = 0
    result_p2.legs_diff = 0
    result_p2.highest_out = 0
    result_p2.best_leg = 0
    result_p2.ton = 0
    result_p2.ton40 = 0
    result_p2.ton70 = 0
    result_p2.ton80 = 0
    result_p2.average = 0
    result_p2.darts9 = 0
    result_p2.darts3 = 0
    result_p2.comment = ''
    result_p2.save()

    messages.success(request, f'Sua partida #{match} foi invalidada com sucesso!')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required()
def ranking(request, slug):
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
        walkover=walkover,
        points=points,
        difference=difference,
        legs=legs,
        wins=wins,
        losses=losses,
        draws=draws,
        average=avg,
        best=best,
        out=out,
        ton=ton,
        ton40=ton40,
        ton70=ton70,
        ton80=ton80,
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

    return render(request, 'user_ranking_show.html', response)


@login_required()
@permission_required('profiles.has_admin_role', raise_exception=True)
def ranking_by_admin(request, slug):
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
        walkover=walkover,
        difference=difference,
        legs=legs,
        wins=wins,
        losses=losses,
        draws=draws,
        average=avg,
        best=best,
        out=out,
        ton=ton,
        ton40=ton40,
        ton70=ton70,
        ton80=ton80,
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

    return render(request, 'admin_ranking_show.html', response)


@login_required()
@permission_required('profiles.has_admin_role', raise_exception=True)
def playoffs(request, division, game, result_p1, result_p2):
    if division.phase == 3 and game.type == 4:
        if result_p1.final == 1:
            game.division.finals.add(result_p1.player)
            game.division.third.add(result_p2.player)

        if result_p2 == 1:
            game.division.finals.add(result_p2.player)
            game.division.third.add(result_p1.player)

        if (division.finals.all().count() == 2) and (division.third.all().count() == 2):
            final = Fixture()
            final.division = division
            final.type = 2
            final.players.add(division.finals.first())
            final.players.add(division.finals.last())
            final.comment = 'Jogo Final'
            final.save()

            for player in final.players.all():
                result = Result()
                result.fixture = final
                result.player = player
                result.enabled = False
                result.save()

            third = Fixture()
            third.division = division
            third.type = 3
            third.players.add(division.third.first())
            third.players.add(division.third.last())
            third.comment = 'Disputa Terceiro Lugar'
            third.save()

            for player in third.players.all():
                result = Result()
                result.fixture = third
                result.player = player
                result.enabled = False
                result.save()

            division.phase = 6
            division.save()

    #final game
    if division.phase == 6 and game.type == 2:
        if result_p1 == 1:
            if len(division.winners.all()) == 0:
                division.winners.add(result_p1.player)
                division.winners.add(result_p2.player)
            else:
                p3 = division.winners.first()
                p4 = division.winners.last()
                division.winners.remove(p3)
                division.winners.remove(p4)
                division.winners.add(result_p1.player)
                division.winners.add(result_p2.player)
                division.winners.add(p3)
                division.winners.add(p4)
                division.phase = 4
                division.save()
        else:
            if len(division.winners.all()) == 0:
                division.winners.add(result_p2.player)
                division.winners.add(result_p1.player)
            else:
                p3 = division.winners.first()
                p4 = division.winners.last()
                division.winners.remove(p3)
                division.winners.remove(p4)
                division.winners.add(result_p2.player)
                division.winners.add(result_p1.player)
                division.winners.add(p3)
                division.winners.add(p4)
                division.phase = 4
                division.save()

    #third game
    if division.phase == 6 and game.type == 3:
        if result_p1 == 1:
            if division.winners.all().count() == 0:
                division.winners.add(result_p1.player)
                division.winners.add(result_p2.player)
            else:
                division.winners.add(result_p1.player)
                division.winners.add(result_p2.player)
                division.phase = 4
                division.save()
        else:
            if division.winners.all().count() == 0:
                division.winners.add(result_p2.player)
                division.winners.add(result_p1.player)
            else:
                division.winners.add(result_p2.player)
                division.winners.add(result_p1.player)
                division.phase = 4
                division.save()

    return division, game, result_p1, result_p2
