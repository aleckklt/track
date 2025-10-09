import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils.timezone import now

class AdminConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if not user.is_authenticated or not user.is_staff:
            await self.close()
            return

        self.group_name = "admin_notifications"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def user_connected(self, event):

        await self.send_json({
            'type': 'user_connected',
            'data': event['data']
        })

    async def user_disconnected(self, event):

        await self.send_json({
            'type': 'user_disconnected',
            'data': event['data']
        })