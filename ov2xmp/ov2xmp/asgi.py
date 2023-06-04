"""
ASGI config for ov2xmp project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path, re_path
from channels.security.websocket import AllowedHostsOriginValidator
from tasks.TasksConsumer import TasksConsumer
from dashboard.CSMSConsumer import CSMSConsumer


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ov2xmp.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    # Django's ASGI application to handle traditional HTTP requests
    "http": django_asgi_app,

    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                path("ws/tasks_updates/", TasksConsumer.as_asgi()),
                path("ws/csms_updates/", CSMSConsumer.as_asgi()),
                #re_path(r"csms/*", CSMSConsumer.as_asgi()),
            ])
        )
    ),
})

