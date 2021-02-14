from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.html import mark_safe

class AnimeName(models.Model):
    anime_name = models.CharField(verbose_name=_('Name of the Anime'),unique=True, max_length=500)
    url = models.URLField(verbose_name=_('Anime Description Url'),null=True,blank=True, help_text=_('Optional'))

    def __str__(self):
        return self.anime_name

    class Meta:
        verbose_name_plural = "Anime Name"

class AnimeImage(models.Model):
    anime_category = models.ForeignKey(AnimeName, on_delete=models.CASCADE, verbose_name=_('Anime Category'))
    image = models.URLField(verbose_name=_('Anime Image Url'))

    def __str__(self):
        return self.anime_category.anime_name + " " + str(self.id)
    
    def view_picture(self):
        height = '100%'
        width = '100%'
        if self.image:
            return mark_safe(f'<img src="{self.image}" width="{width}" height={height}" style="border-radius: 10px;" />')
        else:
            return mark_safe('<h4>Please upload an image</h4>')

    class Meta:
        verbose_name_plural = "Anime Image"