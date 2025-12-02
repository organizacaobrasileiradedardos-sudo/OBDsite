from django.contrib import admin
from brasilonline.dashboards.administrators.results.models import Result


class Resultadmin(admin.ModelAdmin):
    list_display = ('id', 'fixture', 'player', 'enabled', 'validation', 'walkover', 'final', 'legs', 'points', 'highest_out', 'best_leg', 'ton', 'ton40', 'ton70', 'ton80', 'average', 'created_at', 'comment')
    date_hierarchy = 'created_at'
    search_fields = ('id', 'final', 'enabled', 'player', 'fixture', 'validation', 'highest_out', 'best_leg')
    list_filter = ('created_at', 'enabled', 'validation', 'walkover', 'fixture__division', 'highest_out', 'best_leg')

admin.site.register(Result, Resultadmin)