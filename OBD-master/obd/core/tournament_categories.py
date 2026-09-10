"""Tipos de torneio da OBD.

Definição única das categorias usadas no Hall dos Campeões e no painel de captura.
O tipo de cada torneio é um campo de verdade no banco (``TournamentResult.category``),
escolhido pelo administrador. O palpite pelo nome, aqui embaixo, serve apenas como
valor inicial: no momento em que um torneio é capturado pela primeira vez, e na
migração que preencheu os torneios que já existiam.

Este módulo não importa nada do projeto de propósito, para poder ser usado tanto pelos
models quanto pelas migrações sem risco de importação circular.
"""
import re
import unicodedata
from collections import OrderedDict

LIGA_NACIONAL = 'liga-nacional'
TOUR = 'tour'
CIRCUITO_NACIONAL = 'circuito-nacional'
OUTROS = 'outros'

# A ordem deste dicionário é a ordem em que as categorias aparecem no Hall dos Campeões, e
# `cor` escolhe qual das variantes de cabeçalho do tema cada uma usa (vermelho, verde,
# dourado e preto — as quatro que já existem em dartboard-theme.css).
# `prioridade` só é usada pelo palpite: define qual padrão vence quando um nome casa com
# mais de um. "liga nacional" e "circuito nacional" ganham de "tour" por serem mais
# específicas.
CATEGORIAS = OrderedDict([
    (LIGA_NACIONAL, {
        'label': 'Liga Nacional OBD',
        'cor': 'gold',
        'icone': 'bi-trophy-fill',
        'padrao': re.compile(r'liga\s+nacional'),
        'prioridade': 1,
    }),
    (TOUR, {
        'label': 'Tour OBD',
        'cor': 'green',
        'icone': 'bi-globe2',
        'padrao': re.compile(r'\btour\b'),
        'prioridade': 3,
    }),
    (CIRCUITO_NACIONAL, {
        'label': 'Circuito Nacional OBD',
        'cor': 'red',
        'icone': 'bi-geo-alt-fill',
        'padrao': re.compile(r'circuito\s+nacional'),
        'prioridade': 2,
    }),
    (OUTROS, {
        'label': 'Outros Torneios',
        'cor': 'black',
        'icone': 'bi-star-fill',
        'padrao': None,  # é o destino de quem não casa com nenhum padrão
        'prioridade': 99,
    }),
])

CHOICES = [(slug, cfg['label']) for slug, cfg in CATEGORIAS.items()]


def sem_acento(texto):
    """Minúsculas e sem acento, para comparar nomes sem depender de como foram digitados."""
    decomposto = unicodedata.normalize('NFKD', texto or '')
    return ''.join(c for c in decomposto if not unicodedata.combining(c)).lower()


def adivinhar_categoria(nome_torneio):
    """Chuta a categoria a partir do nome do torneio.

    Usado só para sugerir um valor inicial. Quem manda é o campo escolhido pelo
    administrador no painel de captura.
    """
    texto = sem_acento(nome_torneio)
    ordenadas = sorted(CATEGORIAS.items(), key=lambda item: item[1]['prioridade'])
    for slug, cfg in ordenadas:
        if cfg['padrao'] and cfg['padrao'].search(texto):
            return slug
    return OUTROS


def label(slug):
    """Nome de exibição de uma categoria, tolerante a valor desconhecido no banco."""
    return CATEGORIAS.get(slug, CATEGORIAS[OUTROS])['label']
