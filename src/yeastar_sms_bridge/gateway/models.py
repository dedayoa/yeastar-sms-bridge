import uuid

import pytz
from django.conf import settings
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError


# Create your models here.
class Device(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    api_url = models.URLField(blank=True)
    api_username = models.CharField(max_length=255)
    api_password = models.CharField(max_length=255)
    
    sms_sending_disabled = models.BooleanField(default=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    
    created = models.DateTimeField(auto_now=True)
    last_modified = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name}/{self.owner}"


class Span(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    channel_id = models.CharField(max_length=3)
    
    SIM_phone_number = PhoneNumberField()
    SIM_IMSI = models.CharField(max_length=30, blank=True)
    
    device = models.ForeignKey(Device, on_delete=models.PROTECT, related_name="spans")
    sms_sending_disabled = models.BooleanField(default=False)
    
    total_messages_sent = models.PositiveIntegerField(default=0)
    total_messages_sent_today = models.PositiveIntegerField(default=0)
    total_messages_sent_month = models.PositiveIntegerField(default=0)
    
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    message_failure_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return "Channel: {}, {}".format(self.channel_id, self.SIM_phone_number)
    
    def port_id(self):
        return int(self.channel_id)-1
            

class SendProfile(models.Model):
    """ The send profile determines how the messages are delivered
    to a single span, multiple spans (standard and LCR) etc. """
    class SendStrategy:
        SINGLE = "SINGLE"
        DISTRIBUTE = "DISTRIBUTE"
        RANDOM = "RANDOM"
        
    STRATEGY = (
        (SendStrategy.SINGLE, "Single"),
        (SendStrategy.DISTRIBUTE, "Distribute"),
        (SendStrategy.RANDOM, "Random"),
        )    
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=False)
    spans = models.ManyToManyField(Span)
    strategy = models.CharField(max_length=20, choices=STRATEGY, default=SendStrategy.SINGLE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    is_default = models.BooleanField(default=True)
            
    def __str__(self):
        return self.name
        