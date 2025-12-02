from django.contrib.auth.models import User
from django.db import models
from obd.dashboards.administrators.fixtures.models import Fixture


class Validation(models.Model):
    VALIDATION = [
        (0, 'PENDENTE'),
        (1, 'VALIDADO'),
        (2, 'INVALIDO'),
        (3, 'CANCELADO'),
        (4, 'AUTOMATICO')
    ]

    fixture = models.ForeignKey(Fixture, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    validation = models.IntegerField(choices=VALIDATION, blank=False, null=False, default=0)
    comment = models.CharField(max_length=250, blank=True, null=False)
    created_at = models.DateTimeField('Created at', auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = "validations"
        verbose_name = "validation"
        ordering = ('created_at',)