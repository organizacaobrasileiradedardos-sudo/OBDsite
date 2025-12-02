from django.contrib import admin
from brasilonline.dashboards.administrators.fixtures.models import Fixture

class FixtureAdmin(admin.ModelAdmin):
    list_display = ('id', 'division', 'status', 'validation', 'server', 'enabled', 'comment', 'created_at')
    date_hierarchy = 'created_at'
    search_fields = ('id', 'division', 'status', 'server', 'link', 'enabled', 'comment', 'created_at')
    list_filter = ('created_at',)


admin.site.register(Fixture, FixtureAdmin)