from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(default=timezone.now)
    logout_time = models.DateTimeField(null=True, blank=True)
    session_duration = models.DurationField(null=True, blank=True)
    is_connected = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.logout_time and self.is_connected:
            self.is_connected = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {'Connecté' if self.is_connected else 'Déconnecté'}"