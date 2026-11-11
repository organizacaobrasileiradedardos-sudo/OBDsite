import requests
from bs4 import BeautifulSoup
from django.utils import timezone
from obd.core.models import TournamentResult, PlayerTournamentStat
from obd.core.tournament_categories import adivinhar_categoria
import re
import json
from urllib.parse import urljoin
from obd.dashboards.administrators.champions.utils import get_or_create_player, get_or_create_league, register_champion


# Pasta de onde o N01 serve os endpoints do torneio, usada **só** quando a página não diz
# qual é a dela.
#
# Aqui havia o host cru do servidor do N01 (tk2-228-23746.vs.sakura.ne.jp). Quando eles
# puseram um balanceador na frente, esse host passou a responder com um certificado de
# outro nome, e a captura começou a falhar com erro de SSL — uma mensagem que não diz nada
# a quem está no painel. Por isso o endereço de reserva agora é o nome público, que tem
# certificado próprio, e a descoberta pela página virou o caminho principal.
BASE_DA_API_RESERVA = 'https://lbc.n01darts.com/n01/tournament/'

# Formato antigo: cada endpoint escrito inteiro dentro do HTML da página.
_ENDPOINT_NO_HTML = re.compile(r'php(?:TournamentStats|Tournament)\s*:\s*["\']([^"\']+)["\']')

# Formato atual: uma base única, de onde todos os endpoints são montados por concatenação.
_BASE_DECLARADA = re.compile(r'phpSite\s*=\s*["\']([^"\']+)["\']')

# O arquivo de configuração onde essa base passou a morar.
_SCRIPT_DE_CONFIGURACAO = re.compile(r'src\s*=\s*["\']([^"\']*n01_data\.js[^"\']*)["\']')

TEMPO_LIMITE = 30


def tournament_id_from_url(url):
    """Extrai o id do torneio da URL (ex: .../t_stats.html?id=t_ehLY_1878 -> t_ehLY_1878)."""
    match = re.search(r'id=([^&]+)', url or '')
    return match.group(1) if match else None


class N01TournamentScraper:
    def __init__(self, url, in_progress=None):
        # in_progress=None significa "não mexer no status": é o caso das
        # recapturas (botão e agendamento), que nunca devem finalizar nem
        # reabrir uma etapa por conta própria.
        self.url = url
        self.in_progress = in_progress
        # A base dos endpoints é descoberta uma vez e reaproveitada: são duas chamadas
        # (lista de inscritos e estatísticas) que saem da mesma pasta.
        self._base_da_api = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
            'Origin': 'https://n01darts.com',
            'Referer': 'https://n01darts.com/'
        })

    def get_tournament_id(self):
        return tournament_id_from_url(self.url)

    def find_existing_tournament(self):
        """Procura uma captura anterior do mesmo torneio, mesmo que por outra URL.

        O N01 serve o mesmo torneio em páginas diferentes (comp.php e
        t_stats.html, por exemplo). Se procurássemos pelo texto da URL, colar o
        outro endereço criaria uma captura duplicada em vez de atualizar a que
        já existe.
        """
        tid = self.get_tournament_id()
        if not tid:
            return None
        candidatos = TournamentResult.objects.filter(source_url__contains=tid).order_by('created_at')
        for candidato in candidatos:
            if tournament_id_from_url(candidato.source_url) == tid:
                return candidato
        return None

    def fetch_html(self):
        try:
            response = self.session.get(self.url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching HTML: {e}")
            return None

    @staticmethod
    def _com_esquema(url):
        """O N01 escreve os endereços sem `https:`, herdando o esquema da página."""
        url = 'https:' + url if url.startswith('//') else url
        return url if url.endswith('/') else url + '/'

    def base_da_api(self, html):
        """Pasta de onde sairão os endpoints do torneio, descoberta a partir da página.

        Ler isso da página, em vez de fixar no código, é o que mantém a captura viva: o N01
        já mudou o endereço duas vezes, e das duas o valor fixo aqui dentro foi o que
        quebrou. São três formatos tentados, do mais antigo para o atual.
        """
        if self._base_da_api is None:
            self._base_da_api = self._descobrir_base(html) or BASE_DA_API_RESERVA
        return self._base_da_api

    def _descobrir_base(self, html):
        # 1. Formato antigo: o endpoint inteiro escrito na página. Fica em primeiro lugar
        #    porque, se uma página ainda trouxer isso, é a informação mais direta.
        achado = _ENDPOINT_NO_HTML.search(html)
        if achado:
            endpoint = self._com_esquema(achado.group(1)).rstrip('/')
            return endpoint.rsplit('/', 1)[0] + '/'

        # 2. A base declarada na própria página.
        achado = _BASE_DECLARADA.search(html)
        if achado:
            return self._com_esquema(achado.group(1))

        # 3. A base declarada no arquivo de configuração que a página carrega. É aqui que
        #    ela está hoje: o N01 tirou os endereços do HTML e passou a montá-los a partir
        #    de `phpSite`, em n01_v2/js/n01_data.js.
        achado = _SCRIPT_DE_CONFIGURACAO.search(html)
        if not achado:
            return None
        try:
            resposta = self.session.get(urljoin(self.url, achado.group(1)), timeout=TEMPO_LIMITE)
            resposta.raise_for_status()
        except requests.RequestException as erro:
            print(f'Não foi possível ler a configuração do N01: {erro}')
            return None
        achado = _BASE_DECLARADA.search(resposta.text)
        return self._com_esquema(achado.group(1)) if achado else None

    def get_api_base(self, html):
        """Endpoint das estatísticas dos jogadores."""
        return self.base_da_api(html) + 'n01_stats_t.php'

    def get_entry_list_url(self, html):
        """Endpoint dos dados do torneio e da lista de inscritos."""
        return self.base_da_api(html) + 'n01_tournament.php'

    def run(self):
        tdid = self.get_tournament_id()
        if not tdid:
            return False, "Could not extract Tournament ID from URL"

        html = self.fetch_html()
        if not html:
            return False, "Failed to fetch tournament page"

        # Get API endpoints
        stats_url = self.get_api_base(html)
        entry_url = self.get_entry_list_url(html)

        # 0. Fetch Tournament Metadata (to get name)
        tournament_name = f"Tournament {tdid}"
        try:
            # The get_data command is sent to the entry_url (n01_tournament.php)
            response = self.session.post(entry_url, params={'cmd': 'get_data'}, data=json.dumps({'tdid': tdid}))
            response.raise_for_status()
            meta_data = response.json()
            if meta_data and 'title' in meta_data:
                tournament_name = meta_data['title']
        except Exception as e:
            print(f"Failed to fetch tournament metadata: {e}")
            # Fallback to title tag if API fails
            soup = BeautifulSoup(html, 'html.parser')
            title_tag = soup.find('title')
            if title_tag:
                tournament_name = title_tag.text.strip().replace(" (Competiton stats)", "")

        # 1. Fetch Entry List (to get names)
        try:
            response = self.session.post(entry_url, params={'cmd': 'get_entry_list', 'tdid': tdid})
            response.raise_for_status()
            entry_list = response.json()
        except Exception as erro:
            # Esta mensagem é lida por quem está no painel, não por quem escreve código.
            # Antes vinha um rastro de erro de SSL inteiro, que não dizia o que fazer.
            return False, (
                f'não foi possível ler a lista de inscritos do torneio. O endereço '
                f'usado foi {entry_url} — se o N01 mudou a API de novo, é isso que '
                f'precisa ser ajustado no site. Detalhe técnico: '
                f'{type(erro).__name__}: {erro}'
            )

        # Map ID -> Name
        # entry_list is a list of objects: [{"tpid": "...", "name": "..."}]
        player_map = {p['tpid']: p['name'] for p in entry_list if 'tpid' in p}

        # 2. Fetch Stats
        # Try 'stats_list' (Team) first, if empty try 'player_stats_list'
        # But based on JS, it depends on 'team' flag. Let's try both or check which one returns data.
        stats_data = {}
        try:
            # Try stats_list first
            response = self.session.post(stats_url, params={'cmd': 'stats_list', 'tdid': tdid})
            data = response.json()
            if data and isinstance(data, dict) and len(data) > 0 and 'result' not in data:
                 stats_data = data
            else:
                 # Try player_stats_list
                 response = self.session.post(stats_url, params={'cmd': 'player_stats_list', 'tdid': tdid})
                 data = response.json()
                 if data and isinstance(data, dict):
                     stats_data = data
        except Exception as erro:
            return False, (
                f'não foi possível ler as estatísticas do torneio. O endereço usado foi '
                f'{stats_url} — se o N01 mudou a API de novo, é isso que precisa ser '
                f'ajustado no site. Detalhe técnico: {type(erro).__name__}: {erro}'
            )

        if not stats_data:
            return False, "No stats data found"

        # 3. Save Data
        defaults = {
            'name': tournament_name,
            'date': timezone.now().date(),
        }
        if self.in_progress is not None:
            defaults['in_progress'] = self.in_progress

        tournament = self.find_existing_tournament()
        if tournament:
            created = False
            for campo, valor in defaults.items():
                setattr(tournament, campo, valor)
            tournament.save()
        else:
            tournament, created = TournamentResult.objects.update_or_create(
                source_url=self.url,
                defaults=defaults,
            )

        # O tipo é sugerido só quando o torneio nasce. Numa recaptura ele não é tocado,
        # porque o administrador pode ter corrigido a sugestão no painel de captura.
        if created:
            tournament.category = adivinhar_categoria(tournament_name)
            tournament.save(update_fields=['category'])

        PlayerTournamentStat.objects.filter(tournament=tournament).delete()
        champion_user = None  # rank 1
        runner_up_user = None # rank 2
        third_place_user = None # rank 3 (or first encountered rank 3)
        
        # Buffer for stats to process ranks if missing
        processed_stats = []
        has_valid_ranks = False

        for pid, stat in stats_data.items():
            if pid not in player_map:
                continue
            name = player_map[pid]
            
            # Determine rank explicitly from data
            rank_val = stat.get('rank', 0)
            if rank_val > 0:
                has_valid_ranks = True
            
            # Calculate averages and metrics for sorting/saving
            avg3 = 0.0
            if stat.get('darts', 0) > 0:
                avg3 = (stat.get('score', 0) / stat.get('darts', 0)) * 3
            
            avg1 = avg3 / 3
            
            avg9 = 0.0
            if stat.get('f9Darts', 0) > 0:
                avg9 = (stat.get('f9Score', 0) / stat.get('f9Darts', 0)) * 3

            matches_played = stat.get('match', 0)
            matches_won = stat.get('winMatch', 0)
            legs_played = stat.get('leg', 0)
            legs_won = stat.get('winLeg', 0)
            legs_diff = legs_won - (legs_played - legs_won)

            processed_stats.append({
                'pid': pid,
                'stat': stat,
                'name': name,
                'rank': rank_val,
                'avg3': avg3,
                'avg1': avg1,
                'avg9': avg9,
                'matches_played': matches_played,
                'matches_won': matches_won,
                'legs_played': legs_played,
                'legs_won': legs_won,
                'legs_diff': legs_diff
            })

        # Fallback Rank Calculation if needed
        if not has_valid_ranks and processed_stats:
            # Sort by: Matches Won (desc), Legs Won (desc), Leg Diff (desc), Avg3 (desc)
            processed_stats.sort(key=lambda x: (
                x['matches_won'], 
                x['legs_won'], 
                x['legs_diff'], 
                x['avg3']
            ), reverse=True)
            
            # Assign ranks based on sorted order
            for i, p_data in enumerate(processed_stats):
                p_data['rank'] = i + 1

        # Save to DB
        count = 0
        for p_data in processed_stats:
            rank_val = p_data['rank']
            name = p_data['name']

            # Create/find the player account for EVERY participant, not just the podium
            pin = name.replace(' ', '').lower()
            user_obj = get_or_create_player(name, pin)

            if rank_val == 1:
                champion_user = user_obj
            elif rank_val == 2:
                runner_up_user = user_obj
            elif rank_val == 3:
                if not third_place_user:
                    third_place_user = user_obj

            wr_match = f"{(p_data['matches_won']/p_data['matches_played'])*100:.1f}%" if p_data['matches_played'] > 0 else "0.0%"
            wr_leg = f"{(p_data['legs_won']/p_data['legs_played'])*100:.1f}%" if p_data['legs_played'] > 0 else "0.0%"

            PlayerTournamentStat.objects.create(
                tournament=tournament,
                player_name=name,
                player=user_obj,
                rank=rank_val if rank_val > 0 else 999,
                matches_played=p_data['matches_played'],
                matches_won=p_data['matches_won'],
                legs_played=p_data['legs_played'],
                legs_won=p_data['legs_won'],
                legs_diff=p_data['legs_diff'],
                count_100_plus=p_data['stat'].get('ton00', 0),
                count_140_plus=p_data['stat'].get('ton40', 0),
                count_170_plus=p_data['stat'].get('ton70', 0),
                count_180=p_data['stat'].get('ton80', 0),
                high_finish=p_data['stat'].get('highOut', 0),
                count_100_plus_finish=p_data['stat'].get('highOutCount', 0),
                best_leg=p_data['stat'].get('best', 0),
                worst_leg=p_data['stat'].get('worst', 0),
                win_rate_matches=wr_match,
                win_rate_legs=wr_leg,
                average_3_dart=round(p_data['avg3'], 2),
                average_1_dart=round(p_data['avg1'], 2),
                first_9_average=round(p_data['avg9'], 2)
            )
            count += 1

        # Inscritos que ainda não disputaram nenhuma partida não aparecem em
        # stats_data, só na lista de inscritos. Sem eles não dá para saber o
        # total de participantes da etapa (base do cálculo de jogos pendentes),
        # e justamente eles são os que precisam ser cobrados.
        registered_pids = {p_data['pid'] for p_data in processed_stats}
        for pid, name in player_map.items():
            if pid in registered_pids:
                continue

            pin = name.replace(' ', '').lower()
            user_obj = get_or_create_player(name, pin)

            PlayerTournamentStat.objects.create(
                tournament=tournament,
                player_name=name,
                player=user_obj,
                rank=999,
                win_rate_matches="0.0%",
                win_rate_legs="0.0%",
            )
            count += 1

        # Etapa em andamento não tem campeão: o rank 1 é só quem lidera agora.
        # O registro acontece quando a etapa for marcada como finalizada.
        if champion_user and not tournament.in_progress:
            league, division = get_or_create_league(tournament_name, timezone.now().date(), tournament.category)
            register_champion(league, division, champion_user, p2_user=runner_up_user, p3_user=third_place_user)
        return True, f"Successfully captured {count} player stats for '{tournament_name}'"


def refresh_tournaments(tournaments):
    """Recaptura torneios já existentes usando a source_url guardada em cada um.

    Evita ter que cadastrar as URLs em outro lugar: quem já foi capturado uma
    vez sabe de onde veio. Devolve (atualizados, [(nome, erro), ...]).
    """
    updated = 0
    failed = []
    for tournament in tournaments:
        success, message = N01TournamentScraper(tournament.source_url).run()
        if success:
            updated += 1
        else:
            failed.append((tournament.name, message))
    return updated, failed

