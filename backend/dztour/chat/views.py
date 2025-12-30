from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import Thread, ChatMessage
from .serializers import ThreadSerializer, ChatMessageSerializer
from users.models import User


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def thread_list_view(request):
    threads = Thread.objects.by_user(request.user).order_by('-updated_at')
    serializer = ThreadSerializer(threads, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def chat_message_list_view(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    thread = Thread.objects.get_or_create_thread(request.user, other_user)
    if not thread:
        return Response({'error': 'Chat between these users can\'t exist'}, status=status.HTTP_404_NOT_FOUND)
    
    messages = ChatMessage.objects.filter(thread=thread).order_by('-timestamp')
    serializer = ChatMessageSerializer(messages, many=True)
    return Response(serializer.data)