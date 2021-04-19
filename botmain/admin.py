from django.contrib import admin
from .models import *
from django.contrib.auth.admin import Group
from django.utils.translation import gettext_lazy as _
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter


class AnimeNameAdmin(admin.ModelAdmin):
     search_fields = list_display = ('anime_name', 'url')
     list_per_page = 50
     fieldsets = (
        (_('Name'), {'fields': ('anime_name', )}),
        (_('Url'), {'fields': ('url',)}),
    )


class AnimeImageAdmin(admin.ModelAdmin):
    search_fields = list_display = ('anime_category', 'id','image')
    readonly_fields  = ('view_picture',)
    list_per_page = 100
   
    list_filter = (('anime_category', RelatedDropdownFilter),)
    
    fieldsets = (
        (_('Anime Category'), {'fields': ('anime_category', )}),
        (_('Image'), {'fields': ('image', 'view_picture',)}),
    )

class DiscordBotListAdmin(admin.ModelAdmin):
    search_fields = list_display = ('website',)
    readonly_fields  = ('view_website','view_widget')
    list_per_page = 10
       
    fieldsets = (
        (_('Information'), {'fields': ('website', 'widget')}),
        (_('View Website'), {'fields': ('view_website', )}),
        (_('View Widget'), {'fields': ('view_widget', )}),
    )

class ServerListAdmin(admin.ModelAdmin):
    search_fields = list_display = ('website',)
    readonly_fields  = ('view',)
    list_per_page = 10
       
    fieldsets = (
        (_('Information'), {'fields': ('website', )}),
        (_('View Website'), {'fields': ('view',)}),
    )

class InvitesAdmin(admin.ModelAdmin):
    search_fields = list_display = ('name', 'site', 'invites')
    readonly_fields  = ('invites',)
    list_per_page = 10
       
    fieldsets = (
        (_('Information of Referrer'), {'fields': ('name', 'site')}),
        (_('Total No of Invites'), {'fields': ('invites',)}),
    )

admin.site.register(DiscordBotList, DiscordBotListAdmin)
admin.site.register(ServerList, ServerListAdmin)

admin.site.register(Invite, InvitesAdmin)

admin.site.register(AnimeName, AnimeNameAdmin)
admin.site.register(AnimeImage, AnimeImageAdmin)
admin.site.unregister(Group)

admin.site.site_header = 'Yondaime Hokage'
admin.site.site_title = 'Minato Namikaze'
admin.site.index_title = 'Minato Namikaze · Yondaime Hokage'
