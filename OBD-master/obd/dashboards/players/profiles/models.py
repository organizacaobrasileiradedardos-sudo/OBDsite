from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


def image_file_path(instance, filename):
    ext = filename.split('.')[-1]
    return f'{instance.pin}.{ext}'

def validate_file_extension(value):
    if not value.lower()[-3:] not in ['png, jpg']:
        raise ValidationError('Unsupported file extension.')

class Profile(models.Model):
    """Profile Class on OneToOne with User models"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=40, null=False, blank=True)
    photo = models.ImageField(default='/static/media/logos/Logo_OBD_3.jpeg')
    birth_date = models.DateField(blank=True, null=True)
    pin = models.CharField(max_length=10, null=False, blank=True)
    slug = models.CharField(max_length=180, null=False, blank=True)
    bio = models.TextField(max_length=250, null=False, blank=True)
    country = models.CharField(max_length=60, blank=True, default='Brasil')
    state = models.CharField(max_length=40, null=False, blank=True)
    darts = models.CharField(max_length=150, null=False, blank=True)
    site = models.CharField(max_length=150, null=False, blank=True)
    facebook = models.CharField(max_length=150, null=False, blank=True)
    twitter = models.CharField(max_length=150, null=False, blank=True)


    nakka = models.CharField(max_length=80, null=False, blank=True)
    created_at = models.DateTimeField('Created at', auto_now_add=True)

    class Meta:
        verbose_name_plural = "profiles"
        verbose_name = "profile"
        ordering = ('-created_at',)
        permissions = [('has_admin_role', 'Administrador'),
                       ('has_player_role', 'Jogador'),
                       ('can_play_league', 'Habilitado para jogar na Liga')]

    def __str__(self):
        return str(self.pin)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
