from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


def image_file_path(instance, filename):
    ext = instance.split('.')[-1]
    return f"{instance.nickname}.{ext}"


def validate_file_extension(value):
    if not value.lower()[-3:] not in ['png, jpg']:
        raise ValidationError('Unsupported file extension.')


class Event(models.Model):
    author = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=250, null=False, blank=True)
    info = models.CharField(max_length=250, null=False, blank=True)
    photo = models.ImageField(blank=True, null=False)
    start_date = models.DateField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    slug = models.CharField(max_length=180, null=False, blank=True)
    created_at = models.DateTimeField('Created at', auto_now_add=True)

