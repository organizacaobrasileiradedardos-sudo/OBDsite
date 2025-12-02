from django.contrib import admin
from brasilonline.dashboards.administrators.champions.models import Champion

class ChampionAdmin(admin.ModelAdmin):
    list_display = ('id', 'league', 'division', 'p1', 'p2', 'p3', 'p4', 'created_at')
    date_hierarchy = 'created_at'
    search_fields = ('id', 'league', 'division', 'p1', 'p2', 'p3', 'p4', 'created_at')
    list_filter = ('id', 'league', 'division', 'p1', 'p2', 'p3', 'p4', 'created_at')


admin.site.register(Champion, ChampionAdmin)
