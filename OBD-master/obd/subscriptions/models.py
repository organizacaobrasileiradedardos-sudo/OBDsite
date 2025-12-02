from django.db import models


class Subscription(models.Model):
    name = models.CharField('Name', max_length=30)
    last = models.CharField('Last Name', max_length=60)
    email = models.EmailField('E-mail')
    password = models.CharField('Password', max_length=99)
    country = models.CharField('Country', max_length=40)
    nickname = models.CharField('Nickname', max_length=40)
    created_at = models.DateTimeField('Created at', auto_now_add=True)

    class Meta:
        verbose_name_plural = "inscrições"
        verbose_name = "inscrição"
        ordering = ('-created_at',)

    def __str__(self):
        return self.name+' '+self.last
