from django.contrib import admin
from obd.dashboards.administrators.divisions.models import Division

class DivisionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'formation', 'status', 'slug', 'description', 'created_at')
    date_hierarchy = 'created_at'
    search_fields = ('id', 'name', 'formation', 'description', 'slug', 'status', 'created_by')
    list_filter = ('created_at',)


admin.site.register(Division, DivisionAdmin)