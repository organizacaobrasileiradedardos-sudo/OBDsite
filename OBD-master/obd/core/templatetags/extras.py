"""Filtros de template do site."""
from django import template
from django.template.defaultfilters import linebreaks, urlize
from django.utils.safestring import mark_safe

register = template.Library()

# Marcas que denunciam um texto vindo do editor visual. Notícias escritas antes do
# editor existir são texto puro, com quebras de linha e nenhuma dessas marcas.
_MARCAS_DE_HTML = ('<p', '<br', '<ul', '<ol', '<li', '<strong', '<b>', '<em', '<i>',
                   '<u>', '<a ', '<h1', '<h2', '<h3')


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
        return mark_safe(texto)

    # O urlize devolve HTML já escapado e seguro; o linebreaks apenas quebra em
    # parágrafos. O mark_safe no fim é necessário porque linebreaks devolve texto
    # comum, e sem ele o Django escaparia tudo de novo — a página mostraria as
    # etiquetas `<p>` em vez dos parágrafos.
    return mark_safe(linebreaks(urlize(texto)))
