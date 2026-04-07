"""
cPanel Passenger entry point.
Place this file in the application root (same directory as manage.py).
"""
import os
import sys

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

from django.core.wsgi import get_wsgi_application  # noqa: E402
application = get_wsgi_application()
