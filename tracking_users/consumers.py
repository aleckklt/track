import json
from channels.generic.websocket import AsyncWebsocketConsumer

class AdminConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("admin_notifications", self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({"message": "Connecté au serveur"}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("admin_notifications", self.channel_name)

    async def user_event(self, event):
        await self.send(text_data=json.dumps({
            "type": "user_event",
            "user": event["user"],
            "login_time": event.get("login_time"),
            "logout_time": event.get("logout_time"),
            "session_duration": event.get("session_duration"),
        }))