from django.contrib import admin
from .models import Event, News, Document


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'event_date', 'location', 'is_active', 'is_upcoming')
    list_filter = ('event_type', 'is_active', 'event_date')
    search_fields = ('title', 'description', 'location')
    date_hierarchy = 'event_date'
    ordering = ('event_date',)
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('title', 'description', 'event_type')
        }),
        ('Data e Local', {
            'fields': ('event_date', 'end_date', 'location')
        }),
        ('Configurações', {
            'fields': ('registration_link', 'is_active')
        }),
    )


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'published_date', 'is_featured', 'is_active')
    list_filter = ('is_featured', 'is_active', 'published_date', 'source')
    search_fields = ('title', 'summary', 'source')
    date_hierarchy = 'published_date'
    ordering = ('-published_date',)
    fieldsets = (
        ('Informações da Notícia', {
            'fields': ('title', 'summary', 'link', 'source')
        }),
        ('Mídia', {
            'fields': ('image_url',)
        }),
        ('Data e Configurações', {
            'fields': ('published_date', 'is_featured', 'is_active')
        }),
    )


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'version', 'publish_date', 'is_active')
    list_filter = ('category', 'is_active', 'publish_date')
    search_fields = ('title', 'description')
    date_hierarchy = 'publish_date'
    ordering = ('category', '-publish_date')
    fieldsets = (
        ('Informações do Documento', {
            'fields': ('title', 'description', 'category', 'version')
        }),
        ('Arquivo', {
            'fields': ('file',)
        }),
        ('Data e Configurações', {
            'fields': ('publish_date', 'is_active')
        }),
    )
