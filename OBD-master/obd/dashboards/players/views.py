import datetime
import hashlib
import time
import io
from decouple import config
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.messages import get_messages
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from obd.core.obdlib.standardsession import ObdSession
from obd.dashboards.administrators.divisions.models import Division
from obd.dashboards.administrators.fixtures.models import Fixture
from obd.dashboards.administrators.leagues.models import League
from obd.dashboards.players.logins.forms import LoginUserForm, UpdateLoginForm, RecoveryPasswordForm
from obd.dashboards.players.stats.models import Stat
from obd.dashboards.administrators.results.models import Result
import pandas as pd


@login_required()
def dashboard(request):
    stat = Stat.objects.get(user=request.user)
    total = stat.divAwinner+stat.divBwinner+stat.divCwinner+stat.divDwinner+stat.divOtherswinner
    fullname = request.user.first_name+'-'+request.user.last_name

    labels = []
    data = []
    title = ''
    averages = Result.objects.filter(validation=1, player=request.user, average__gt=0).order_by('-on_date')[:10]
    totals = averages.count()
    if totals > 0:
        for label in range(totals):
            label = label + 1
            labels.append(f'Jogo {label}')

        for average in averages:
            data.append(float(average.average))

        data = list(reversed(data))
        min_data = min(data)
        max_data = max(data)
        avg = request.user.stat.bcmAvg
        title = f'Mín: {min_data}, Média: {avg}, Máx: {max_data}'

    context = {'total': total,
               'fullname': fullname,
               'labels': labels,
               'data': data,
               'title': title,
               'graph': totals}

    return render(request, 'dashuser.html', context)


def loginuser(request):
    if request.method == 'POST':
        form = LoginUserForm(request.POST)
        if not form.is_valid():
            token = ObdSession().startSession()
            return render(request, 'login.html', {'form': form, 'token': token})
        else:
            logout(request)
            user = authenticate(username=form.cleaned_data['username'].lower(), password=form.cleaned_data['password'])
            login(request, user)
            return HttpResponseRedirect('/dashboard/player/')
    else:
        boasession = ObdSession()
        token = boasession.startSession()
        return render(request, 'login.html', {'form': LoginUserForm(), 'token': token})


def logoutuser(request):
    if not get_messages(request):
        name = str(request.user.first_name).capitalize()
        messages.success(request, f'Até mais, %s! Tenha um ótimo dia e bons treinos!' % name)
    logout(request)
    token = ObdSession().startSession()
    return render(request, 'login.html', {'form': LoginUserForm(), 'token': token})


@login_required()
def signupleague(request, slug):
    player = request.user
    player_nakka = player.profile.nakka

    # Check if user already has an account on NAKKA. If not, no allowed subscribe for leagues.
    if (player_nakka == '' or player_nakka == 'Null'):
        messages.success(request, f'Para se inscrever, primeiro informe seu apelido NAKKA em "Configurações do Perfil"')
        return userleagues(request, alert='alert-danger')
    else:
        # Get league instance and related formation DIV;
        league = League.objects.get(slug__iexact=slug)
        div = Division.objects.get(league=league, formation=0)

        # Add current logged player to DIV
        div.players.add(player)

        # If everything okay, set a success message and render user_open_leagues page.
        messages.success(request, f'Valeu, {request.user.first_name}! Você agora está inscrito em {league.name}!')
        return userleagues(request, alert='alert-success')


@login_required()
def signoffleague(request, slug):
    # Get the league division by SLUG div and logged player...
    division = Division.objects.get(slug__iexact=slug)
    player = request.user

    #Remove user from division/league
    division.players.remove(player)

    # If everything okay, set a success message and render user_open_leagues page.
    messages.success(request, f'Valeu, {request.user.first_name}! Você saiu da liga {division.league.name}!')
    return userleagues(request, alert='alert-danger')


@login_required()
def userleagues(request, alert=''):
    # List all tournaments that user is participating in (all phases)
    tournaments = Division.objects.filter(
        status=True, 
        players=request.user.id
    ).exclude(
        formation=0  # Exclude formation divisions
    ).order_by('-league__phase', 'league__start_date')

    return render(request, 'user_open_leagues.html', {'tournaments': tournaments, 'alert': alert})


@login_required()
def currentlogin(request):
    if request.method == 'POST':
        return updatelogin(request)
    else:
        return showcurrentlogin(request)



def recoverypassword(request):
    form = RecoveryPasswordForm(request.POST)
    if not form.is_valid():
        boasession = ObdSession()
        token = boasession.startSession()
        return render(request, 'login.html', {'form': form, 'token': token})

    u = User.objects.get(email=form.cleaned_data['email'])

    for x in range(5):
        key = hashlib.md5(str(time.time()).split('.')[1].encode('utf-8')).hexdigest()
        for y in range(5):
            force = hashlib.md5(str(time.time()).split('.')[1].encode('utf-8')).hexdigest()

    code = (force+key+config('RECOVERY_KEY')).encode('utf-8')
    code = hashlib.md5(code).hexdigest()[:11]

    context = {'code': code,
               'username': u.username,
               'first': u.first_name.capitalize(),
               'last': u.last_name.capitalize()}

    # Send E-Mail to new member with a CC List to OBD Org.
    _send_email('SOLICITAÇÃO DE RECUPERAÇÃO DE SENHA OBD',
                settings.DEFAULT_FROM_EMAIL,
                form.cleaned_data['email'],
                'recovery_password.txt',
                context)

    # Success feedback
    messages.success(request, f'Recebemos sua solicitação. Se o e-mail for válido, você receberá em minutos uma nova senha. Atualize a mesma após o login.')
    boasession = ObdSession()
    token = boasession.startSession()
    u.set_password(code)
    u.save()
    return render(request, 'login.html', {'token': token})


def _send_email(subject, from_, to, template_name, context):
    body = render_to_string(template_name, context)
    send_mail(subject, body, from_, [from_, to])


def updatelogin(request):
        form = UpdateLoginForm(request.POST)
        if not form.is_valid():
            return render(request, 'profile_update_passwd.html', {'form': form})
        else:
            updated = []
            auth_user = authenticate(username=form.cleaned_data['username'].lower(),
                                password=form.cleaned_data['password'])
            logged_user = request.user
            if logged_user == auth_user:
                if len(str(form.cleaned_data['username2']).strip()):
                    logged_user.username = form.cleaned_data['username2'].lower()
                    updated.append('Usuário')
                if len(str(form.cleaned_data['email2']).strip()):
                    logged_user.email = form.cleaned_data['email2']
                    updated.append('E-mail')
                if len(str(form.cleaned_data['password3']).strip()):
                    logged_user.set_password(form.cleaned_data['password3'])
                    updated.append('Senha')
                if len(updated):
                    logged_user.save()
                    # Success feedback
                    passwd = form.cleaned_data["password3"]
                    messages.success(request, f'Valeu, {request.user.first_name}! Você atualizou: {updated}')
                    return logoutuser(request)
                else:
                    name = request.user.first_name
                    messages.success(request, f'{name}, informe ao menos um campo para atualizar.')
                    return render(request, 'profile_update_passwd.html', {'form': form, 'alert': 'alert-danger'})

            else:
                name = request.user.first_name
                login_username = form.cleaned_data['username']
                messages.success(request, f'{name}, verifique se "{login_username}" é realmente o seu usuário.')
                return render(request, 'profile_update_passwd.html', {'form': form, 'alert': 'alert-danger'})



def showcurrentlogin(request):
    return render(request, 'profile_update_passwd.html',
                  {'form': UpdateLoginForm()})


@login_required()
@permission_required('profiles.has_admin_role', raise_exception=True)
def audit(request):
    results = list(Result.objects.filter(validation=1).values())

    for r in results:
        u = User.objects.get(id=r['player_id'])
        r['player_id'] = f'{u.first_name} {u.last_name} #{u.id}'
        if not r['on_date'] is None:
            r['on_date'] = r['on_date'].strftime("%m/%d/%Y, %H:%M:%S")
        if not r['created_at'] is None:
            r['created_at'] = r['created_at'].strftime("%m/%d/%Y, %H:%M:%S")
        f = Fixture.objects.get(id=r['fixture_id'])
        r.update([('Server', f.server), ('Link', f.link), ('League', f.division.league.name), ('Division', f.division.get_formation_display())])

    path = str(datetime.date.today())
    filename = f'OBD_BRASILONLINE_REPORT_AUDIT_{path}_BY_{request.user.profile.pin}.xlsx'
    buffer = io.BytesIO()
    try:
        df = pd.DataFrame(data=results)
        df.to_excel(buffer)
    except ValueError:
        pass

    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response


@login_required()
def player_audit(request):
    results = list(Result.objects.filter(player=request.user, validation=1).values())
    for r in results:
        u = User.objects.get(id=r['player_id'])
        r['player_id'] = f'{u.first_name} {u.last_name} #{u.id}'
        if not r['on_date'] is None:
            r['on_date'] = r['on_date'].strftime("%m/%d/%Y, %H:%M:%S")
        if not r['created_at'] is None:
            r['created_at'] = r['created_at'].strftime("%m/%d/%Y, %H:%M:%S")
        f = Fixture.objects.get(id=r['fixture_id'])
        r.update([('Server', f.server), ('Link', f.link), ('League', f.division.league.name), ('Division', f.division.get_formation_display())])

    path = str(datetime.date.today())
    filename = f'OBD_BRASILONLINE_REPORT_AUDIT_{path}_BY_{request.user.profile.pin}.xlsx'
    buffer = io.BytesIO()
    try:
        df = pd.DataFrame(data=results)
        df.to_excel(buffer)
    except ValueError:
        pass

    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response


def mygames(request):
    matches = Result.objects.filter(fixture__status=1, enabled=True, validation=1, player=request.user).all().order_by('-on_date')
    context = {'matches': matches}
    return render(request, 'user_all_games.html', context)

