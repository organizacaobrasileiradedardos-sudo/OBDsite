from django.contrib.auth.decorators import permission_required, login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from obd.dashboards.administrators.enviroments.forms import EnviromentForm
from obd.dashboards.administrators.enviroments.models import Enviroment
from django.contrib import messages


@login_required()
@permission_required('profiles.has_admin_role', raise_exception=True)
def dashboard(request):
    if request.method == 'POST':
        return EnviromentsCreate(request)
    else:
        return EnviromentsIndex(request)


@login_required()
@permission_required('profiles.has_admin_role', raise_exception=True)
def EnviromentsIndex(request):
    return render(request, 'enviroment.html', {'form': EnviromentForm(), 'env': Enviroment.objects.first()})


@login_required()
@permission_required('profiles.has_admin_role', raise_exception=True)
def EnviromentsCreate(request):
    form = EnviromentForm(request.POST)
    if not form.is_valid():
        messages.success(request, 'Erro no formulário!')
        context = {'form': EnviromentForm()}
        return render(request, 'enviroment.html', context)

    # Create new Enviroment Table
    env = Enviroment()

    # Setting ENV from FORM data
    env.meritPmin = form.cleaned_data['meritPmin']
    env.meritAmin = form.cleaned_data['meritAmin']
    env.meritBmin = form.cleaned_data['meritBmin']
    env.meritCmin = form.cleaned_data['meritCmin']
    env.meritDmin = form.cleaned_data['meritDmin']
    env.meritRmin = form.cleaned_data['meritRmin']
    env.meritTimeline = form.cleaned_data['meritTimeline']
    env.meritChampionBonus = form.cleaned_data['meritChampionBonus']
    env.meritSecondBonus = form.cleaned_data['meritSecondBonus']
    env.meritThirdBonus = form.cleaned_data['meritThirdBonus']
    env.meritDivAPoints = form.cleaned_data['meritDivAPoints']
    env.meritDivBPoints = form.cleaned_data['meritDivBPoints']
    env.meritDivCPoints = form.cleaned_data['meritDivCPoints']
    env.meritDivOthersPoints = form.cleaned_data['meritDivOthersPoints']
    env.matchDrawPoints = form.cleaned_data['matchDrawPoints']
    env.matchWinPoints = form.cleaned_data['matchWinPoints']
    env.leagueMinPlayers = form.cleaned_data['leagueMinPlayers']
    env.leagueMaxPlayers = form.cleaned_data['leagueMaxPlayers']
    env.allowAutoDemo = form.cleaned_data['allowAutoDemo']
    env.allowAutoPromo = form.cleaned_data['allowAutoPromo']
    env.allowAutoBye = form.cleaned_data['allowAutoBye']
    env.leagueSubscriptionsEnds = form.cleaned_data['leagueSubscriptionsEnds']
    env.leagueAplayoffs = form.cleaned_data['leagueAplayoffs']
    env.leagueBplayoffs = form.cleaned_data['leagueBplayoffs']
    env.leagueCplayoffs = form.cleaned_data['leagueCplayoffs']
    env.leagueOthersplayoffs = form.cleaned_data['leagueOthersplayoffs']
    env.leagueAMaxSet = form.cleaned_data['leagueAMaxSet']
    env.leagueBMaxSet = form.cleaned_data['leagueBMaxSet']
    env.leagueCMaxSet = form.cleaned_data['leagueCMaxSet']
    env.leagueOthersMaxSet = form.cleaned_data['leagueOthersMaxSet']
    env.leagueABestof = form.cleaned_data['leagueABestof']
    env.leagueBBestof = form.cleaned_data['leagueBBestof']
    env.leagueCBestof = form.cleaned_data['leagueCBestof']
    env.leagueOthersBestof = form.cleaned_data['leagueOthersBestof']
    env.leagueAFirstTo = form.cleaned_data['leagueAFirstTo']
    env.leagueBFirstTo = form.cleaned_data['leagueBFirstTo']
    env.leagueCFirstTo = form.cleaned_data['leagueCFirstTo']
    env.leagueOthersFirstTo = form.cleaned_data['leagueOthersFirstTo']
    env.leagueAGameMode = form.cleaned_data['leagueAGameMode']
    env.leagueBGameMode = form.cleaned_data['leagueBGameMode']
    env.leagueCGameMode = form.cleaned_data['leagueCGameMode']
    env.leagueOthersGameMode = form.cleaned_data['leagueOthersGameMode']
    env.leagueAWinnerBy = form.cleaned_data['leagueAWinnerBy']
    env.leagueBWinnerBy = form.cleaned_data['leagueBWinnerBy']
    env.leagueCWinnerBy = form.cleaned_data['leagueCWinnerBy']
    env.leagueOthersWinnerBy = form.cleaned_data['leagueOthersWinnerBy']
    env.save()

    # Send a success message to requestor page
    messages.success(request, 'Nova configuração da Liga OBD criada com sucesso!')
    return HttpResponseRedirect('enviroment')

