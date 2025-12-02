from django.contrib import admin
from brasilonline.dashboards.administrators.enviroments.models import Enviroment


class EnviromentAdmin(admin.ModelAdmin):
    list_display = ('id', 'leagueABestof', 'leagueBBestof', 'leagueAGameMode', 'leagueAWinnerBy', 'meritTimeline', 'created_at')
    date_hierarchy = 'created_at'
    search_fields = ('id', 'leagueABestof', 'leagueBBestof', 'leagueCBestof', 'leagueAGameMode', 'leagueAWinnerBy', 'meritTimeline', 'leagueSubscriptionsEnds')
    list_filter = ('created_at',)


admin.site.register(Enviroment, EnviromentAdmin)
