from django.contrib import admin
from django.utils.timezone import now
from obd.subscriptions.models import Subscription


class SubscriptionModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'last', 'email', 'nickname', 'country', 'created_at', 'subscribed_today')
    date_hierarchy = 'created_at'
    search_fields = ('name', 'email', 'nickname', 'country')
    list_filter = ('created_at',)

    def subscribed_today(self, obj):
        return obj.created_at == now().date()

    subscribed_today.short_description = 'Subscribed today?'
    subscribed_today.boolean = True

admin.site.register(Subscription, SubscriptionModelAdmin)