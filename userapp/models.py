from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from timezone_field import TimeZoneField
# Create your models here.

class User(AbstractUser):
    pass

class Contact(models.Model):
    first_name = models.CharField(max_length=255, blank=False)
    last_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="contacts", null=True, blank=True)
    
    def __str__(self):
        return self.first_name


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    notification_contacts = models.ManyToManyField(Contact, blank=True, help_text="general notification recipient(s)")
    messages_backup_recipients = models.ManyToManyField(Contact, blank=True, help_text="message backup recipient(s)", related_name="backup_recipients")
    timezone = TimeZoneField()
    daily_summary_last_sent_at = models.DateTimeField(blank=True, null=True)
    messages_backup_last_sent_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return self.user.get_full_name()