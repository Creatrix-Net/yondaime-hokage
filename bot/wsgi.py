"""
WSGI config for bot project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot.settings')

application = get_wsgi_application()

try:
   import uwsgidecorators
   from django.core.management import call_command

   @uwsgidecorators.timer(1200)
   def send_queued_mail(num):
       '''run the command after 20 mins'''
       call_command('api_connect_run', processes=1)

except ImportError:
   print("uwsgidecorators not found. Cron and timers are disabled")