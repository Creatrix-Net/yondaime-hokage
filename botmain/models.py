from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class servers(models.Model):
    servername = models.CharField(_('Server Name'),null=True,max_length=500)
    server_user_data = models.JSONField(_('Server Users Data'),null=False,default=dict)
    levels = models.BooleanField(_('Leveling and autoroles'),default='False')

    def __str__(self):
        return self.servername
