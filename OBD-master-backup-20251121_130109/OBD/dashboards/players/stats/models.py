from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Stat(models.Model):
    """Stat Class on OneToOne with User models"""
    LEAGUE_DIV = [
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

    LEAGUE_CLASS = [
        (1, 'CLASS PRO'),
        (2, 'CLASS A'),
        (3, 'CLASS B'),
        (4, 'CLASS C'),
        (5, 'CLASS D'),
        (99, 'CLASS R')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bcmClass = models.IntegerField(choices=LEAGUE_CLASS, default=99)
    bcmDiv = models.IntegerField(choices=LEAGUE_DIV, default=10)
    bcmPoints = models.FloatField(default=0)
    bcmAvg = models.FloatField(default=0)
    best3da = models.FloatField(default=0)
    bcmMatches = models.IntegerField(default=0)
    bcmWin = models.IntegerField(default=0)
    bcm9DartsEnd = models.IntegerField(default=0)
    bcmTon = models.IntegerField(default=0)
    bcmTon40 = models.IntegerField(default=0)
    bcmTon70 = models.IntegerField(default=0)
    bcmTon80 = models.IntegerField(default=0)
    bcmLeg = models.IntegerField(default=0)
    bcmOut = models.IntegerField(default=0)
    leaguePerformance = models.CharField(max_length=10, default='XXXXXXXXXX')
    leagueParticipation = models.IntegerField(default=0)
    divAwinner = models.IntegerField(default=0)
    divBwinner = models.IntegerField(default=0)
    divCwinner = models.IntegerField(default=0)
    divDwinner = models.IntegerField(default=0)
    divOtherswinner = models.IntegerField(default=0)
    created_at = models.DateTimeField('Created at', auto_now_add=True)

    class Meta:
        verbose_name_plural = "stats"
        verbose_name = "stat"
        ordering = ('-created_at',)

    def __str__(self):
        return str(self.bcmClass)

@receiver(post_save, sender=User)
def create_user_stat(sender, instance, created, **kwargs):
    if created:
        Stat.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_stat(sender, instance, **kwargs):
    instance.stat.save()
