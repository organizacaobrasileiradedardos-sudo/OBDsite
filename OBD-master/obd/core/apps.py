from django.apps import AppConfig
from pathlib import Path


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'obd.core'
    path = Path(__file__).resolve().parent

    def ready(self):
        # Importa por efeito colateral: é aqui que os receptores de sinal do limite
        # de tentativas de login se registram. Sem isto eles nunca são chamados.
        from obd.core import seguranca  # noqa: F401
