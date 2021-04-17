#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import multiprocessing
import os
import sys

import dotenv
import sentry_sdk


def token_get(tokenname):
    if os.path.isfile(".env"):
        dotenv.load_dotenv(".env")
    return os.environ.get(tokenname)

sentry_link = token_get('SENTRY')

def main():
    """Run administrative tasks."""
    global sentry_link
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    sentry_sdk.init(
        sentry_link,
        traces_sample_rate=1.0
    )
    try:
        division_by_zero = 1 / 0
    except:
        pass
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    multiprocessing.Process(target=main).start()
    multiprocessing.Process(target=os.system('python discordbot.py')).start()
