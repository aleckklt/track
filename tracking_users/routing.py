from django.urls import re_path
from .consumers import AdminConsumer

websocket_urlpatterns = [
    re_path(r'ws/admin/notifications/$', AdminConsumer.as_asgi()),
]
