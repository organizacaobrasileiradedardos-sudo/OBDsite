from django.contrib import admin
from django.utils.timezone import now
from obd.dashboards.players.profiles.models import ApelidoN01, Profile


class ApelidoN01Inline(admin.TabularInline):
    """Outros nomes com que o jogador aparece no N01, editáveis junto com o perfil."""
    model = ApelidoN01
    extra = 1


class ProfileModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'pin', 'nickname', 'nakka', 'country', 'state')
    date_hierarchy = 'created_at'
    search_fields = ('pin', 'nickname', 'nakka', 'country', 'state')
    list_filter = ('country',)
    inlines = [ApelidoN01Inline]

    def subscribed_today(self, obj):
        return obj.created_at == now().date()

    subscribed_today.short_description = 'Subscribed today?'
    subscribed_today.boolean = True


@admin.register(ApelidoN01)
class ApelidoN01Admin(admin.ModelAdmin):
    list_display = ('apelido', 'profile', 'created_at')
    search_fields = ('apelido', 'profile__nickname', 'profile__user__username')


admin.site.register(Profile, ProfileModelAdmin)
