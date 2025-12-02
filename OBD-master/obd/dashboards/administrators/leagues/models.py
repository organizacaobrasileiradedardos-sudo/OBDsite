from django.contrib.auth.models import User
from django.db import models
from obd.dashboards.administrators.enviroments.models import Enviroment


class League(models.Model):

    LEAGUE_RUNOFF = [
        (1, 'Turno'),
        (2, 'Returno')
    ]

    LEAGUE_PHASE = [
        (0, 'Inscrição'),
        (1, 'Formação'),
        (2, 'Classificação'),
        (3, 'Playoffs'),
        (4, 'Encerrada'),
        (5, 'Anulada'),
        (6, 'Final')
    ]

    LEAGUE_SCOPE = [
        (0, 'Internacional'),
        (1, 'Continental'),
        (2, 'Nacional'),
        (3, 'Estadual'),
        (4, 'Municipal'),
        (5, 'Comemorativa')
    ]

    enviroment = models.ForeignKey(Enviroment, blank=True, null=True, on_delete=models.SET_NULL)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100, blank=False, null=True, unique=True)
    description = models.CharField(max_length=250, blank=True, null=False, default='Liga Online OBD')
    add_info = models.CharField(max_length=250, blank=True, null=False, default='Para maiores informações consulte sempre as regras.')
    slug = models.CharField(max_length=250, blank=False, null=False, unique=True)
    start_date = models.DateField(blank=False, null=False)
    end_date = models.DateField(blank=False, null=False)
    runoff = models.IntegerField(choices=LEAGUE_RUNOFF, default=1)
    phase = models.IntegerField(choices=LEAGUE_PHASE, default=0)
    scope = models.IntegerField(choices=LEAGUE_SCOPE, default=0)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField('Created at', auto_now_add=True)

    def __str__(self):
        return self.slug

    class Meta:
        verbose_name_plural = "leagues"
        verbose_name = "league"
        ordering = ('-created_at',)
