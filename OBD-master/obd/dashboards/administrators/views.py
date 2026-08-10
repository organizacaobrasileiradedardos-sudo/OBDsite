from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from obd.core.models import TournamentResult
from obd.core.obdlib.webscraping.n01 import N01TournamentScraper
from obd.dashboards.administrators.fixtures.models import Fixture
from obd.dashboards.administrators.leagues.models import League
import pandas as pd 
import datetime
import unicodedata
from decimal import Decimal, InvalidOperation
from obd.dashboards.players.profiles.models import Profile
from obd.dashboards.administrators.leagues.models import League, OrderOfMeritEntry
from obd.dashboards.administrators.leagues.models import NationalRankingEntry
from obd.dashboards.administrators.champions.utils import get_or_create_player

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


@login_required
@permission_required('profiles.has_admin_role', raise_exception=True)
def scraping_dashboard(request):
    tournaments = TournamentResult.objects.all().order_by('-created_at')
    return render(request, 'scraping_dashboard.html', {'tournaments': tournaments})


@login_required
@permission_required('profiles.has_admin_role', raise_exception=True)
def run_capture(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        if url:
            scraper = N01TournamentScraper(url)
            success, message = scraper.run()
            if success:
                messages.success(request, message)
            else:
                messages.error(request, f"Erro: {message}")
        else:
            messages.error(request, "URL não fornecida.")
    
    return redirect('administrators:scraping_dashboard')


@login_required
@permission_required('profiles.has_admin_role', raise_exception=True)
def order_of_merit_dashboard(request):
    leagues = League.objects.filter(scope=2).order_by('-start_date')  # scope=2 = Nacional
    return render(request, 'order_of_merit_dashboard.html', {'leagues': leagues})


def _strip_accents(text):
    return ''.join(
        c for c in unicodedata.normalize('NFKD', text)
        if not unicodedata.combining(c)
    )

@login_required
@permission_required('profiles.has_admin_role', raise_exception=True)
def import_order_of_merit(request):
    if request.method != 'POST':
        return redirect('administrators:order_of_merit_dashboard')

    league_id = request.POST.get('league_id')
    excel_file = request.FILES.get('file')

    if not league_id or not excel_file:
        messages.error(request, "Selecione a etapa e o arquivo antes de importar.")
        return redirect('administrators:order_of_merit_dashboard')

    try:
        league = League.objects.get(id=league_id)
    except League.DoesNotExist:
        messages.error(request, "Etapa não encontrada.")
        return redirect('administrators:order_of_merit_dashboard')

    try:
        df = pd.read_excel(excel_file)
    except Exception as e:
        messages.error(request, f"Não foi possível ler o arquivo: {e}")
        return redirect('administrators:order_of_merit_dashboard')

    # Normaliza nomes de colunas (remove espaços, deixa minúsculo, tira acentos comuns)
    df.columns = [str(c).strip().lower() for c in df.columns]

    # Tenta localizar as colunas certas, aceitando pequenas variações
    col_pos = next((c for c in df.columns if 'pos' in c), None)
    col_player = next((c for c in df.columns if 'jogador' in c or 'nome' in c), None)
    col_value = next((c for c in df.columns if 'valor' in c or 'premia' in c or 'r$' in c), None)

    if not col_player or not col_value:
        messages.error(request, "Não foi possível identificar as colunas 'Jogador' e 'Valor' na planilha.")
        return redirect('administrators:order_of_merit_dashboard')

    matched = 0
    not_found = []
    created_provisional = []

    for _, row in df.iterrows():
        name = str(row[col_player]).strip()
        if not name or name.lower() == 'nan':
            continue

        raw_value = row[col_value]
        try:
            value = Decimal(str(raw_value).replace('R$', '').replace(',', '.').strip())
        except (InvalidOperation, ValueError):
            not_found.append(f"{name} (valor inválido: {raw_value})")
            continue

        position = None
        if col_pos:
            try:
                position = int(row[col_pos])
            except (ValueError, TypeError):
                position = None

        pin = name.replace(' ', '').lower()
        user = User.objects.filter(username__iexact=pin).first()

        if not user:
            # Fallback: nome na planilha pode ser abreviado (ex: "Rodrigo KEKO" vs
            # cadastro completo "Rodrigo Keko Johan"). Tenta achar por prefixo.
            candidates = list(User.objects.filter(username__istartswith=pin))
            if len(candidates) == 1:
                user = candidates[0]
            elif len(candidates) > 1:
                not_found.append(f"{name} (ambíguo: várias correspondências possíveis)")
                continue
            else:
                not_found.append(name)
                continue

        OrderOfMeritEntry.objects.update_or_create(
            player=user,
            league=league,
            defaults={'value': value, 'position_in_stage': position}
        )
        matched += 1

    messages.success(request, f"Importação concluída: {matched} jogadores atualizados na etapa {league.name}.")
    if not_found:
        messages.warning(request, f"{len(not_found)} nomes não encontrados no cadastro: {', '.join(not_found)}")

    return redirect('administrators:order_of_merit_dashboard')


@login_required
@permission_required('profiles.has_admin_role', raise_exception=True)
def national_ranking_dashboard(request):
    return render(request, 'national_ranking_dashboard.html')


@login_required
@permission_required('profiles.has_admin_role', raise_exception=True)
def import_national_ranking(request):
    if request.method != 'POST':
        return redirect('administrators:national_ranking_dashboard')

    excel_file = request.FILES.get('file')

    if not excel_file:
        messages.error(request, "Selecione o arquivo antes de importar.")
        return redirect('administrators:national_ranking_dashboard')

    try:
        df_raw = pd.read_excel(excel_file, header=None)
    except Exception as e:
        messages.error(request, f"Não foi possível ler o arquivo: {e}")
        return redirect('administrators:national_ranking_dashboard')

    # Linha 1 (índice 0): Torneio | Nome
    # Linha 2 (índice 1): Data | Data
    # Linha 4 (índice 3): Colocação | Jogador | Pontos
    try:
        tournament_name = str(df_raw.iloc[0, 1]).strip()
        raw_date = df_raw.iloc[1, 1]
    except (IndexError, KeyError):
        messages.error(request, "Formato inválido: verifique as linhas de Torneio e Data no início do arquivo.")
        return redirect('administrators:national_ranking_dashboard')

    if not tournament_name or tournament_name.lower() == 'nan':
        messages.error(request, "Nome do torneio não encontrado na linha 1.")
        return redirect('administrators:national_ranking_dashboard')

    if isinstance(raw_date, (datetime.datetime, datetime.date)):
        tournament_date = raw_date.date() if isinstance(raw_date, datetime.datetime) else raw_date
    else:
        try:
            tournament_date = datetime.datetime.strptime(str(raw_date).strip(), '%d/%m/%Y').date()
        except ValueError:
            messages.error(request, f"Data inválida na linha 2: '{raw_date}'. Use o formato DD/MM/AAAA.")
            return redirect('administrators:national_ranking_dashboard')

    # Get or create the League (torneio)
    slug = tournament_name.lower().replace(' ', '-')
    league, created = League.objects.get_or_create(
        name=tournament_name,
        defaults={
            'slug': slug,
            'start_date': tournament_date,
            'end_date': tournament_date,
            'runoff': 1,
            'phase': 4,
            'scope': 0,
            'status': True,
        }
    )

    # Linha 4 (índice 3) em diante = tabela de jogadores
    try:
        df = pd.read_excel(excel_file, skiprows=3)
    except Exception as e:
        messages.error(request, f"Não foi possível ler a tabela de jogadores: {e}")
        return redirect('administrators:national_ranking_dashboard')

    df.columns = [str(c).strip().lower() for c in df.columns]

    col_pos = next((c for c in df.columns if 'pos' in c or 'coloca' in c), None)
    col_player = next((c for c in df.columns if 'jogador' in c or 'nome' in c), None)
    col_points = next((c for c in df.columns if 'ponto' in c), None)

    if not col_player or not col_points:
        messages.error(request, "Não foi possível identificar as colunas 'Jogador' e 'Pontos' na tabela.")
        return redirect('administrators:national_ranking_dashboard')

    matched = 0
    not_found = []
    created_provisional = []

    for _, row in df.iterrows():
        name = str(row[col_player]).strip()
        if not name or name.lower() == 'nan':
            continue

        raw_points = row[col_points]
        try:
            points = Decimal(str(raw_points).replace(',', '.').strip())
        except (InvalidOperation, ValueError):
            not_found.append(f"{name} (valor inválido: {raw_points})")
            continue

        position = None
        if col_pos:
            try:
                position = int(row[col_pos])
            except (ValueError, TypeError):
                position = None

        pin = name.replace(' ', '').lower()
        user = User.objects.filter(username__iexact=pin).first()

        if not user:
            candidates = list(User.objects.filter(username__istartswith=pin))
            if not candidates:
                pin_no_accent = _strip_accents(pin)
                candidates = [
                    u for u in User.objects.only('id', 'username')
                    if _strip_accents(u.username.lower()).startswith(pin_no_accent)
                ]
            if len(candidates) == 1:
                user = candidates[0]
            elif len(candidates) > 1:
                not_found.append(f"{name} (ambíguo: várias correspondências possíveis)")
                continue

        if not user:
            # Cria cadastro provisório (não verificado), igual à Captura de Torneios
            user = get_or_create_player(name, pin)
            created_provisional.append(name)

        NationalRankingEntry.objects.update_or_create(
            player=user,
            league=league,
            defaults={'points': points, 'position_in_stage': position}
        )
        matched += 1

    action = "criado" if created else "encontrado"
    messages.success(request, f"Torneio '{tournament_name}' {action}. Importação concluída: {matched} jogadores atualizados.")
    if created_provisional:
        messages.info(request, f"{len(created_provisional)} cadastros provisórios criados (aguardando reivindicação): {', '.join(created_provisional)}")
    if not_found:
        messages.warning(request, f"{len(not_found)} nomes com problema: {', '.join(not_found)}")

    return redirect('administrators:national_ranking_dashboard')


def _player_summary(user):
    return {
        'user': user,
        'tournament_stats': PlayerTournamentStat.objects.filter(player=user).count(),
        'order_of_merit': OrderOfMeritEntry.objects.filter(player=user).count(),
        'national_ranking': NationalRankingEntry.objects.filter(player=user).count(),
        'champion_titles': (
            Champion.objects.filter(p1=user).count()
            + Champion.objects.filter(p2=user).count()
            + Champion.objects.filter(p3=user).count()
            + Champion.objects.filter(p4=user).count()
        ),
    }


@login_required
@permission_required('profiles.has_admin_role', raise_exception=True)
def merge_players_dashboard(request):
    from obd.core.models import PlayerTournamentStat

    source_username = request.POST.get('source_username') or request.GET.get('source_username')
    target_username = request.POST.get('target_username') or request.GET.get('target_username')

    context = {'source_username': source_username or '', 'target_username': target_username or ''}

    if source_username and target_username:
        try:
            source_user = User.objects.get(username__iexact=source_username.strip())
        except User.DoesNotExist:
            messages.error(request, f"Usuário '{source_username}' (a mesclar) não encontrado.")
            return render(request, 'merge_players_dashboard.html', context)

        try:
            target_user = User.objects.get(username__iexact=target_username.strip())
        except User.DoesNotExist:
            messages.error(request, f"Usuário '{target_username}' (a manter) não encontrado.")
            return render(request, 'merge_players_dashboard.html', context)

        if source_user.id == target_user.id:
            messages.error(request, "Os dois usuários são o mesmo. Escolha usuários diferentes.")
            return render(request, 'merge_players_dashboard.html', context)

        context['source_summary'] = _player_summary(source_user)
        context['target_summary'] = _player_summary(target_user)
        context['show_confirm'] = True

    return render(request, 'merge_players_dashboard.html', context)


@login_required
@permission_required('profiles.has_admin_role', raise_exception=True)
def merge_players_execute(request):
    from obd.core.models import PlayerTournamentStat

    if request.method != 'POST':
        return redirect('administrators:merge_players_dashboard')

    source_username = request.POST.get('source_username')
    target_username = request.POST.get('target_username')

    try:
        source_user = User.objects.get(username__iexact=source_username)
        target_user = User.objects.get(username__iexact=target_username)
    except User.DoesNotExist:
        messages.error(request, "Usuário não encontrado. Nada foi alterado.")
        return redirect('administrators:merge_players_dashboard')

    if source_user.id == target_user.id:
        messages.error(request, "Os dois usuários são o mesmo. Nada foi alterado.")
        return redirect('administrators:merge_players_dashboard')

    moved = 0
    skipped = 0

    # PlayerTournamentStat - sem unique_together, sempre migra
    moved += PlayerTournamentStat.objects.filter(player=source_user).update(player=target_user)

    # OrderOfMeritEntry - unique_together (player, league): se já existir para o target, descarta o do source
    for entry in OrderOfMeritEntry.objects.filter(player=source_user):
        if OrderOfMeritEntry.objects.filter(player=target_user, league=entry.league).exists():
            entry.delete()
            skipped += 1
        else:
            entry.player = target_user
            entry.save()
            moved += 1

    # NationalRankingEntry - mesma lógica
    for entry in NationalRankingEntry.objects.filter(player=source_user):
        if NationalRankingEntry.objects.filter(player=target_user, league=entry.league).exists():
            entry.delete()
            skipped += 1
        else:
            entry.player = target_user
            entry.save()
            moved += 1

    # Champion - migra p1/p2/p3/p4
    for field in ['p1', 'p2', 'p3', 'p4']:
        Champion.objects.filter(**{field: source_user}).update(**{field: target_user})

    # Apaga o usuário duplicado (e o Profile dele, via CASCADE)
    source_user.delete()

    messages.success(
        request,
        f"Mesclagem concluída: {moved} registros migrados, {skipped} descartados por já existirem no destino. "
        f"'{source_username}' foi removido."
    )
    return redirect('administrators:merge_players_dashboard')