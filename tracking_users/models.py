from django.db import models
from django.contrib.auth.models import User

class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField()
    logout_time = models.DateTimeField(null=True, blank=True)

    @property
    def time_connexion(self):
        if self.logout_time:
            return self.logout_time - self.login_time
        return None
    
    def __str__(self):
        return f"{self.user.username} - {self.login_time}"