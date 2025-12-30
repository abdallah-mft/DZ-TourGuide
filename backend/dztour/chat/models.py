from django.db import models
from django.conf import settings
from django.db.models import Q

class ThreadManager(models.Manager):
    def by_user(self, user):
        return self.get_queryset().filter(Q(first_person=user) | Q(second_person=user)).distinct()

    def get_or_create_thread(self, user1, user2):
        if user1 == user2:
            return None
            
        if user1.role == user2.role:
            return None

        qlookup1 = Q(first_person=user1) & Q(second_person=user2)
        qlookup2 = Q(first_person=user2) & Q(second_person=user1)
        thread = self.get_queryset().filter(qlookup1 | qlookup2).first()
        if thread:
            return thread
        else:
            thread = self.create(first_person=user1, second_person=user2)
            return thread

class Thread(models.Model):
    first_person = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='thread_first_person')
    second_person = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='thread_second_person')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ThreadManager()

    class Meta:
        unique_together = ['first_person', 'second_person']

    def __str__(self):
        return f"Thread between {self.first_person} and {self.second_person}"

class ChatMessage(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='chatmessage_thread')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.user} in {self.thread}"
