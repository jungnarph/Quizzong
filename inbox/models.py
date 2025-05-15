from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.SET_NULL, null=True)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.SET_NULL, null=True)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.subject} from {self.sender} to {self.recipient}'
