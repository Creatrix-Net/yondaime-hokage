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

admin.site.register(AnimeName, AnimeNameAdmin)
admin.site.register(AnimeImage, AnimeImageAdmin)
admin.site.unregister(Group)

admin.site.site_header = 'Yondaime Hokage'
admin.site.site_title = 'Minato Namikaze'
admin.site.index_title = 'Minato Namikaze · Yondaime Hokage'
