from django.db import models
from django.utils import timezone


class Event(models.Model):
    """Model for events calendar"""
    EVENT_TYPES = [
        ('tournament', 'Torneio'),
        ('championship', 'Campeonato'),
        ('training', 'Treinamento'),
        ('meeting', 'Reunião'),
        ('other', 'Outro'),
    ]
    
    title = models.CharField('Título', max_length=200)
    description = models.TextField('Descrição')
    event_date = models.DateTimeField('Data do Evento')
    end_date = models.DateTimeField('Data de Término', null=True, blank=True)
    location = models.CharField('Local', max_length=200)
    event_type = models.CharField('Tipo', max_length=50, choices=EVENT_TYPES, default='other')
    registration_link = models.URLField('Link de Inscrição', blank=True)
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['event_date']
    
    def __str__(self):
        return f"{self.title} - {self.event_date.strftime('%d/%m/%Y')}"
    
    @property
    def is_upcoming(self):
        return self.event_date >= timezone.now()


class News(models.Model):
    """Model for darts news"""
    title = models.CharField('Título', max_length=200)
    summary = models.TextField('Resumo')
    link = models.URLField('Link da Notícia')
    source = models.CharField('Fonte', max_length=100)
    published_date = models.DateField('Data de Publicação')
    image_url = models.URLField('URL da Imagem', blank=True)
    is_featured = models.BooleanField('Destaque', default=False)
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Notícia'
        verbose_name_plural = 'Notícias'
        ordering = ['-published_date']
    
    def __str__(self):
        return f"{self.title} - {self.source}"


class Document(models.Model):
    """Model for official documents"""
    CATEGORY_CHOICES = [
        ('statute', 'Estatuto'),
        ('rules', 'Regras'),
        ('regulation', 'Regulamento'),
        ('guide', 'Guia'),
        ('other', 'Outro'),
    ]
    
    title = models.CharField('Título', max_length=200)
    description = models.TextField('Descrição')
    category = models.CharField('Categoria', max_length=50, choices=CATEGORY_CHOICES, default='other')
    file = models.FileField('Arquivo', upload_to='documents/')
    version = models.CharField('Versão', max_length=20, default='1.0')
    publish_date = models.DateField('Data de Publicação', default=timezone.now)
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        ordering = ['category', '-publish_date']
    
    def __str__(self):
        return f"{self.title} (v{self.version})"
