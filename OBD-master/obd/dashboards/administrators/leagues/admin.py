from django.contrib import admin
from obd.dashboards.administrators.leagues.models import League

class LeagueAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'start_date', 'end_date', 'phase', 'scope', 'slug', 'status', 'created_at')
    # Editável direto na listagem: é assim que se corrige uma liga cujo nome ficou
    # diferente do nome do torneio capturado.
    list_editable = ('category',)
    date_hierarchy = 'created_at'
    search_fields = ('id', 'name', 'start_date', 'end_date', 'phase', 'scope', 'status', 'created_by')
    list_filter = ('category', 'created_at')


admin.site.register(League, LeagueAdmin)