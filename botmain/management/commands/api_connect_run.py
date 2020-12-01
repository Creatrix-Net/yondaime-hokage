"""
 Simple internal command to keep the process running
"""
from django.core.management.base import BaseCommand
class Command(BaseCommand):
    help = "Simple internal command to keep the process running"
    def handle(self, *args, **options): return True
