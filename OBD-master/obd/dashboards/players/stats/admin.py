from django.contrib import admin
from django.utils.timezone import now
from obd.dashboards.players.stats.models import Stat


class StatModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'bcmDiv', 'leagueParticipation', 'bcmAvg', 'bcmMatches', 'bcmWin', 'created_at')
    date_hierarchy = 'created_at'
    search_fields = ('bcmDiv',)
    list_filter = ('bcmDiv',)

    def subscribed_today(self, obj):
        return obj.created_at == now().date()

    subscribed_today.short_description = 'Subscribed today?'
    subscribed_today.boolean = True


admin.site.register(Stat, StatModelAdmin)