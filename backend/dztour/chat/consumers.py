import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Thread, ChatMessage

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        if not user.is_authenticated:
            await self.close()
            return

        other_user_id = self.scope['url_route']['kwargs']['user_id']
        self.other_user = await self.get_user(other_user_id)
        if not self.other_user:
            await self.close()
            return

        self.thread = await self.get_thread(user, self.other_user)
        if not self.thread:
             await self.close()
             return

        self.room_group_name = f"chat_thread_{self.thread.id}"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        user = self.scope['user']

        if message:
            chat_message = await self.create_chat_message(self.thread, user, message)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user_id': user.id,
                    'user_email': user.email,
                    'timestamp': chat_message.timestamp.isoformat()
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'user_id': event['user_id'],
            'user_email': event['user_email'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def get_thread(self, user1, user2):
        return Thread.objects.get_or_create_thread(user1, user2)

    @database_sync_to_async
    def create_chat_message(self, thread, user, message):
        return ChatMessage.objects.create(thread=thread, user=user, message=message)
