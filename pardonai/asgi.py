"""
ASGI config for pardonai project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pardonai.settings')

application = get_asgi_application()
