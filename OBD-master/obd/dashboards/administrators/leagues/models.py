from django.contrib.auth.models import User
from django.db import models


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

class OrderOfMeritEntry(models.Model):
    """Registra o valor em R$ que um jogador recebeu em uma etapa (League) da Liga Nacional."""

    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='order_of_merit_entries')
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='order_of_merit_entries')
    position_in_stage = models.IntegerField('Posição na Etapa', blank=True, null=True)
    value = models.DecimalField('Valor (R$)', max_digits=8, decimal_places=2, default=0)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name_plural = "order of merit entries"
        verbose_name = "order of merit entry"
        unique_together = ('player', 'league')
        ordering = ('-league__start_date',)

    def __str__(self):
        return f"{self.player} - {self.league.name}: R$ {self.value}"

class NationalRankingEntry(models.Model):
    """Registra os pontos que um jogador recebeu em uma etapa (League) do Ranking Nacional OBD."""

    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='national_ranking_entries')
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='national_ranking_entries')
    position_in_stage = models.IntegerField('Posição na Etapa', blank=True, null=True)
    points = models.DecimalField('Pontos', max_digits=8, decimal_places=2, default=0)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name_plural = "national ranking entries"
        verbose_name = "national ranking entry"
        unique_together = ('player', 'league')
        ordering = ('-league__start_date',)

    def __str__(self):
        return f"{self.player} - {self.league.name}: {self.points} pts"       