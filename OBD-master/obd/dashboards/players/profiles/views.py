from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from obd.dashboards.administrators.fixtures.models import Fixture
from obd.dashboards.administrators.results.models import Result
from obd.dashboards.players.profiles.forms import ProfileForm
from obd.dashboards.players.profiles.models import Profile
from obd.dashboards.players.stats.models import Stat
from django.contrib.auth import login as auth_login
from obd.dashboards.players.profiles.forms import ClaimAccountForm
import cloudinary
import cloudinary.uploader
import cloudinary.api

@login_required()
def config(request):
    if request.method == 'POST':
        return updateconfig(request)
    else:
        return showconfig(request)

def showconfig(request):
    return showprofile(request)


def updateconfig(request):
    form = ProfileForm(request.POST, request.FILES)
    if not form.is_valid():
        return render(request, 'profile_view.html', {'form': form})

    # Update User Profile
    profile = Profile.objects.get(user=request.user)

    if form.cleaned_data['photo'] is not None:
        cloudinary_response = cloudinary.uploader.upload(form.cleaned_data['photo'],
                                                         public_id=f'boa/media/uploads/profiles/{profile.pin}',
                                                         gravity='face',
                                                         height='300',
                                                         width='300',
                                                         crop='thumb')

        profile.photo = cloudinary_response['url']

    profile.birth_date = form.cleaned_data['birthdate']
    profile.country = form.cleaned_data['country']
    profile.state = form.cleaned_data['state']
    profile.bio = form.cleaned_data['bio']
    profile.nickname = form.cleaned_data['nickname']
    profile.darts = form.cleaned_data['darts']
    profile.facebook = form.cleaned_data['facebook']
    profile.site = form.cleaned_data['site']
    profile.twitter = form.cleaned_data['social']
    profile.nakka = form.cleaned_data['nakka']

    # Marca como verificado automaticamente: se o jogador chegou até aqui e
    # salvou o próprio perfil, é prova de que é uma pessoa real controlando a conta.
    if not profile.is_verified:
        profile.is_verified = True

    profile.save()

    # Success feedback
    messages.success(request, 'Informações atualizadas com sucesso, ')
    return HttpResponseRedirect(reverse('profiles:config'))

def showprofile(request):
    return render(request, 'profile_view.html',
           {'form': ProfileForm(),
            'profile': Profile.objects.get(user=request.user)})

from django.db.models import Sum, Max, Min, Count, F
from obd.core.models import PlayerTournamentStat


def publicprofile(request, pin, first, last):

    profile = Profile.objects.get(pin=pin)
    matches = Fixture.objects.filter(status=1, validation=1, players__profile=profile).order_by('-on_date')[:5]
    stat = Stat.objects.get(user=profile.user)
    total = stat.divAwinner + stat.divBwinner + stat.divCwinner + stat.divDwinner + stat.divOtherswinner

    # === Estatísticas de Torneios (PlayerTournamentStat) ===
    t_stats = PlayerTournamentStat.objects.filter(player=profile.user)
    tournament_summary = None

    if t_stats.exists():
        agg = t_stats.aggregate(
            matches_played=Sum('matches_played'),
            matches_won=Sum('matches_won'),
            legs_played=Sum('legs_played'),
            total_100=Sum('count_100_plus'),
            total_140=Sum('count_140_plus'),
            total_170=Sum('count_170_plus'),
            total_180=Sum('count_180'),
            highest_out=Max('high_finish'),
            best_avg=Max('average_3_dart'),
        )

        best_leg_qs = t_stats.filter(best_leg__gte=9).aggregate(best_leg=Min('best_leg'))

        career_avg = 0
        if agg['legs_played']:
            weighted = t_stats.aggregate(w=Sum(F('average_3_dart') * F('legs_played')))['w'] or 0
            career_avg = weighted / agg['legs_played']

        titles = t_stats.filter(rank=1).count()

        tournament_summary = {
            **agg,
            'career_avg': career_avg,
            'titles': titles,
            'best_leg': best_leg_qs['best_leg'],
        }

    recent_tournaments = t_stats.select_related('tournament').order_by('-tournament__date')[:10]

    context = {'total': total,
               'profile': profile,
               'stat': stat,
               'matches': matches,
               'recent_tournaments': recent_tournaments,
               'tournament_summary': tournament_summary}

    return render(request, 'user_public_profile.html', context)

def publicprofile_by_pin(request, pin):
    profile = Profile.objects.get(pin=pin)
    first = profile.user.first_name or profile.pin
    last = profile.user.last_name or ''
    return publicprofile(request, pin, first, last)    

def claim_account(request, pin):
    try:
        profile = Profile.objects.get(pin=pin)
    except Profile.DoesNotExist:
        messages.error(request, 'Cadastro não encontrado.')
        return HttpResponseRedirect('/')

    if profile.is_verified:
        messages.info(request, 'Este cadastro já foi verificado. Se for você, faça login normalmente ou use "Esqueci minha senha".')
        return HttpResponseRedirect(reverse('players:login'))

    # Usuário já logado com outra conta - oferece mesclagem em vez do formulário de cadastro
    if request.user.is_authenticated and request.user.id != profile.user.id:
        if request.method == 'POST' and request.POST.get('confirm_merge') == 'yes':
            from obd.dashboards.administrators.champions.utils import merge_player_accounts
            source_user = profile.user
            target_user = request.user
            moved, skipped = merge_player_accounts(source_user, target_user)
            messages.success(request, f'Cadastros mesclados com sucesso! {moved} registro(s) migrado(s) para a sua conta.')
            return HttpResponseRedirect(reverse('players:dashboard'))

        return render(request, 'claim_account_merge_confirm.html', {
            'profile': profile,
            'current_user': request.user,
        })

    if request.method == 'POST':
        form = ClaimAccountForm(request.POST)
        if form.is_valid():
            user = profile.user
            user.email = form.cleaned_data['email']
            user.set_password(form.cleaned_data['password'])
            user.save()

            profile.is_verified = True
            profile.save()

            user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth_login(request, user)

            messages.success(request, f'Cadastro reivindicado com sucesso, {user.first_name}! Complete seu perfil abaixo.')
            return HttpResponseRedirect(reverse('profiles:config'))
    else:
        form = ClaimAccountForm()

    return render(request, 'claim_account.html', {'form': form, 'profile': profile})  
