
from django.db import models

class BotLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    user_id = models.BigIntegerField()
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    chat_type = models.CharField(max_length=50, null=True, blank=True)
    message_text = models.TextField(null=True, blank=True)
    command = models.CharField(max_length=100, null=True, blank=True)
    action = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user_id} - {self.action} - {self.timestamp}"
