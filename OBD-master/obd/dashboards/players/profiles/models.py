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
    pin = models.CharField(max_length=50, null=False, blank=True)
    is_verified = models.BooleanField('Verificado', default=True)
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


class ApelidoN01(models.Model):
    """Outros nomes com que o mesmo jogador já apareceu no N01.

    ``Profile.nakka`` guarda o apelido principal, mas um jogador pode aparecer com
    nomes diferentes em etapas diferentes. Quando dois cadastros são mesclados, o
    apelido do que foi absorvido vira um destes registros — sem isso, o robô de
    captura deixaria de reconhecer aquele nome e recriaria o cadastro na captura
    seguinte, desfazendo a mesclagem.
    """

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='apelidos_n01')
    apelido = models.CharField('Apelido no N01', max_length=80, unique=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'apelido no N01'
        verbose_name_plural = 'apelidos no N01'
        ordering = ('apelido',)

    def __str__(self):
        return self.apelido


def jogador_por_apelido_n01(nome):
    """Encontra o jogador por qualquer um dos nomes com que ele aparece no N01.

    Procura primeiro no apelido principal do perfil e depois nos alternativos.
    Devolve o User, ou None se nenhum cadastro usa aquele nome.
    """
    nome = (nome or '').strip()
    if not nome:
        return None

    perfil = Profile.objects.filter(nakka__iexact=nome).first()
    if perfil:
        return perfil.user

    alternativo = ApelidoN01.objects.select_related('profile__user').filter(apelido__iexact=nome).first()
    return alternativo.profile.user if alternativo else None


def apelido_n01_em_uso(nome, ignorar_profile=None):
    """Diz se algum cadastro já usa esse nome, como apelido principal ou alternativo."""
    nome = (nome or '').strip()
    if not nome:
        return True  # nome vazio não serve como apelido

    perfis = Profile.objects.filter(nakka__iexact=nome)
    apelidos = ApelidoN01.objects.filter(apelido__iexact=nome)
    if ignorar_profile is not None:
        perfis = perfis.exclude(pk=ignorar_profile.pk)
        apelidos = apelidos.exclude(profile=ignorar_profile)
    return perfis.exists() or apelidos.exists()
