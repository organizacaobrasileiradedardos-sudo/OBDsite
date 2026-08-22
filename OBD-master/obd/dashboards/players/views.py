import datetime
import io
import resend
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.messages import get_messages
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from obd.core.obdlib.standardsession import ObdSession
from obd.dashboards.administrators.divisions.models import Division
from obd.dashboards.administrators.fixtures.models import Fixture
from obd.dashboards.administrators.leagues.models import League
from obd.dashboards.players.logins.forms import LoginUserForm, UpdateLoginForm, RecoveryPasswordForm, SetNewPasswordForm
from obd.dashboards.players.stats.models import Stat
from obd.dashboards.administrators.results.models import Result
import pandas as pd


@login_required()
def dashboard(request):
    fullname = request.user.first_name + '-' + request.user.last_name

    # === Estatísticas de Torneios (PlayerTournamentStat) ===
    from django.db.models import Sum, Max, Min, Count, F
    from obd.core.models import PlayerTournamentStat

    t_stats = PlayerTournamentStat.objects.filter(player=request.user)
    tournament_summary = None

    has_played_liga_nacional = t_stats.filter(tournament__name__icontains='LIGA NACIONAL').exists()

    if t_stats.exists():
        agg = t_stats.aggregate(
            tournaments=Count('id'),
            matches_played=Sum('matches_played'),
            matches_won=Sum('matches_won'),
            legs_played=Sum('legs_played'),
            legs_won=Sum('legs_won'),
            legs_diff=Sum('legs_diff'),
            total_180=Sum('count_180'),
            total_140=Sum('count_140_plus'),
            total_100=Sum('count_100_plus'),
            total_100_finish=Sum('count_100_plus_finish'),
            best_avg=Max('average_3_dart'),
            highest_out=Max('high_finish'),
            most_180_single=Max('count_180'),
            best_rank=Min('rank'),
        )

        best_leg_qs = t_stats.filter(best_leg__gt=0).aggregate(best_leg=Min('best_leg'))

        win_rate = 0
        if agg['matches_played']:
            win_rate = round((agg['matches_won'] / agg['matches_played']) * 100, 1)

        career_avg = 0
        if agg['legs_played']:
            weighted = t_stats.aggregate(w=Sum(F('average_3_dart') * F('legs_played')))['w'] or 0
            career_avg = round(weighted / agg['legs_played'], 2)

        titles = t_stats.filter(rank=1).count()

        recent_form = t_stats.select_related('tournament').order_by('-tournament__date')[:3]

        tournament_summary = {
            **agg,
            'win_rate': win_rate,
            'career_avg': career_avg,
            'titles': titles,
            'best_leg': best_leg_qs['best_leg'],
            'recent_form': recent_form,
        }

    # QR Code Generation
    qr_code_base64 = None
    if request.user.profile.pin and request.user.first_name and request.user.last_name:
        try:
            import qrcode
            import base64
            from django.urls import reverse

            # Build the public profile URL
            profile_url = reverse('profiles:publicprofile', kwargs={
                'pin': request.user.profile.pin,
                'first': request.user.first_name,
                'last': request.user.last_name
            })
            full_url = request.build_absolute_uri(profile_url)

            # Generate QR Code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(full_url)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            # Save to BytesIO
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            qr_image = base64.b64encode(buffer.getvalue()).decode()
            qr_code_base64 = f"data:image/png;base64,{qr_image}"

        except Exception as e:
            print(f"Error generating QR code: {e}")
            qr_code_base64 = None

    context = {'fullname': fullname,
               'qr_code': qr_code_base64,
               'has_played_liga_nacional': has_played_liga_nacional,
               'tournament_summary': tournament_summary}

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
            return HttpResponseRedirect(reverse('players:dashboard'))
    else:
        boasession = ObdSession()
        token = boasession.startSession()
        return render(request, 'login.html', {'form': LoginUserForm(), 'token': token})


def logoutuser(request):
    if request.user.is_authenticated and not get_messages(request):
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

    email = form.cleaned_data['email']
    try:
        u = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        u = None

    # Só envia o e-mail se o cadastro existir, mas a mensagem exibida é sempre
    # a mesma (evita revelar se um e-mail está ou não cadastrado no OBD).
    if u is not None:
        uidb64 = urlsafe_base64_encode(force_bytes(u.pk))
        reset_token = default_token_generator.make_token(u)
        reset_link = request.build_absolute_uri(
            reverse('players:password_reset_confirm', kwargs={'uidb64': uidb64, 'token': reset_token})
        )

        context = {'reset_link': reset_link,
                   'username': u.username,
                   'first': u.first_name.capitalize(),
                   'last': u.last_name.capitalize()}

        _send_email('SOLICITAÇÃO DE RECUPERAÇÃO DE SENHA OBD',
                    settings.DEFAULT_FROM_EMAIL,
                    email,
                    'recovery_password.txt',
                    context)

    # Success feedback (genérico, independente de o e-mail existir ou não)
    messages.success(request, 'Recebemos sua solicitação. Se o e-mail informado estiver cadastrado, você receberá em instantes um link para redefinir sua senha.')
    boasession = ObdSession()
    token = boasession.startSession()
    return render(request, 'login.html', {'token': token})


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        u = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        u = None

    valid_link = u is not None and default_token_generator.check_token(u, token)

    if not valid_link:
        boasession = ObdSession()
        session_token = boasession.startSession()
        messages.error(request, 'Este link de redefinição de senha é inválido ou já expirou. Solicite um novo.')
        return render(request, 'login.html', {'form': LoginUserForm(), 'token': session_token})

    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            u.set_password(form.cleaned_data['password1'])
            u.save()
            boasession = ObdSession()
            session_token = boasession.startSession()
            messages.success(request, 'Senha redefinida com sucesso! Faça login com sua nova senha.')
            return render(request, 'login.html', {'form': LoginUserForm(), 'token': session_token})
    else:
        form = SetNewPasswordForm()

    return render(request, 'password_reset_confirm.html', {'form': form})


def _send_email(subject, from_, to, template_name, context):
    body = render_to_string(template_name, context)
    resend.Emails.send({
        "from": from_,
        "to": [from_, to],
        "subject": subject,
        "text": body,
    })


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

