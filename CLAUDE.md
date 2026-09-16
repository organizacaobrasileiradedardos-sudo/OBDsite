# OBDsite — instruções do projeto

Site da Organização Brasileira de Dardos (obdardos.com.br). Django 4.2 + PostgreSQL,
hospedado no Railway.

## Documentação

A documentação do site está em `OBD-master/documentacao/DOCUMENTACAO-OBDSITE.md`
(a versão em página é `documentacao-obdsite.html`, com o mesmo conteúdo).

**Sempre que uma alteração mudar algo descrito nessa documentação, atualize a
documentação no mesmo commit da alteração.** Não é preciso o usuário pedir.

Vale para: regra de negócio nova ou alterada, tela nova ou que mudou de endereço,
campo novo no banco, rotina operacional que passou a funcionar de outro jeito,
armadilha nova descoberta, e item da seção 10 (Pontos em aberto) que foi resolvido.

Não vale para: ajuste de cor, tamanho ou espaçamento, e correção de bug que não muda
a regra. Documentação que muda à toa perde a confiança de quem lê.

**Atualize também a data de revisão do cabeçalho**, em dois lugares: a linha
`Última revisão:` no `.md` e o campo `<b>Revisão</b>` no `.html`. Uma data velha faz o
leitor duvidar do resto do documento.

Ao atualizar, avise no fim da resposta qual seção foi mexida, porque o usuário mantém
uma cópia desse arquivo como conhecimento de um Projeto no Claude Desktop e precisa
subir a versão nova de lá.

## Comunicação

O usuário é Guilherme Altomar, administrador da OBD, e não é desenvolvedor.
Responda sempre em português. Explique o "porquê" das coisas, não só o "o quê".

## Deploy

Commit direto na `main` e `git push`. O Railway publica sozinho. O `Procfile` roda
`collectstatic` e `migrate` a cada deploy, então migrações sobem automaticamente.

## Ao remover código

Apagar uma consulta e esquecer a variável dela no dicionário de contexto derruba a página
com `NameError`, e nem o `manage.py check` nem a compilação dos templates pegam isso —
só quem abre a página. Já aconteceu: o perfil público ficou dando erro 500 depois de uma
limpeza.

Depois de remover qualquer código, rode `python3 ferramentas/nomes_indefinidos.py` na
pasta `OBD-master`. Ele aponta nomes que são usados mas ninguém define.

## Se o site sair do ar depois de um deploy

O redirecionamento de http para https depende do `SECURE_PROXY_SSL_HEADER`. Se o site
entrar em laço de redirecionamento, ponha **`SECURE_SSL_REDIRECT=False`** nas variáveis
do Railway e reinicie — desliga na hora, sem precisar de deploy.

## Armadilhas que já causaram problema

- **Não deixe autoformatador de HTML rodar nos templates.** O tokenizador do Django é
  compilado sem `re.DOTALL`: uma tag `{% %}` quebrada em duas linhas deixa de ser tag
  e derruba a página. Já aconteceu com 171 tags e 7 telas fora do ar.
- **`TournamentResult.date` é reescrito a cada recaptura.** Para ordem cronológica
  confiável use `created_at`.
- **Duas folhas de estilo se atropelam** (`dartboard-theme.css` clara e `style.css`
  escura), produzindo texto escuro sobre fundo escuro. Escope as regras de CSS
  (`.card .card-title`, nunca `.card-title` solto).
- **O fim de uma etapa da Liga Nacional não pode ser deduzido dos dados.** Uma etapa
  pode terminar com jogos pendentes. Quem encerra é o administrador, pelo campo
  `in_progress`.
- **O endereço do admin do Django vem da variável `ADMIN_URL`**, não é fixo. Nunca
  escreva `/admin/` à mão no código: o limite de tentativas acha a tela de entrada por
  `reverse('admin:login')`, e fixar o caminho faria o admin perder essa proteção em
  silêncio se o endereço mudasse.
- **`authenticate()` tem que receber o `request`.** Sem ele o Django dispara
  `user_login_failed` com `request=None`, e o limite de tentativas de login não conta a
  tentativa. Foi assim que a primeira versão dessa proteção não funcionou.
- **E-mail de usuário nunca copia a caixa da OBD.** Envie por
  `obd/core/emails.py`: `enviar_para_usuario` vai só para o destinatário (é por ali que
  passam o link de redefinição e a senha do cadastro), e `avisar_administracao` avisa a
  OBD com um texto próprio, sem nada que dê acesso a uma conta.
- **`DEFAULT_FROM_EMAIL` é o remetente, não a caixa da OBD.** É `noreply@obdardos.com.br`
  e não tem caixa postal. Avisos para a administração vão para `settings.EMAIL_AVISOS`.
  Mandar para o remetente faz a mensagem sumir sem erro e sem rastro — já aconteceu.
- **A mesma pessoa nunca disputa uma etapa com dois nomes diferentes.** Ela pode usar
  nomes diferentes em etapas diferentes, e por isso um jogador tem vários apelidos do
  N01 (`ApelidoN01`). Mas duas estatísticas do mesmo torneio para o mesmo jogador são
  sempre duplicidade, nunca resultado legítimo.
