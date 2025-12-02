from django.contrib import admin
from django.utils.timezone import now
from obd.dashboards.players.profiles.models import Profile


class ProfileModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'pin', 'nickname', 'bio', 'country', 'state')
    date_hierarchy = 'created_at'
    search_fields = ('pin', 'nickname', 'country', 'state')
    list_filter = ('country',)

    def subscribed_today(self, obj):
        return obj.created_at == now().date()

    subscribed_today.short_description = 'Subscribed today?'
    subscribed_today.boolean = True


admin.site.register(Profile, ProfileModelAdmin)
