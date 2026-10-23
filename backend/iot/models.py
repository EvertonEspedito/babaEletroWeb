
from django.db import models


class Alert(models.Model):
    alert_type = models.CharField(
        max_length=40,
        default="possible_cry"
    )

    message = models.CharField(max_length=240)

    sound_level = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.message} - {self.created_at}"


class DeviceStatus(models.Model):
    name = models.CharField(max_length=80, unique=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    last_sound_level = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.last_seen}"
