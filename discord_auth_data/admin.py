from django.contrib import admin
from .models import DiscordUser, DiscordInvite


@admin.register(DiscordUser)
class DiscordUserAdmin(admin.ModelAdmin):
    list_display = ('user',
                    'uid',
                    'username',
                    'discriminator',
                    'email')
    list_display_links = ('uid',)
    fieldsets = (
        (None, {
            'fields': ('user',),
        }),
        ('Discord Account', {
            'fields': ('uid',
                       ('username', 'discriminator'),
                       'email', 'avatar'),
        }),
        ('OAuth2', {
            'classes': ('collapse',),
            'fields': ('access_token', 'refresh_token', 'scope', 'expiry'),
        }),
    )
    readonly_fields = ('user',
                       'uid',
                       'access_token',
                       'refresh_token',
                       'scope',
                       'expiry')
    search_fields = ['user__username',
                     'user__email',
                     'username',
                     'discriminator',
                     'uid',
                     'email']


@admin.register(DiscordInvite)
class DiscordInviteAdmin(admin.ModelAdmin):
    list_display = ('code',
                    'active',
                    'description',
                    'guild_name',
                    'channel_name',
                    'channel_type')
    list_display_links = ('code',)
    fieldsets = (
        (None, {
            'fields': (('code', 'active'), 'description', 'groups'),
        }),
        ('Discord Guild', {
            'fields': ('guild_name', 'guild_id', 'guild_icon'),
        }),
        ('Discord Channel', {
            'fields': ('channel_name', 'channel_id', 'channel_type'),
        }),
    )
    readonly_fields = ('guild_name',
                       'guild_id',
                       'guild_icon',
                       'channel_name',
                       'channel_id',
                       'channel_type')
    filter_horizontal = ('groups',)
    actions = ['update_context']

    def update_context(self, request, queryset):
        """ Pull invite details from Discord """
        update = 0
        delete = 0
        invites = queryset.all()
        for invite in invites:
            if invite.update_context():
                update += 1
            else:
                invite.delete()
                delete += 1
        self.message_user(request, '%d updated, %d deleted' % (update, delete))
    update_context.short_description = 'Update invite context'
