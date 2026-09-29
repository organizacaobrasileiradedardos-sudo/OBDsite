#!/usr/bin/env python3
"""Acha tags e comentários de template do Django quebrados em mais de uma linha.

Por que isso importa: o tokenizador de templates do Django é compilado **sem**
`re.DOTALL`. Uma abertura `{%`, `{{` ou `{#` que só fecha numa linha seguinte deixa de
ser reconhecida — o Django não avisa nada, e o texto cru aparece na página. Quando esse
texto contém `<a>` ou `<img>`, o navegador os interpreta como etiquetas de verdade e a
tela quebra de um jeito difícil de entender.

Já aconteceu duas vezes: com 171 tags `{% %}` estragadas por um autoformatador de HTML,
e com um comentário `{# #}` de três linhas escrito à mão, que deixou a imagem de uma
notícia sem o link dela.

Uso:  python3 ferramentas/tags_quebradas.py
"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# Pares de abertura e fechamento do template. A ordem importa: `{#` e `{%` antes de `{{`
# não é necessário porque os prefixos são distintos, mas mantemos explícito.
PARES = (('{%', '%}'), ('{{', '}}'), ('{#', '#}'))

# Só interessam os templates de verdade, que moram numa pasta `templates/`. Fora dela há
# HTML que não é template e que **cita** aberturas de tag como exemplo — a própria página
# da documentação faz isso, e sem este filtro ela aparecia como três tags quebradas.
SO_DENTRO_DE = 'templates'

IGNORAR = ('staticfiles/', 'venv_backup/', 'node_modules/', '/media/')


def aberturas_sem_fechamento(linha):
    """Devolve as aberturas desta linha que não fecham nela mesma."""
    achados = []
    for abre, fecha in PARES:
        pos = 0
        while True:
            i = linha.find(abre, pos)
            if i < 0:
                break
            j = linha.find(fecha, i + len(abre))
            if j < 0:
                achados.append(abre)
                pos = i + len(abre)
            else:
                pos = j + len(fecha)
    return achados


def main():
    arquivos = [p for p in RAIZ.rglob('*.html')
                if SO_DENTRO_DE in p.parts
                and not any(parte in str(p) for parte in IGNORAR)]
    problemas = 0
    for caminho in sorted(arquivos):
        try:
            linhas = caminho.read_text(encoding='utf-8').splitlines()
        except UnicodeDecodeError:
            continue
        for numero, linha in enumerate(linhas, start=1):
            for abre in aberturas_sem_fechamento(linha):
                problemas += 1
                relativo = caminho.relative_to(RAIZ)
                print(f'{relativo}:{numero}  abre "{abre}" e não fecha nesta linha')
                print(f'    {linha.strip()[:110]}')
    print(f'\n{len(arquivos)} template(s) analisado(s), {problemas} tag(s) quebrada(s)')
    return 1 if problemas else 0


if __name__ == '__main__':
    sys.exit(main())
