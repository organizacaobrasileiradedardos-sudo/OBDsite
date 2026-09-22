"""Filtros de template do site."""
import re

from django import template
from django.template.defaultfilters import linebreaks, urlize
from django.utils.html import urlize as urlizar_texto
from django.utils.safestring import mark_safe

register = template.Library()

# Marcas que denunciam um texto vindo do editor visual. Notícias escritas antes do
# editor existir são texto puro, com quebras de linha e nenhuma dessas marcas.
_MARCAS_DE_HTML = ('<p', '<br', '<ul', '<ol', '<li', '<strong', '<b>', '<em', '<i>',
                   '<u>', '<a ', '<h1', '<h2', '<h3')


# Divide o HTML em pedaços alternando texto e etiqueta. O primeiro pedaço é texto, e
# daí em diante alterna: índice par é texto, ímpar é etiqueta.
_PEDACOS = re.compile(r'(<[^>]+>)')


def _transformar_enderecos_em_links(html):
    """Torna clicável um endereço digitado solto no meio do texto.

    Aplicar a conversão ao HTML inteiro estragaria o conteúdo: ela linkaria também o
    endereço que está **dentro** do `href` de um link já existente, produzindo etiquetas
    aninhadas. Por isso a conversão é feita só nos pedaços de texto, e nunca dentro de
    uma etiqueta nem entre a abertura e o fechamento de um link.
    """
    pedacos = _PEDACOS.split(html)
    dentro_de_link = False
    saida = []

    for i, pedaco in enumerate(pedacos):
        if i % 2:                       # é uma etiqueta
            minusculo = pedaco.lower()
            if minusculo.startswith('<a'):
                dentro_de_link = True
            elif minusculo.startswith('</a'):
                dentro_de_link = False
            saida.append(pedaco)
        else:                           # é texto
            # autoescape=False porque este texto já vem escapado do editor; escapar de
            # novo transformaria "&amp;" em "&amp;amp;".
            saida.append(pedaco if dentro_de_link
                         else urlizar_texto(pedaco, nofollow=True, autoescape=False))

    return ''.join(saida)


@register.filter
def conteudo_de_noticia(texto):
    """Exibe o conteúdo de uma notícia, venha ele do editor visual ou não.

    O editor grava HTML, que precisa ser exibido como formatação e não como texto. Mas
    as notícias escritas antes dele são texto puro, e exibir esse texto sem converter as
    quebras de linha juntaria todos os parágrafos num bloco só.

    Por isso os dois casos são tratados: se o texto traz marcas de HTML, vai como está;
    se não traz, recebe o tratamento antigo, que transforma quebras em parágrafos e
    endereços em links.

    **Sobre confiar no HTML:** notícia só é escrita por quem tem acesso ao admin do
    Django. Não há caminho pelo qual um visitante escreva aqui.
    """
    texto = (texto or '').strip()
    if not texto:
        return ''

    minusculo = texto.lower()
    if any(marca in minusculo for marca in _MARCAS_DE_HTML):
        return mark_safe(_transformar_enderecos_em_links(texto))

    # O urlize devolve HTML já escapado e seguro; o linebreaks apenas quebra em
    # parágrafos. O mark_safe no fim é necessário porque linebreaks devolve texto
    # comum, e sem ele o Django escaparia tudo de novo — a página mostraria as
    # etiquetas `<p>` em vez dos parágrafos.
    return mark_safe(linebreaks(urlize(texto)))
