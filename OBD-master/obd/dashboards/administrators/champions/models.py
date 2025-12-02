from django.contrib.auth.models import User
from django.db import models
from obd.dashboards.administrators.leagues.models import League
from obd.dashboards.administrators.divisions.models import Division


class Champion(models.Model):
    MODE = [
        (1, 'Pontos Corridos'),
        (2, 'Mata-Mata'),
        (3, 'Copa'),
    ]

    league = models.ForeignKey(League, on_delete=models.DO_NOTHING, blank=False)
    division = models.ForeignKey(Division, on_delete=models.DO_NOTHING, blank=False)
    mode = models.IntegerField(choices=MODE, default=1)
    p1 = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='p1', blank=True, null=True)
    p2 = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='p2', blank=True, null=True)
    p3 = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='p3', blank=True, null=True)
    p4 = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='p4', blank=True, null=True)
    created_at = models.DateTimeField('Created at', auto_now_add=True)

    class Meta:
        verbose_name_plural = "champions"
        verbose_name = "champion"
        ordering = ('-created_at',)
