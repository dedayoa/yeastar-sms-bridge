from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from sms_counter import SMSCounter
import uuid
from django.conf import settings

# Create your models here.

class SMSMessageStateLog(models.Model):
    class State:
        PROCESSING = "processing"
        SUBMITTED_OK = "submitted"
        QUEUED = "queued"
        DELAYED = "delayed"
        FAILED = "failed"
        ERROR = "error"

    STATE = (
        (State.SUBMITTED_OK, "Submitted OK"),
        (State.QUEUED, "Queued"),
        (State.DELAYED, "Delayed"),
        (State.FAILED, "Failed"),
        (State.PROCESSING, "Processing"),
        (State.ERROR, "Error")
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sms_message_id = models.UUIDField(blank=False, null=False, db_index=True)
    state = models.CharField(max_length=30, default=State.QUEUED, choices=STATE)
    state_reason = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class SMSMessage(models.Model):
    class Status:
        NEW = "new"
        SUCCESS = "success"
        FAILED = "failed"
        ERROR = "error"

    STATUS = (
        (Status.SUCCESS, "Success"),
        (Status.NEW, "New"),
        (Status.FAILED, "Failed"),
        (Status.ERROR, "Error")
    )
    id = models.UUIDField(primary_key=True, editable=False)
    bulk_id = models.UUIDField(blank=True, null=True)
    text = models.TextField(blank=False)
    recipient = PhoneNumberField()
    pages = models.PositiveIntegerField(default=0, blank=True)  
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, default=Status.NEW, choices=STATUS)
    class Meta:
        ordering = ("-created_at",)
        verbose_name = "SMS Message"
        verbose_name_plural = "SMS Messages"
    
    def __str__(self):
        return self.text
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = uuid.uuid4()
        self.pages = SMSCounter.count(self.text)['messages']
        super(SMSMessage, self).save(*args, **kwargs)

    def add_state_log(self, state, state_reason = ""):
        SMSMessageStateLog.objects.create(
            sms_message_id = self.id,
            state = state,
            state_reason = state_reason
        )
        if state == SMSMessageStateLog.State.SUBMITTED_OK:
            self.status = SMSMessage.Status.SUCCESS
        if state == SMSMessageStateLog.State.FAILED:
            self.status = SMSMessage.Status.FAILED
        if state == SMSMessageStateLog.State.ERROR:
            self.status = SMSMessage.Status.ERROR
        self.save()

    def get_latest_state_log(self):
        return SMSMessageStateLog.objects.filter(sms_message_id = self.id).first()
            
class InvalidSMSMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField(blank=False)
    message = models.OneToOneField(SMSMessage, on_delete=models.SET_NULL, null=True)
    recipient = models.CharField(max_length=255)
    error_reason = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.recipient} / {self.error_reason}'
    
    class Meta:
        ordering = ("-created",)


class SMSQueue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.OneToOneField(SMSMessage, on_delete=models.CASCADE)
    submit_attempts = models.PositiveIntegerField(default=0)
    send_span = models.ForeignKey('gateway.Span', on_delete=models.PROTECT, related_name="span_sms_messages")
    next_submit_attempt_at = models.DateTimeField(help_text="next time send_sms will be attempted", null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ("-created",)




