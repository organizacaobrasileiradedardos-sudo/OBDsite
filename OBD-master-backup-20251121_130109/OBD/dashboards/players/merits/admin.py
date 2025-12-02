from django.contrib import admin
from brasilonline.dashboards.players.merits.models import Merit


class MeritModelAdmin(admin.ModelAdmin):
    list_display = ('player', 'match', 'points', 'type', 'enabled', 'created_at')
    date_hierarchy = 'created_at'
    search_fields = ('player', 'match', 'points', 'type', 'enabled', 'created_at')
    list_filter = ('player', 'match', 'points', 'type', 'enabled', 'created_at',)

admin.site.register(Merit, MeritModelAdmin)