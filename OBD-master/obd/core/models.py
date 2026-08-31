from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from cloudinary.models import CloudinaryField


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
    flyer = CloudinaryField('Flyer', blank=True, null=True)
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
    content = models.TextField(
        'Conteúdo Completo',
        blank=True,
        help_text='Preencha para notícias próprias da OBD (sem link de fonte externa). '
                   'Vira a página que abre ao clicar na notícia no site.',
    )
    link = models.URLField('Link da Notícia (fonte externa, opcional)', blank=True)
    source = models.CharField('Fonte', max_length=100)
    published_date = models.DateField('Data de Publicação')
    image = CloudinaryField('Imagem (upload)', blank=True, null=True)
    image_url = models.URLField('URL da Imagem (alternativa ao upload)', blank=True)
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

    @property
    def display_image_url(self):
        """Prioriza a imagem enviada por upload; usa a URL externa como alternativa."""
        if self.image:
            return self.image.url
        return self.image_url


class NewsImage(models.Model):
    """Extra gallery images for a News article, in addition to its main image"""
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='gallery_images')
    image = CloudinaryField('Imagem')
    caption = models.CharField('Legenda', max_length=200, blank=True)
    order = models.PositiveIntegerField('Ordem', default=0)

    class Meta:
        verbose_name = 'Imagem da Galeria'
        verbose_name_plural = 'Imagens da Galeria'
        ordering = ['order', 'id']

    def __str__(self):
        return f"Imagem de {self.news.title}"


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
    file = CloudinaryField('Arquivo', resource_type='raw', folder='documents')
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


class TournamentResult(models.Model):
    """Model for storing N01 tournament results"""
    name = models.CharField('Nome do Torneio', max_length=200)
    source_url = models.URLField('URL da Fonte')
    date = models.DateField('Data do Torneio', default=timezone.now)
    created_at = models.DateTimeField('Capturado em', auto_now_add=True)
    prize_value = models.DecimalField(
        'Premiação Distribuída (R$)',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        default=None,
        help_text='Preencha apenas para torneios avulsos (ex: Tour Online). '
                   'Etapas da Liga Nacional já têm a premiação somada via Order of Merit, '
                   'não preencha aqui para evitar contar em dobro.',
    )

    class Meta:
        verbose_name = 'Resultado de Torneio'
        verbose_name_plural = 'Resultados de Torneios'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.name} ({self.date})"


class PlayerTournamentStat(models.Model):
    """Model for storing player stats in a tournament"""
    tournament = models.ForeignKey(TournamentResult, on_delete=models.CASCADE, related_name='stats')
    player_name = models.CharField('Nome do Jogador', max_length=100)
    player = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tournament_stats')
    rank = models.IntegerField('Classificação')
    
    # Match Stats
    matches_played = models.IntegerField('Partidas Jogadas', default=0)
    matches_won = models.IntegerField('Partidas Vencidas', default=0)
    win_rate_matches = models.CharField('Win Rate (Partidas)', max_length=10, default="0%")
    
    # Leg Stats
    legs_played = models.IntegerField('Legs Jogados', default=0)
    legs_won = models.IntegerField('Legs Vencidos', default=0)
    legs_diff = models.IntegerField('Saldo de Legs', default=0)
    win_rate_legs = models.CharField('Win Rate (Legs)', max_length=10, default="0%")
    
    # Averages
    average_3_dart = models.FloatField('Média 3 Dardos', default=0.0)
    average_1_dart = models.FloatField('Média 1 Dardo', default=0.0)
    first_9_average = models.FloatField('Média Primeiros 9', default=0.0)
    
    # High Scores & Finishes
    best_leg = models.IntegerField('Melhor Leg (Dardos)', default=0)
    worst_leg = models.IntegerField('Pior Leg (Dardos)', default=0)
    high_finish = models.IntegerField('Maior Fechamento', default=0)
    count_100_plus = models.IntegerField('100+', default=0)
    count_140_plus = models.IntegerField('140+', default=0)
    count_170_plus = models.IntegerField('170+', default=0) # Although rare/impossible in some formats, column exists
    count_180 = models.IntegerField('180s', default=0)
    count_100_plus_finish = models.IntegerField('Fechamentos 100+', default=0)

    class Meta:
        verbose_name = 'Estatística de Jogador'
        verbose_name_plural = 'Estatísticas de Jogadores'
        ordering = ['rank']
    
    def __str__(self):
        return f"{self.rank}. {self.player_name} - {self.tournament.name}"
