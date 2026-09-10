"""Sem modelos.

O modelo Merit (pontos por partida na liga online) foi removido junto com o fluxo de liga
online, que estava aposentado. Nada a ver com o Order of Merit dos rankings, que vive em
leagues/models.py como OrderOfMeritEntry. O app continua no INSTALLED_APPS porque a
migração que apaga a tabela precisa dele para rodar.
"""
