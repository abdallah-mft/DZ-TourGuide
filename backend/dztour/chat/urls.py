from django.urls import path
from .views import chat_message_list_view, thread_list_view

urlpatterns = [
    path('threads/', thread_list_view),
    path('messages/<int:user_id>/', chat_message_list_view),
]
