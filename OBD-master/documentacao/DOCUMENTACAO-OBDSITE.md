# Documentação do site da OBD

**Organização Brasileira de Dardos — obdardos.com.br**

Última revisão: 10 de setembro de 2026.

Este documento descreve como o site funciona por dentro: quais telas existem, o que
cada uma faz, de onde vêm os números que elas mostram e quais regras de negócio estão
embutidas no código. Ele foi escrito para duas situações: consulta humana e uso como
base de conhecimento para o Claude.

---

## 1. Visão geral

O site é uma aplicação **Django 4.2** em Python, hospedada no **Railway**, com banco
**PostgreSQL**. Ele tem três finalidades:

1. **Vitrine pública** — notícias, eventos, documentos, rankings, hall dos campeões e
   perfis de jogadores, tudo acessível sem login.
2. **Área do jogador** — perfil, foto, histórico de torneios, senha.
3. **Área administrativa** — captura automática de estatísticas do N01 Darts,
   importação de planilhas de ranking, e gestão de ligas.

O ponto que mais distingue este site de um site institucional comum é que **os dados
esportivos não são digitados à mão**. Eles são raspados da plataforma N01 Darts por um
robô, ou importados de planilhas Excel. Boa parte da complexidade do sistema existe para
resolver um único problema difícil: *descobrir se o "Bruno Amaro" que apareceu no N01 é o
mesmo "Bruno Amaro" que já tem conta no site.* A seção 6 trata disso em detalhe.

### Tecnologias

| Camada | Escolha |
|---|---|
| Framework | Django 4.2.11, Python 3.9 |
| Banco | PostgreSQL (Railway) |
| Servidor | gunicorn |
| Arquivos estáticos | whitenoise (`CompressedManifestStaticFilesStorage`) |
| Imagens enviadas | Cloudinary |
| E-mail | Resend |
| Front-end | Bootstrap 5 + Bootstrap Icons, CSS próprio |
| Calendário | FullCalendar 5.11.3 |
| Raspagem | requests + BeautifulSoup |
| Planilhas | pandas + openpyxl |
| Analytics | Umami (auto-hospedado no Railway) |
| Monitoramento | Scout APM |

### Por que Cloudinary

O sistema de arquivos do Railway é **efêmero**: tudo que for gravado em disco desaparece
no próximo deploy. Por isso nenhuma imagem enviada por formulário pode ser guardada
localmente. Toda foto de notícia, de galeria e de perfil vai para o Cloudinary, e o banco
guarda apenas a referência. Isso não é uma preferência estética — é uma necessidade da
hospedagem.

---

## 2. Estrutura do projeto

```
obd/
├── settings.py, urls.py, wsgi.py      configuração e rotas raiz
├── core/                              o site público
│   ├── models.py                      Event, News, NewsImage, Document,
│   │                                  TournamentResult, PlayerTournamentStat
│   ├── views.py                       home, rankings públicos, notícias,
│   │                                  documentos, eventos, painel Liga Nacional
│   ├── obdlib/webscraping/n01.py      o robô de captura do N01
│   ├── management/commands/           tarefas de linha de comando (agendamento)
│   └── templates/                     os 34 templates do site inteiro
├── dashboards/
│   ├── administrators/                área do administrador
│   │   ├── views.py                   captura, importações, mesclagem
│   │   ├── leagues/                   League, OrderOfMeritEntry,
│   │   │                              NationalRankingEntry
│   │   ├── divisions/, fixtures/,
│   │   │   results/, champions/       modelo antigo de liga online
│   │   └── enviroments/
│   └── players/                       área do jogador
│       ├── views.py                   login, senha, painel
│       ├── profiles/                  Profile (inclui o campo `nakka`)
│       ├── stats/, merits/, validations/
├── subscriptions/                     cadastro de novo usuário
└── updates/
```

**Todos os 34 templates ficam numa única pasta**, `obd/core/templates/`, mesmo os que
pertencem a outras áreas. Não há subpastas por app.

---

## 3. Mapa de telas

### 3.1 Área pública (sem login)

| URL | View | Template | O que faz |
|---|---|---|---|
| `/` | `core.views.index` | `index.html` | Home: estatísticas gerais, campeões da etapa, notícias e documentos recentes |
| `/obd/players/` | `public_players` | `user_public_players.html` | Lista de jogadores; o card inteiro é clicável e leva ao perfil |
| `/profile/public/<pin>/show/<nome>-<sobrenome>/` | `profiles.publicprofile` | `user_public_profile.html` | Perfil público do jogador |
| `/profile/claim/<pin>/` | `profiles.claim_account` | `claim_account.html` | "É você? Reivindique" — assume um cadastro provisório |
| `/dashboard/public/obd/merit/ranking/view` | `leagues.orderofmerit` | `user_public_order_of_merit.html` | Order of Merit (premiação em R$) |
| `/dashboard/public/obd/national/ranking/view` | `leagues.national_ranking` | `user_public_national_ranking.html` | Ranking Nacional (pontos) |
| `/obd/league/all/champions` | `champions.champions` | `user_public_all_champs.html` | Hall dos Campeões, separado por tipo de torneio (ver 5.7) |
| `/eventos/` | `events_list` | `events.html` | Calendário de eventos |
| `/noticias/` | `news_list` | `news.html` | Lista de notícias |
| `/noticias/<pk>/` | `news_detail` | `news_detail.html` | Notícia completa com galeria |
| `/documentos/` | `documents_list` | `documents.html` | Regras, estatuto e outros PDFs |
| `/obd/` | `obd_organization` | `obd_organization.html` | Página institucional |
| `/subscribe/` | `subscriptions.subscribe` | `subscription.html` | Cadastro de novo usuário |

### 3.2 Restrito a quem tem login

| URL | View | Template | Observação |
|---|---|---|---|
| `/obd/leagues/` | `public_leagues` | `user_public_leagues.html` | **Painel da Liga Nacional.** Único item do menu público que exige login |

Quem não estiver logado é levado para a tela de login com a mensagem *"Página de acesso
exclusivo para usuários logados. Crie seu login ou faça o login"*. Ver seção 5.3.

### 3.3 Área do jogador

| URL | View | Template |
|---|---|---|
| `/dashboard/players/dashboard/player/login` | `loginuser` | `login.html` |
| `.../login/recovery/password` | `recoverypassword` | `login.html` |
| `.../login/recovery/password/confirm/<uidb64>/<token>` | `password_reset_confirm` | `password_reset_confirm.html` |
| `/dashboard/players/dashboard/player/` | `dashboard` | `dashuser.html` |
| `/dashboard/profiles/dashboard/player/profile/view/` | `profiles.config` | `profile_view.html` |

A área do jogador tem hoje apenas essas telas. Inscrição em liga, histórico de partidas e
geração de relatório saíram junto com o módulo legado (seção 8).

### 3.4 Área do administrador

| URL | View | Template | O que faz |
|---|---|---|---|
| `/dashboard/administrators/dashboard/admin/` | `dashboard` | `dashadmin.html` | Painel inicial |
| `.../admin/players/view` | `members` | `admin_user_list.html` | Lista de associados |
| `.../admin/scraping/` | `scraping_dashboard` | `scraping_dashboard.html` | **Captura de dados N01** |
| `.../admin/scraping/run/` | `run_capture` | — | Executa uma captura |
| `.../admin/scraping/prize/<id>/` | `update_tournament_prize` | — | Grava a premiação de torneio avulso |
| `.../admin/scraping/andamento/<id>/` | `update_tournament_progress` | — | Liga/desliga "em andamento" |
| `.../admin/scraping/tipo/<id>/` | `update_tournament_category` | — | Grava o tipo do torneio |
| `.../admin/scraping/excluir/<id>/` | `delete_tournament` | — | Apaga uma captura |
| `.../admin/order-of-merit/` | `order_of_merit_dashboard` | `order_of_merit_dashboard.html` | Importar Order of Merit |
| `.../admin/order-of-merit/import/` | `import_order_of_merit` | `import_review.html` | Tela de conferência |
| `.../admin/order-of-merit/import/confirmar/` | `confirm_order_of_merit` | — | Grava o que foi conferido |
| `.../admin/national-ranking/...` | idem | idem | Mesmo fluxo, para pontos |
| `.../admin/merge-players/` | `merge_players_dashboard` | `merge_players_dashboard.html` | Mesclar cadastros duplicados |

O acesso a tudo aqui é controlado por dois decoradores empilhados:

```python
@login_required
@permission_required('profiles.has_admin_role', raise_exception=True)
```

`has_admin_role` é uma permissão personalizada declarada no `Meta` do modelo `Profile`.
Não basta ser `is_staff` do Django.

### 3.5 O que foi removido

Todo o modelo antigo de liga online foi retirado do código (seção 8). Saíram 13 telas,
duas camadas de views inteiras e as rotas correspondentes:

| Removido | O que era |
|---|---|
| `admin_adm_leagues.html`, `admin_players_leagues.html` | Gestão de ligas e jogadores da liga |
| `admin_ranking_show.html`, `user_ranking_show.html` | Ranking de uma divisão |
| `user_open_leagues.html` | Inscrição em liga |
| `user_result_submit.html` | Lançamento de resultado pelo jogador |
| `user_matches_show.html`, `user_all_games.html`, `user_audit_matches.html` | Minhas partidas e relatórios |
| `user_public_match_result.html` | Relatório de partida |
| `create_league.html`, `user_public_ranking_show.html`, `user_public_players_leagues.html` | Criar liga e páginas públicas de liga/divisão |
| `results/views.py`, `results/urls.py`, `results/forms.py` | Lançamento e validação de resultado |
| `fixtures/views.py`, `fixtures/urls.py`, `fixtures/forms.py` | Tabela de confrontos |
| `core/obdlib/fixturing.py` | Gerador de confrontos todos-contra-todos |
| `leagues/forms.py` | Formulário de criação de liga |
| `bkp_views_2.py`, `bkp__views__.py` | Cópias de segurança antigas |

De `leagues/views.py` sobraram **duas** funções: `orderofmerit` e `national_ranking`, os
dois rankings públicos. De `players/views.py` saíram inscrição, histórico e relatórios.

Saíram também os atalhos que apontavam para essas telas: três na barra lateral do jogador
(*Meus Torneios*, *Ver meu histórico*, *Gerar relatório*) e um na do administrador
(*Backup de Resultados*), além da fila de validação de partidas no painel do
administrador.

**Computação morta que saiu junto.** A tela inicial calculava, a cada carregamento,
agregados de partidas e resultados, contagens de fase de liga e um bloco inteiro de
estatísticas por torneio — **nada disso era exibido**. O template não usava nenhuma
dessas variáveis. O mesmo valia para uma consulta de partidas no perfil público.

## 4. Modelo de dados

### 4.1 Os modelos que importam hoje

**`TournamentResult`** — um torneio capturado do N01. **Atenção:** na Liga Nacional, cada
divisão é um `TournamentResult` separado. Uma etapa com 4 divisões gera 4 registros.

| Campo | Observação |
|---|---|
| `name` | Ex: `3ª ETAPA LIGA NACIONAL OBD 2026 - DIVISÃO A` |
| `source_url` | URL do N01 de onde veio |
| `date` | **Regravado com "hoje" a cada recaptura** — não serve para ordenar |
| `created_at` | Primeira captura; nunca muda. É o campo confiável para ordenar |
| `prize_value` | Só para torneios avulsos (ver 5.2) |
| `in_progress` | Etapa ainda em disputa (ver 5.4) |
| `category` | Tipo do torneio, que define o bloco do Hall dos Campeões (ver 5.7) |

**`PlayerTournamentStat`** — a linha de um jogador num torneio: `rank`, partidas, legs,
médias, contagens de 100+/140+/170+/180, melhor leg, maior fechamento.
`tournament` é `CASCADE`; `player` é `SET_NULL`.

**`League`** — no uso atual, **uma etapa de ranking**, não uma liga. Cada linha de
cabeçalho de planilha importada vira uma `League`. Campo `scope` distingue Order of Merit
de Ranking Nacional. O campo `category` guarda o tipo de torneio e é o que manda no Hall
dos Campeões (ver 5.7).

**`OrderOfMeritEntry`** — valor em R$ de um jogador numa etapa.
`unique_together = ('player', 'league')`.

**`NationalRankingEntry`** — pontos de um jogador numa etapa. Mesma restrição.

**`Profile`** — extensão do `User` do Django. Campos importantes:

| Campo | Para que serve |
|---|---|
| `nakka` | **O apelido do jogador no N01.** A chave que liga a conta do site à identidade dele no N01. Obrigatório no formulário de perfil e validado como único |
| `pin` | Identificador usado nas URLs públicas |
| `is_verified` | `False` = cadastro provisório criado por robô/importação, ainda não reivindicado |
| `photo` | Foto do jogador |

**`News`, `NewsImage`, `Document`, `Event`** — conteúdo editorial, alimentado pelo admin
do Django.

### 4.2 Relações principais

```
User ──1:1── Profile  (nakka, pin, is_verified)
 │
 ├──1:N── PlayerTournamentStat ──N:1── TournamentResult
 ├──1:N── OrderOfMeritEntry     ──N:1── League
 └──1:N── NationalRankingEntry  ──N:1── League

News ──1:N── NewsImage
```

### 4.3 Cuidado: dois modelos chamados `Event`

Existem **dois** modelos com esse nome:

- `obd/core/models.py` → `Event` — **este é o usado**, alimenta o calendário
- `obd/dashboards/administrators/events/models.py` → `Event` — legado, não usado

Ao mexer em eventos, confirme que está no `core`.

---

## 5. Regras de negócio

Esta é a seção mais importante do documento. São as decisões que não dá para deduzir
lendo o código superficialmente.

### 5.1 Ranking Nacional: só os 8 melhores resultados

Um jogador que participa de mais de 8 etapas **não soma tudo**. Apenas os 8 maiores
resultados entram no total; os demais aparecem na tabela riscados em cinza.

```python
counted_league_ids = {
    league_id for league_id, _ in sorted(
        values_by_league.items(), key=lambda item: item[1], reverse=True
    )[:NATIONAL_RANKING_BEST_OF]
}
```

**Desempate é alfabético.** Quando dois jogadores têm o mesmo total, a ordem é pelo nome:

```python
ranking.sort(key=lambda x: (-x['total'],
                            x['player'].first_name.lower(),
                            x['player'].last_name.lower()))
```

A colocação exibida respeita empates de verdade: 1º, 2º, 2º, 4º — não 1º, 2º, 3º, 4º.

### 5.2 Premiação distribuída: duas fontes que não podem se somar duas vezes

O número "Premiação Distribuída" da home vem de **duas** origens:

1. `OrderOfMeritEntry.value` — os valores da Liga Nacional, importados por planilha.
2. `TournamentResult.prize_value` — preenchido à mão, apenas para **torneios avulsos**
   (o Tour Online, por exemplo, que distribuiu R$ 400,00 por etapa e não tem Order of
   Merit).

```python
obd_numbers['prize_total'] = order_of_merit_prize_total + standalone_prize_total
```

**Regra operacional:** nunca preencha `prize_value` numa etapa da Liga Nacional. O valor
dela já entra pelo Order of Merit, e preencher os dois conta em dobro. O próprio campo
avisa isso no `help_text`.

### 5.3 Painel da Liga Nacional

A tela `/obd/leagues/` mostra, por divisão: jogos realizados, 180's, maior fechamento,
melhor leg, e um banner de jogos pendentes.

**Qual etapa aparece**, em ordem de prioridade:

1. A etapa pedida na URL (`?etapa=...`, vinda do combobox);
2. senão, a etapa **em andamento**, se houver;
3. senão, a **última concluída**.

**Ordenação por `created_at`, não por `date`.** Este é um detalhe que já causou confusão:
o campo `date` é reescrito com a data de hoje a cada recaptura, então após o agendamento
rodar todas as etapas parecem ser de hoje. `created_at` é `auto_now_add` e nunca muda.

**Jogos pendentes** são calculados assumindo turno único, todos contra todos:

```python
possible = entrants * (entrants - 1) // 2
played   = sum(s.matches_played for s in stats) // 2   # cada jogo conta 2x
pending  = max(possible - played, 0)
```

> **Regra de negócio importante:** o número de jogos pendentes **não** indica que a etapa
> acabou. Uma etapa da Liga Nacional pode ser encerrada mesmo com jogos pendentes. Foi
> justamente por isso que o campo `in_progress` foi criado — o fim de uma etapa é uma
> decisão do administrador, não algo dedutível dos dados.

### 5.4 O sinalizador `in_progress`

Enquanto uma etapa está marcada como em andamento:

- o campeão **não** é registrado no Hall dos Campeões (o rank 1 é só o líder do momento);
- a etapa **não** aparece nos campeões da tela inicial;
- ela **não** conta em "Torneios Realizados no ano";
- ela aparece no painel da Liga Nacional e é ela que o agendamento recaptura.

Quando o administrador desmarca, o campeão é registrado **naquele momento**, a partir dos
dados já gravados — não é preciso recapturar:

```python
if was_in_progress:
    champion = register_champion_from_tournament(tournament)
```

E o caminho inverso também limpa: **marcar uma etapa como em andamento apaga o campeão
que estivesse registrado para ela**. Isso importa porque o registro do campeão é feito
com `get_or_create` e, antes, nada o apagava — bastava a etapa ter sido capturada uma vez
sem a marcação para o campeão ficar no Hall para sempre, mesmo depois de a etapa voltar a
ficar em disputa.

Como reforço, o Hall dos Campeões também **exclui da tela** os campeões de qualquer etapa
que esteja em andamento, mesmo que o registro ainda exista no banco.

### 5.5 Eventos em andamento no calendário

Um evento que começou no passado e ainda não terminou é um evento **futuro**, não passado.
A lógica considera `end_date` quando ele existe:

```python
still_upcoming = Q(end_date__isnull=False, end_date__gte=now) | Q(end_date__isnull=True, event_date__gte=now)
already_past   = Q(end_date__isnull=False, end_date__lt=now)  | Q(end_date__isnull=True, event_date__lt=now)
```

Cada evento recebe uma cor distinta de uma paleta fixa (`EVENT_COLOR_PALETTE`), para que
dois eventos no mesmo dia sejam distinguíveis. Não há ícones no calendário.

### 5.6 O campo "Ativo" das notícias

`News.is_active = False` **esconde a notícia do site** sem apagá-la. É o jeito de tirar
algo do ar preservando o registro.

### 5.7 Categorias do Hall dos Campeões

O Hall dos Campeões separa os títulos em três categorias, cada uma expandindo ao ser
clicada. **A página abre com todas fechadas** — a contagem no cabeçalho já diz o que existe
dentro de cada uma, e quem escolhe o que abrir é o usuário. As categorias são:

- **Liga Nacional OBD**
- **Tour OBD**
- **Circuito Nacional OBD**

**O tipo é um campo de verdade no banco, e mora em dois lugares.** `TournamentResult.category`
é onde o administrador escolhe, na coluna *Tipo de Torneio* do painel de captura.
`League.category` é o que o Hall dos Campeões realmente lê, porque `Champion` aponta para
`League` e não para o torneio.

Ao salvar o tipo no painel de captura, o valor é repassado para a liga de mesmo nome. E
quando um campeão é registrado, a liga nasce já com o tipo do torneio.

O palpite pelo nome existe, mas só como **valor inicial**: quando um torneio é capturado
pela primeira vez, e na migração que preencheu os torneios que já existiam. Depois disso,
quem manda é o campo.

| Categoria | Cor | Palpite inicial quando o nome contém |
|---|---|---|
| Liga Nacional OBD | dourado | `liga nacional` |
| Tour OBD | verde | a palavra `tour` isolada |
| Circuito Nacional OBD | vermelho | `circuito nacional` |
| Outros Torneios | preto | nenhum dos anteriores |

Cada categoria tem uma cor, usada no cabeçalho do bloco, no ícone, na contagem, na tarja
do ano e no cabeçalho de cada card de campeão. São as **quatro variantes de
`.card-header-dartboard` que o tema do site já define** — nenhuma cor foi inventada. A
troca é feita por variáveis CSS (`--cat-cor`, `--cat-fundo`), então as regras de estilo
são as mesmas para todas as categorias; só os valores mudam.

O palpite ignora maiúsculas e acentos, e testa `liga nacional` e `circuito nacional`
**antes** de `tour`, por serem mais específicas. Uma recaptura **não** mexe no tipo — se
mexesse, apagaria a correção feita à mão.

> **A quarta categoria, "Outros Torneios",** recolhe o que não é nenhum dos três — Opens,
> campeonatos avulsos, torneios comemorativos — para que nenhum campeão desapareça da
> tela. Ela só aparece quando tem alguém dentro. As três categorias da OBD aparecem
> sempre, mesmo vazias, para a tela ter estrutura previsível.

Tudo isso está definido num lugar só, `obd/core/tournament_categories.py`: os nomes das
categorias, os ícones, os padrões do palpite e a ordem de exibição. Acrescentar uma
categoria nova é acrescentar uma entrada nesse dicionário e gerar a migração do novo
valor de `choices`.

### Por que o tipo mora na liga, e não só no torneio

Esta é a parte que já deu problema na prática, e vale entender.

**O robô reescreve o nome do torneio a cada captura.** Se o organizador muda o título no
N01, `TournamentResult.name` muda junto — mas a liga continua com o nome antigo, porque
ela foi criada lá atrás. Aconteceu com o Open São Roque:

```
liga    : 'Open São Roque (SP) 2026'
torneio : 'Open São Roque 2026 - OBD 21.02.2026'
```

Enquanto o Hall procurava o tipo pelo nome do torneio, esse campeão ficava órfão e caía em
"Outros Torneios", **mesmo com o tipo certo gravado no torneio**. Nenhuma tolerância a
maiúsculas ou acentos resolveria: não são grafias diferentes, são nomes diferentes.

Guardando o tipo na própria liga, a classificação passa a não depender de nome nenhum.
Uma vez gravada, ela sobrevive a qualquer renomeação futura.

**Quando o nome da liga já divergiu**, o repasse do painel de captura não encontra a liga.
Nesse caso o site avisa na tela, e a correção é feita uma vez em `/admin/` → **Ligas**, no
campo *Tipo de Torneio*, editável direto na listagem.

Dentro de cada categoria, os títulos continuam agrupados por ano, do mais recente para o
mais antigo, e o filtro de temporada no topo da página vale para todas elas ao mesmo
tempo.

**A grade muda conforme a categoria ter divisões ou não.** Na Liga Nacional cada etapa tem
quatro divisões, cada uma com seu campeão: ali os cards ficam **4 por linha** e a linha é
quebrada a cada etapa, de modo que uma etapa nunca divide a linha com outra. Nas demais
categorias, onde cada torneio tem um campeão só, a grade é de 3 por linha, sem quebras.

Isso não depende de a etapa ter sempre quatro divisões. Os campeões são agrupados por
etapa — o nome do torneio sem o sufixo `- DIVISÃO X`, via `chave_do_evento` — e a categoria
adota o formato de etapa quando **alguma** delas tem mais de um campeão. Uma etapa com três
ou cinco divisões continua ocupando a sua própria linha.

**A contagem no cabeçalho de cada categoria diz "N títulos em M torneios", e os dois
números são diferentes de propósito.** Na Liga Nacional cada divisão tem seu próprio
campeão, então uma etapa com quatro divisões rende quatro títulos num único torneio.

Esse número também **não bate** com "Torneios Realizados" da tela inicial, e não deveria:
a home conta eventos distintos do ano corrente com as divisões agrupadas (ver 5.2 e o
`_tournament_event_key`), enquanto o Hall conta títulos de todos os anos. São medidas
diferentes da mesma realidade.

---

## 6. Identidade do jogador — o problema central

O mesmo ser humano pode aparecer de três formas:

- como **conta do site**, criada por ele mesmo no cadastro;
- como **nome no N01**, que ele digitou na plataforma de dardos;
- como **nome numa planilha** de ranking, digitado por um organizador.

Esses três nomes raramente batem. "Douglas Giordani" no N01 pode ser "Douglas Gurgel" no
site. Se o sistema errar, cria uma conta duplicada e o jogador perde o histórico.

### 6.1 A chave correta: `Profile.nakka`

O campo `nakka` guarda o apelido do jogador no N01. É **obrigatório** no formulário de
perfil e validado como único. É por ele que a busca começa:

```python
def get_or_create_player(name: str, pin: str) -> User:
    nakka = name.strip()
    if nakka:
        registered = Profile.objects.filter(nakka__iexact=nakka).first()
        if registered:
            return registered.user
    ...
```

Antes dessa correção, a busca era por `username == nome_sem_espaços`, o que falhava
sempre que o apelido do N01 não era igual ao nome de usuário. Foi a causa das
duplicidades de Bruno Amaro, Douglas Giordani e Joubert Kozak.

### 6.2 Classificação na importação de planilhas

Ao importar, cada nome é classificado em uma de cinco situações:

| Situação | Significado | Vai para |
|---|---|---|
| `nakka` | Achou pelo apelido do N01 | Reconhecidos |
| `username` | Achou pelo nome de usuário exato | Reconhecidos |
| `palpite` | Achou um parecido, começando igual | **Conferir** |
| `ambiguo` | Achou vários parecidos | **Conferir** |
| `novo` | Não achou ninguém | **Conferir** |

### 6.3 Cadastro provisório e reivindicação

Quando o sistema cria uma conta sozinho, ela nasce com `is_verified = False`. Nas
tabelas públicas ela aparece com o selo amarelo **"Não Verificado"** e o link
**"(é você? reivindique)"**, que leva a `claim_account`. Ali o jogador assume o cadastro,
e se ele já tiver outra conta os dados são mesclados.

### 6.4 Mesclagem manual

`merge_player_accounts(source_user, target_user)` migra estatísticas, entradas de ranking
e títulos de uma conta para outra e apaga a de origem. Registros que já existirem no
destino são descartados em vez de duplicados. Disponível em *Mesclar Cadastros* no painel
do administrador.

---

## 7. Rotinas operacionais

### 7.1 Capturar um torneio do N01

1. *Captura de Torneios* no menu do administrador.
2. Cole a URL do torneio no N01.
3. Marque **"Etapa em andamento"** se a etapa ainda está em disputa.
4. *Capturar Dados*.

O robô identifica o torneio pelo **`id=` da URL**, não pelo texto da URL inteira. O N01
serve o mesmo torneio em endereços diferentes (`comp.php` e `t_stats.html`); colar
qualquer um deles atualiza o mesmo registro, em vez de criar uma duplicata.

Para apagar uma captura, use o botão de lixeira no histórico. As estatísticas dos
jogadores saem junto (`on_delete=CASCADE`).

### 7.2 Atualização automática durante a etapa

O comando `python manage.py scrape_liga` recaptura **apenas as divisões da etapa em
andamento**, usando as URLs já guardadas. Ele é executado por um serviço de cron separado
no Railway. Há também um botão *"Atualizar agora"* no painel da Liga Nacional, visível só
para administradores.

Nas recapturas, o construtor do robô recebe `in_progress=None`, que significa *"não mexa
no status"*. Uma recaptura nunca encerra nem reabre uma etapa por conta própria.

### 7.3 Importar planilha de ranking

Formato esperado:

- Célula **B1**: nome da etapa
- Célula **B2**: data (DD/MM/AAAA)
- Linha 4 em diante: cabeçalho e dados, com colunas de posição, jogador e valor/pontos

O fluxo tem **dois passos**:

1. **Conferência** — a planilha é lida e cada jogador classificado. *Nada é gravado
   neste passo.* A tela mostra dois blocos: reconhecidos com certeza, e os que precisam
   da sua conferência. Para cada duvidoso você escolhe: criar cadastro novo, ignorar, ou
   vincular a um jogador existente. Marcando *"gravar apelido"*, o nome da planilha é
   gravado como `nakka` do jogador e nas próximas importações ele é reconhecido sozinho.
2. **Confirmar e gravar** — grava exatamente o que foi revisado.

A etapa é localizada por `League.objects.get_or_create(name=etapa_name)`, **comparando o
nome exato**. Um acento ou espaço diferente cria uma segunda etapa e os pontos passam a
contar duas vezes. Confira a célula B1 antes de confirmar.

Como as entradas usam `update_or_create(player, league)`, reimportar a mesma planilha com
o mesmo nome de etapa é inofensivo: reescreve as mesmas linhas com os mesmos valores.

### 7.4 Publicar uma notícia

Pelo admin do Django (`/admin/`), modelo *Notícias*. Campos: título, resumo, conteúdo
completo, imagem (upload direto, vai para o Cloudinary), link externo opcional, fonte,
data e destaque. Imagens adicionais entram como `NewsImage`. Desmarcar *Ativo* tira do ar
sem apagar.

### 7.5 Deploy

Commit direto na `main` e `git push`. O Railway detecta e publica. O `Procfile` roda:

```
python manage.py collectstatic --noinput && python manage.py migrate && gunicorn obd.wsgi
```

Ou seja, **as migrações rodam sozinhas a cada deploy**.

---

## 8. O modelo antigo de liga online (removido)

O site nasceu com um sistema completo de liga online: `League` com fases, `Division`,
`Fixture` (confrontos), `Result`, inscrição de jogadores, lançamento de resultado pelo
próprio usuário, validação pelo administrador, playoffs e finais.

**Esse fluxo foi aposentado.** Uma verificação no banco encontrou 18 divisões e **zero**
confrontos: ninguém usava havia muito tempo. Todo o código de tela foi removido
(seção 3.5).

### O que saiu do banco

Conferidas as contagens em produção — `Fixture`, `Result` e `Merit` estavam com **zero
registros** —, os três modelos foram removidos e suas tabelas apagadas por migração. Os
registros no admin do Django saíram junto.

`Validation` era um caso à parte: o app **nunca esteve no `INSTALLED_APPS`** e não tinha
migração nenhuma, então a tabela `players_validation` jamais chegou a existir. Consultá-la
dava erro de tabela inexistente. O app inteiro foi apagado, sem precisar de migração.

Os três apps (`fixtures`, `results`, `merits`) continuam no `INSTALLED_APPS` com um
`models.py` vazio: a migração que apaga a tabela só roda se o app estiver instalado.
Removê-los de vez é um passo posterior, depois que a migração tiver sido aplicada.

Dois modelos desse conjunto **continuam em uso ativo** e não podem ser removidos:

- **`League`** foi reaproveitado: hoje representa uma *etapa de ranking* importada por
  planilha, e é a ela que `Champion` e as entradas de Order of Merit e Ranking Nacional
  apontam.
- **`Division`** é destino de uma chave estrangeira obrigatória em `Champion`, e toda
  captura de torneio cria uma divisão "Principal" (`get_or_create_league`).

Por isso o nome `League` no código significa duas coisas diferentes conforme o contexto —
a armadilha que sobrou dessa história.

## 9. Convenções e armadilhas conhecidas

### 9.1 Duas folhas de estilo que se atropelam

- `dartboard-theme.css` — visual claro, cards brancos, títulos escuros
- `style.css` — tema escuro, `--card-bg: #1e293b`

Quando as duas se aplicam ao mesmo elemento, o resultado é **texto escuro sobre fundo
escuro**, praticamente invisível. Isso já apareceu em vários lugares. Ao corrigir,
**escopar a regra**: `.card .card-title`, não `.card-title` solto — um `<h2 class="card-title">`
fora de qualquer card ficaria branco sobre fundo claro.

### 9.2 Versões diferentes de Bootstrap

| Base | Bootstrap | Bootstrap Icons |
|---|---|---|
| `base.html` (público) | 5.3.3 | 1.11.3 |
| `baseuser.html` | **5.0.0-beta2** | 1.11.3 |
| `baseadmin.html` | **5.0.0-beta2** | 1.11.3 |

Os ícones já foram unificados. **O Bootstrap em si não.** Isso significa que componentes
mais novos podem se comportar de forma diferente nas telas internas. Unificar é um
trabalho pendente e de risco alto, porque afeta todas as telas administrativas de uma vez.

*Sintoma típico da versão antiga:* um ícone que não existe naquela versão renderiza um
`<i>` vazio, e o botão aparece sem nada dentro — parecendo um problema de cor.

### 9.3 O tokenizador de templates do Django não aceita quebra de linha dentro de tag

A expressão que o Django usa é compilada **sem** `re.DOTALL`:

```python
tag_re = ({%.*?%}|{{.*?}}|{#.*?#})
```

Consequência: `{% if algo %}` quebrado em duas linhas **não é reconhecido como tag** — ele
vira texto literal na página, ou derruba o template com erro 500. Um "Format Document"
do editor já inseriu quebras em 171 tags e derrubou 7 telas.

**Nunca deixe um autoformatador de HTML rodar solto nos templates.**

### 9.4 `config()` e `os.getenv()` misturados

`settings.py` usa os dois. `config()` (python-decouple) **quebra a inicialização** se a
variável não existir e não tiver default; `os.getenv()` devolve `None` silenciosamente.
Ao rodar o projeto fora do Railway é preciso fornecer todas as variáveis exigidas por
`config()`.

### 9.5 Localização de números em campos ocultos

Com `pt-br`, um `Decimal` renderizado em HTML vira `500,00`. Ao voltar pelo formulário,
`Decimal('500,00')` levanta exceção. Em campos ocultos use `{% load l10n %}` e o filtro
`|unlocalize`.

### 9.6 Datas: `date` versus `created_at`

Já dito na seção 5.3, mas vale repetir porque é a armadilha mais fácil de cair:
**`TournamentResult.date` é reescrito a cada recaptura.** Para ordenação cronológica
confiável, use `created_at`.

---

## 10. Pontos de atenção em aberto

Levantados ao longo do desenvolvimento e ainda não resolvidos:

1. **E-mail de recuperação de senha com cópia para a caixa da OBD.** Qualquer pessoa com
   acesso àquela caixa consegue redefinir a senha de qualquer jogador. É o item mais
   sério da lista.
2. **`/admin/` no caminho padrão**, sem limite de tentativas de login.
3. **Sem limitação de tentativas** na tela de login dos jogadores.
4. **Cabeçalhos de segurança HTTPS ausentes**, incluindo `SECURE_PROXY_SSL_HEADER`.
5. **Bootstrap não unificado** (seção 9.2).
6. **Apps vazios** — `fixtures`, `results` e `merits` continuam no `INSTALLED_APPS` só
   para as migrações de exclusão rodarem. Podem ser removidos num deploy seguinte.

---

## 11. Glossário

| Termo | Significado |
|---|---|
| **N01 / Nakka** | Plataforma online onde as partidas de dardos são jogadas e as estatísticas geradas |
| **nakka** (campo) | O apelido do jogador no N01, guardado no perfil. A chave de ligação entre o site e o N01 |
| **Etapa** | Uma rodada da Liga Nacional ou do circuito. No banco, uma `League` |
| **Divisão** | Subdivisão de uma etapa (A, B, C, D). Cada uma é um `TournamentResult` |
| **Order of Merit** | Ranking por premiação recebida em R$ |
| **Ranking Nacional** | Ranking por pontos, considerando os 8 melhores resultados |
| **Leg** | Uma partida individual dentro de um set |
| **180** | Pontuação máxima com três dardos |
| **Fechamento (checkout)** | Pontuação com que o jogador encerrou o leg |
| **PIN** | Identificador do jogador usado nas URLs públicas |
| **Cadastro provisório** | Conta criada automaticamente, com `is_verified = False` |
