from django.db import models
from obd.dashboards.administrators.divisions.models import Division
from django.contrib.auth.models import User


class Fixture(models.Model):

    SERVER = [
        ('WED', 'WEBCAMDARTS'),
        ('N01', 'NAKKA'),
        ('LID', 'LIDARTS'),
        ('DAC', 'DARTCONNECT'),
        ('GOP', 'GODARTSPRO'),
        ('PRE', 'PRESENCIAL'),
        ('OTH', 'OUTRO'),
        ('WO', 'WALKOVER')
    ]

    STATUS = [
        (0, 'PENDENTE'),
        (1, 'FINALIZADO'),
        (2, 'CANCELADO')
    ]

    VALIDATION = [
        (0, 'PENDENTE'),
        (1, 'VALIDADO'),
        (2, 'INVALIDO'),
        (3, 'CANCELADO')
    ]

    TYPE = [
        (0, 'NORMAL'),
        (2, 'FINAL'),
        (3, 'THIRD'),
        (4, 'BEST4'),
        (8, 'BEST8'),
        (16, 'BEST16'),
        (32, 'BEST32'),
        (64, 'BEST64'),
        (128, 'BEST128'),
        (256, 'BEST256'),
        (512, 'BEST512'),
        (1024, 'BEST1024'),
        (2048, 'BEST2048')
    ]

    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    players = models.ManyToManyField(User)
    photo = models.ImageField(default='https://res.cloudinary.com/hvnnhpdtd/image/upload/v1625926909/logo_black_gold_boa_2.png')
    status = models.IntegerField(choices=STATUS, default=0)
    submited_by = models.CharField(max_length=250, blank=True, null=False)
    on_date = models.DateField(blank=True, null=True)
    link = models.CharField(max_length=250, blank=True, null=False)
    server = models.CharField(max_length=250, choices=SERVER, default='OTH')
    validation = models.IntegerField(choices=VALIDATION, default=0)
    enabled = models.BooleanField(default=True)
    type = models.IntegerField(choices=TYPE, default=0)
    comment = models.CharField(max_length=250, blank=True, null=False)
    created_at = models.DateTimeField('Created at', auto_now_add=True)


    def __str__(self):
        return str(self.id)


    class Meta:
        verbose_name_plural = "fixtures"
        verbose_name = "fixture"
        ordering = ('created_at',)