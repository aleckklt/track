from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(default=timezone.now)
    logout_time = models.DateTimeField(null=True, blank=True)
    session_duration = models.DurationField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.login_time.strftime('%Y-%m-%d %H:%M:%S')})"