from django.contrib.auth.models import User
from django.db import models
from brasilonline.dashboards.administrators.leagues.models import League


class Division(models.Model):
    FORMATION = [
        (1, 'A'),
        (2, 'B'),
        (3, 'C'),
        (4, 'D'),
        (5, 'E'),
        (6, 'F'),
        (7, 'G'),
        (8, 'H'),
        (9, 'I'),
        (10, 'J'),
        (0, 'Formação'),
    ]

    DIVISION_PHASE = [
        (0, 'A Definir'),
        (1, 'Em Formação'),
        (2, 'Em Andamento'),
        (3, 'Fase de Playoffs'),
        (4, 'Divisão Encerrada'),
        (5, 'Divisão Anulada'),
        (6, 'Fase Final')
    ]

    league = models.ForeignKey(League, on_delete=models.CASCADE)
    players = models.ManyToManyField(User, blank=True)
    name = models.CharField(max_length=100, blank=False, null=False, unique=True)
    description = models.CharField(max_length=250, blank=True, null=False, default='Divisão OBD')
    slug = models.CharField(max_length=250, blank=False, null=False, unique=True)
    formation = models.IntegerField(choices=FORMATION, default=0)
    status = models.BooleanField(default=True)
    phase = models.IntegerField(choices=DIVISION_PHASE, default=0)
    playoffs = models.ManyToManyField(User, related_name='playoffs', blank=True)
    finals = models.ManyToManyField(User, related_name='finals', blank=True)
    third = models.ManyToManyField(User, related_name='third', blank=True)
    winners = models.ManyToManyField(User, related_name='winners', blank=True)
    created_at = models.DateTimeField('Created at', auto_now_add=True)

    def __str__(self):
        return self.slug

    class Meta:
        verbose_name_plural = "divisions"
        verbose_name = "division"
        ordering = ('-created_at',)
