from django.contrib.auth.models import User
from django.db import models
from brasilonline.dashboards.administrators.fixtures.models import Fixture


class Merit(models.Model):

    TYPE = [
        (0, 'DERROTA'),
        (1, 'EMPATE'),
        (2, 'VITORIA'),
        (3, 'CAMPEAO'),
        (4, 'VICE'),
        (5, 'TERCEIRO'),
        (6, 'AUTO'),
        ]

    player = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Fixture, on_delete=models.CASCADE)
    points = models.IntegerField(default=0, blank=True, null=False)
    type = models.IntegerField(default=6, choices=TYPE, blank=True, null=False)
    enabled = models.BooleanField(default=False)
    comment = models.CharField(max_length=200, blank=True, null=False)
    created_at = models.DateTimeField('Created at', auto_now_add=True)

    class Meta:
        verbose_name_plural = "merits"
        verbose_name = "merit"
        ordering = ('-created_at',)