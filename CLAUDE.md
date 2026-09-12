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
- **A mesma pessoa nunca disputa uma etapa com dois nomes diferentes.** Ela pode usar
  nomes diferentes em etapas diferentes, e por isso um jogador tem vários apelidos do
  N01 (`ApelidoN01`). Mas duas estatísticas do mesmo torneio para o mesmo jogador são
  sempre duplicidade, nunca resultado legítimo.
