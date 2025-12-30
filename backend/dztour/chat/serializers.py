from rest_framework import serializers
from .models import Thread, ChatMessage
from users.serializers import UserSerializer

class ChatMessageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'user', 'message', 'timestamp']

class ThreadSerializer(serializers.ModelSerializer):
    other_user = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Thread
        fields = ['id', 'other_user', 'updated_at', 'last_message']

    def get_other_user(self, obj):
        request = self.context.get('request')
        if request and request.user:
            if obj.first_person == request.user:
                return UserSerializer(obj.second_person).data
            return UserSerializer(obj.first_person).data
        return None

    def get_last_message(self, obj):
        last_msg = obj.chatmessage_thread.order_by('-timestamp').first()
        if last_msg:
            return ChatMessageSerializer(last_msg).data
        return None
