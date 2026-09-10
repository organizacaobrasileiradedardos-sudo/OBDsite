from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from obd.core.models import TournamentResult
from obd.core.models import PlayerTournamentStat
from obd.core.obdlib.webscraping.n01 import N01TournamentScraper
from obd.dashboards.administrators.leagues.models import League
import pandas as pd 
import datetime
import unicodedata
from decimal import Decimal, InvalidOperation
from obd.dashboards.players.profiles.models import Profile
from obd.dashboards.administrators.leagues.models import League, OrderOfMeritEntry
from obd.dashboards.administrators.leagues.models import NationalRankingEntry
from obd.dashboards.administrators.champions.utils import get_or_create_player
from obd.dashboards.administrators.champions.models import Champion

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
               'canceled': inactives}

    return render(request, 'dashadmin.html', context)

def members(request):
    players = User.objects.all()
    return render(request, 'admin_user_list.html', {'players': players})

def logoutAdm(request):
    pass


@login_required
@permission_required('profiles.has_admin_role', raise_exception=True)
def scraping_dashboard(request):
    from obd.core.tournament_categories import CHOICES

    tournaments = TournamentResult.objects.all().order_by('-created_at')
    return render(request, 'scraping_dashboard.html', {
        'tournaments': tournaments,
        'tipos_de_torneio': CHOICES,
    })


@login_required
@permission_required('profiles.has_admin_role', raise_exception=True)
def run_capture(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        if url:
            in_progress = request.POST.get('in_progress') == 'on'
            scraper = N01TournamentScraper(url, in_progress=in_progress)
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
def update_tournament_prize(request, tournament_id):
    tournament = get_object_or_404(TournamentResult, id=tournament_id)
    if request.method == 'POST':
        raw_value = request.POST.get('prize_value', '').strip()
        if not raw_value:
            tournament.prize_value = None
        else:
            try:
                tournament.prize_value = Decimal(raw_value.replace(',', '.'))
            except InvalidOperation:
                messages.error(request, f"Valor de premiação inválido: {raw_value}")
                return redirect('administrators:scraping_dashboard')
        tournament.save(update_fields=['prize_value'])
        messages.success(request, f"Premiação de \"{tournament.name}\" atualizada.")

    return redirect('administrators:scraping_dashboard')


@login_required
@permission_required('profiles.has_admin_role', raise_exception=True)
def update_tournament_category(request, tournament_id):
    """Grava o tipo do torneio, que define o bloco do Hall dos Campeões."""
    from obd.core.tournament_categories import CATEGORIAS, label

    tournament = get_object_or_404(TournamentResult, id=tournament_id)
    if request.method != 'POST':
        return redirect('administrators:scraping_dashboard')

    escolha = request.POST.get('category', '')
    if escolha not in CATEGORIAS:
        messages.error(request, "Tipo de torneio inválido. Nada foi alterado.")
        return redirect('administrators:scraping_dashboard')

    tournament.category = escolha
    tournament.save(update_fields=['category'])
    messages.success(request, f'"{tournament.name}" agora aparece em {label(escolha)}.')

    # Quem manda no Hall dos Campeões é o tipo gravado na liga. Normalmente a liga tem
    # o mesmo nome do torneio, então dá para repassar. Quando não tem — porque o
    # torneio foi renomeado no N01 depois de o campeão ser registrado — é preciso
    # avisar, senão o Hall continuaria mostrando a categoria antiga sem explicação.
    from obd.dashboards.administrators.leagues.models import League
    ligas = League.objects.filter(name=tournament.name)
    if ligas.update(category=escolha) == 0 and tournament.stats.filter(rank=1).exists():
        messages.warning(
            request,
            f'Nenhuma liga com o nome "{tournament.name}" foi encontrada. Se o campeão deste '
            'torneio já estiver no Hall dos Campeões, ele continua na categoria antiga: '
            'o nome do torneio mudou depois que o campeão foi registrado. Corrija o tipo da '
            'liga em /admin/ → Ligas.'
        )

    return redirect('administrators:scraping_dashboard')


@login_required
@permission_required('profiles.has_admin_role', raise_exception=True)
def delete_tournament(request, tournament_id):
    """Apaga uma captura do histórico.

    Serve principalmente para desfazer uma captura duplicada. As estatísticas
    dos jogadores daquele torneio saem junto, por causa do on_delete=CASCADE.
    """
    tournament = get_object_or_404(TournamentResult, id=tournament_id)
    if request.method != 'POST':
        return redirect('administrators:scraping_dashboard')

    nome = tournament.name
    quantidade = tournament.stats.count()
    tournament.delete()
    messages.success(
        request,
        f'Captura de "{nome}" excluída, junto com {quantidade} estatística(s) de jogadores.'
    )
    return redirect('administrators:scraping_dashboard')


@login_required
@permission_required('profiles.has_admin_role', raise_exception=True)
def update_tournament_progress(request, tournament_id):
    tournament = get_object_or_404(TournamentResult, id=tournament_id)
    if request.method != 'POST':
        return redirect('administrators:scraping_dashboard')

    was_in_progress = tournament.in_progress
    tournament.in_progress = request.POST.get('in_progress') == 'on'
    tournament.save(update_fields=['in_progress'])

    if tournament.in_progress:
        messages.success(request, f"\"{tournament.name}\" marcada como etapa em andamento.")

        # Enquanto a etapa está em disputa não existe campeão, só líder do momento.
        # Se um campeão já tinha sido gravado, ele sai do Hall dos Campeões agora.
        from obd.dashboards.administrators.champions.utils import remove_champion_from_tournament
        if remove_champion_from_tournament(tournament):
            messages.info(request, "O campeão que estava registrado para esta etapa foi removido do Hall dos Campeões.")

        return redirect('administrators:scraping_dashboard')

    messages.success(request, f"\"{tournament.name}\" marcada como finalizada.")

    # Finalizar é o momento de registrar o campeão: o pódio já está no banco.
    if was_in_progress:
        from obd.dashboards.administrators.champions.utils import register_champion_from_tournament
        champion = register_champion_from_tournament(tournament)
        if champion:
            messages.success(request, f"Campeão registrado: {champion.p1.first_name} {champion.p1.last_name}.")
        else:
            messages.warning(request, "Nenhum 1º colocado encontrado — campeão não registrado.")

    return redirect('administrators:scraping_dashboard')


@login_required
@permission_required('profiles.has_admin_role', raise_exception=True)
def order_of_merit_dashboard(request):
    existing_leagues = League.objects.all().order_by('-start_date')
    return render(request, 'order_of_merit_dashboard.html', {'existing_leagues': existing_leagues})


def _strip_accents(text):
    return ''.join(
        c for c in unicodedata.normalize('NFKD', text)
        if not unicodedata.combining(c)
    )


# As duas importações (Order of Merit e Ranking Nacional) leem o mesmo formato de
# planilha e só diferem no rótulo, na coluna de valor e no model gravado.
IMPORT_KINDS = {
    'merit': {
        'noun': 'Etapa',
        'title': 'Order of Merit',
        'dashboard': 'administrators:order_of_merit_dashboard',
        'confirm': 'administrators:confirm_order_of_merit',
        'value_cols': ('valor', 'premia', 'r$'),
        'value_label': 'Valor (R$)',
        'strip_currency': True,
        'model': OrderOfMeritEntry,
        'value_field': 'value',
        'scope': 2,
    },
    'ranking': {
        'noun': 'Torneio',
        'title': 'Ranking Nacional',
        'dashboard': 'administrators:national_ranking_dashboard',
        'confirm': 'administrators:confirm_national_ranking',
        'value_cols': ('ponto',),
        'value_label': 'Pontos',
        'strip_currency': False,
        'model': NationalRankingEntry,
        'value_field': 'points',
        'scope': 0,
    },
}


def _parse_import_sheet(excel_file, kind):
    """Lê a planilha e devolve (nome, data, linhas, erro).

    Cada linha é um dicionário com nome do jogador, valor e colocação. Não toca
    no banco: serve tanto para a tela de conferência quanto para a gravação.
    """
    cfg = IMPORT_KINDS[kind]
    try:
        df_raw = pd.read_excel(excel_file, header=None)
    except Exception as e:
        return None, None, None, f"Não foi possível ler o arquivo: {e}"

    try:
        etapa_name = str(df_raw.iloc[0, 1]).strip()
        raw_date = df_raw.iloc[1, 1]
    except (IndexError, KeyError):
        return None, None, None, (
            f"Formato inválido: verifique as linhas de {cfg['noun']} e Data no início do arquivo."
        )

    if not etapa_name or etapa_name.lower() == 'nan':
        return None, None, None, f"Nome d{'a etapa' if kind == 'merit' else 'o torneio'} não encontrado na linha 1."

    if isinstance(raw_date, (datetime.datetime, datetime.date)):
        etapa_date = raw_date.date() if isinstance(raw_date, datetime.datetime) else raw_date
    else:
        try:
            etapa_date = datetime.datetime.strptime(str(raw_date).strip(), '%d/%m/%Y').date()
        except ValueError:
            return None, None, None, f"Data inválida na linha 2: '{raw_date}'. Use o formato DD/MM/AAAA."

    excel_file.seek(0)
    try:
        df = pd.read_excel(excel_file, skiprows=3)
    except Exception as e:
        return None, None, None, f"Não foi possível ler a tabela de jogadores: {e}"

    df.columns = [str(c).strip().lower() for c in df.columns]
    col_pos = next((c for c in df.columns if 'pos' in c or 'coloca' in c), None)
    col_player = next((c for c in df.columns if 'jogador' in c or 'nome' in c), None)
    col_value = next((c for c in df.columns if any(t in c for t in cfg['value_cols'])), None)

    if not col_player or not col_value:
        return None, None, None, (
            f"Não foi possível identificar as colunas 'Jogador' e '{cfg['value_label']}' na tabela."
        )

    linhas = []
    for _, row in df.iterrows():
        name = str(row[col_player]).strip()
        if not name or name.lower() == 'nan':
            continue

        raw_value = row[col_value]
        texto = str(raw_value)
        if cfg['strip_currency']:
            texto = texto.replace('R$', '')
        try:
            value = Decimal(texto.replace(',', '.').strip())
        except (InvalidOperation, ValueError):
            linhas.append({'name': name, 'value': None, 'position': None, 'erro': f"valor inválido: {raw_value}"})
            continue

        position = None
        if col_pos:
            try:
                position = int(row[col_pos])
            except (ValueError, TypeError):
                position = None

        linhas.append({'name': name, 'value': value, 'position': position, 'erro': None})

    return etapa_name, etapa_date, linhas, None


def _classify_player(name):
    """Como o nome da planilha se relaciona com as contas existentes.

    Devolve (situacao, user, candidatos), onde situacao é:
      'nakka'    - casou pelo apelido do N01 (vínculo explícito, confiável)
      'username' - casou pelo nome de usuário exato
      'palpite'  - só um candidato por prefixo; precisa de confirmação
      'ambiguo'  - vários candidatos por prefixo
      'novo'     - ninguém parecido
    """
    pin = name.replace(' ', '').lower()

    by_nakka = Profile.objects.filter(nakka__iexact=name.strip()).first()
    if by_nakka:
        return 'nakka', by_nakka.user, []

    exato = User.objects.filter(username__iexact=pin).first()
    if exato:
        return 'username', exato, []

    candidatos = list(User.objects.filter(username__istartswith=pin))
    if not candidatos:
        sem_acento = _strip_accents(pin)
        candidatos = [
            u for u in User.objects.all()
            if _strip_accents(u.username.lower()).startswith(sem_acento)
        ]

    if len(candidatos) == 1:
        return 'palpite', candidatos[0], candidatos
    if len(candidatos) > 1:
        return 'ambiguo', None, candidatos
    return 'novo', None, []


def _save_nakka(user, name):
    """Grava o nome da planilha como apelido do N01, se ainda não houver conflito.

    É isso que torna a correção definitiva: na próxima importação o jogador já
    casa sozinho, sem passar de novo pela tela de conferência.
    """
    nakka = name.strip()
    profile = getattr(user, 'profile', None)
    if not profile or profile.nakka.strip().lower() == nakka.lower():
        return False
    if Profile.objects.filter(nakka__iexact=nakka).exclude(pk=profile.pk).exists():
        return False
    profile.nakka = nakka
    profile.save(update_fields=['nakka'])
    return True


def _import_review(request, kind):
    """Passo 1: lê a planilha, classifica cada jogador e mostra para conferência."""
    cfg = IMPORT_KINDS[kind]
    if request.method != 'POST':
        return redirect(cfg['dashboard'])

    excel_file = request.FILES.get('file')
    if not excel_file:
        messages.error(request, "Selecione o arquivo antes de importar.")
        return redirect(cfg['dashboard'])

    etapa_name, etapa_date, linhas, erro = _parse_import_sheet(excel_file, kind)
    if erro:
        messages.error(request, erro)
        return redirect(cfg['dashboard'])

    reconhecidos, conferir, invalidos = [], [], []
    for linha in linhas:
        if linha['erro']:
            invalidos.append(linha)
            continue

        situacao, user, candidatos = _classify_player(linha['name'])
        item = {**linha, 'situacao': situacao, 'user': user, 'candidatos': candidatos}
        (reconhecidos if situacao in ('nakka', 'username') else conferir).append(item)

    if not reconhecidos and not conferir:
        messages.error(request, "Nenhum jogador válido encontrado na planilha.")
        return redirect(cfg['dashboard'])

    return render(request, 'import_review.html', {
        'kind': kind,
        'cfg': cfg,
        'confirm_url': cfg['confirm'],
        'dashboard_url': cfg['dashboard'],
        'etapa_name': etapa_name,
        'etapa_date': etapa_date.isoformat(),
        'etapa_date_display': etapa_date,
        'reconhecidos': reconhecidos,
        'conferir': conferir,
        'invalidos': invalidos,
        'jogadores': User.objects.filter(is_superuser=False).order_by('first_name', 'last_name'),
    })


def _import_confirm(request, kind):
    """Passo 2: grava exatamente o que foi revisado na tela de conferência."""
    cfg = IMPORT_KINDS[kind]
    if request.method != 'POST':
        return redirect(cfg['dashboard'])

    etapa_name = request.POST.get('etapa_name', '').strip()
    try:
        etapa_date = datetime.date.fromisoformat(request.POST.get('etapa_date', ''))
    except ValueError:
        messages.error(request, "Dados da importação expiraram. Envie a planilha novamente.")
        return redirect(cfg['dashboard'])

    league, created = League.objects.get_or_create(
        name=etapa_name,
        defaults={
            'slug': etapa_name.lower().replace(' ', '-'),
            'start_date': etapa_date,
            'end_date': etapa_date,
            'runoff': 1,
            'phase': 4,
            'scope': cfg['scope'],
            'status': True,
        }
    )

    gravados, criados, pulados, vinculados = 0, [], [], []

    for idx in request.POST.getlist('row'):
        name = request.POST.get(f'name_{idx}', '').strip()
        escolha = request.POST.get(f'choice_{idx}', 'skip')
        if not name or escolha == 'skip':
            if name:
                pulados.append(name)
            continue

        try:
            # aceita vírgula decimal, caso o campo venha formatado no padrão local
            value = Decimal(request.POST.get(f'value_{idx}', '').replace(',', '.'))
        except (InvalidOperation, ValueError):
            pulados.append(name)
            continue

        posicao = request.POST.get(f'position_{idx}', '')
        position = int(posicao) if posicao.isdigit() else None

        if escolha == 'new':
            user = get_or_create_player(name, name.replace(' ', '').lower())
            criados.append(name)
        else:
            user = User.objects.filter(pk=escolha.removeprefix('u:')).first()
            if not user:
                pulados.append(name)
                continue
            if request.POST.get(f'save_nakka_{idx}') == 'on' and _save_nakka(user, name):
                vinculados.append(f'{name} → {user.first_name} {user.last_name}')

        cfg['model'].objects.update_or_create(
            player=user,
            league=league,
            defaults={cfg['value_field']: value, 'position_in_stage': position}
        )
        gravados += 1

    acao = "criad" + ("a" if kind == 'merit' else "o")
    encontrado = "encontrad" + ("a" if kind == 'merit' else "o")
    messages.success(
        request,
        f"{cfg['noun']} '{etapa_name}' {acao if created else encontrado}. "
        f"Importação concluída: {gravados} jogadores atualizados."
    )
    if criados:
        messages.info(request, f"{len(criados)} cadastros provisórios criados: {', '.join(criados)}")
    if vinculados:
        messages.info(
            request,
            f"{len(vinculados)} apelido(s) do N01 gravados — nas próximas importações "
            f"esses jogadores serão reconhecidos sozinhos: {', '.join(vinculados)}"
        )
    if pulados:
        messages.warning(request, f"{len(pulados)} linha(s) ignorada(s): {', '.join(pulados)}")

    return redirect(cfg['dashboard'])

@login_required
@permission_required('profiles.has_admin_role', raise_exception=True)
def import_order_of_merit(request):
    return _import_review(request, 'merit')


@login_required
@permission_required('profiles.has_admin_role', raise_exception=True)
def national_ranking_dashboard(request):
    existing_leagues = League.objects.all().order_by('-start_date')
    return render(request, 'national_ranking_dashboard.html', {'existing_leagues': existing_leagues})


@login_required
@permission_required('profiles.has_admin_role', raise_exception=True)
def import_national_ranking(request):
    return _import_review(request, 'ranking')



@login_required
@permission_required('profiles.has_admin_role', raise_exception=True)
def confirm_order_of_merit(request):
    return _import_confirm(request, 'merit')


@login_required
@permission_required('profiles.has_admin_role', raise_exception=True)
def confirm_national_ranking(request):
    return _import_confirm(request, 'ranking')


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

    from obd.dashboards.administrators.champions.utils import merge_player_accounts
    moved, skipped = merge_player_accounts(source_user, target_user)

    messages.success(
        request,
        f"Mesclagem concluída: {moved} registros migrados, {skipped} descartados por já existirem no destino. "
        f"'{source_username}' foi removido."
    )
    return redirect('administrators:merge_players_dashboard')