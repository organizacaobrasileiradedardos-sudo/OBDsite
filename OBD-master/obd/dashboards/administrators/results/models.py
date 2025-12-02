from django.contrib.auth.models import User
from django.db import models
from obd.dashboards.administrators.fixtures.models import Fixture
from django.core.exceptions import ValidationError


def image_file_path(instance, filename):
    ext = filename.split('.')[-1]
    return f'{instance.id}.{ext}'

def validate_file_extension(value):
    if not value.lower()[-3:] not in ['png, jpg']:
        raise ValidationError('Unsupported file extension.')

class Result(models.Model):

    VALIDATION = [
        (0, 'PENDENTE'),
        (1, 'VALIDADO'),
        (2, 'INVALIDO'),
        (3, 'CANCELADO'),
        (4, 'AUTO'),
    ]

    FINAL = [
        (0, 'Derrota'),
        (1, 'Triunfo'),
        (2, 'Empate'),
        (3, 'Cancelado'),
        (4, 'AUTO'),
    ]

    fixture = models.ForeignKey(Fixture, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    validation = models.IntegerField(choices=VALIDATION, blank=False, null=False, default=4)
    enabled = models.BooleanField(default=False)
    walkover = models.BooleanField(default=False)
    on_date = models.DateField(blank=True, null=True)
    final = models.IntegerField(choices=FINAL, blank=False, null=False, default=4)
    points = models.IntegerField(blank=False, null=False, default=0)
    sets = models.IntegerField(blank=False, null=False, default=0)
    legs = models.IntegerField(blank=False, null=False, default=0)
    legs_diff = models.IntegerField(blank=False, null=False, default=0)
    highest_out = models.IntegerField(blank=False, null=False, default=0)
    best_leg = models.IntegerField(blank=False, null=False, default=0)
    ton = models.IntegerField(blank=True, null=False, default=0)
    ton40 = models.IntegerField(blank=True, null=False, default=0)
    ton70 = models.IntegerField(blank=True, null=False, default=0)
    ton80 = models.IntegerField(blank=True, null=False, default=0)
    average = models.FloatField(blank=False, null=False, default=0)
    darts9 = models.FloatField(blank=True, null=False, default=0)
    darts3 = models.FloatField(blank=True, null=False, default=0)
    comment = models.CharField(max_length=250, blank=True, null=False)
    created_at = models.DateTimeField('Created at', auto_now_add=True)

    def __str__(self):
        return str(self.id)



