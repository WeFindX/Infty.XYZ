from django.db import models
from django.conf import settings
from django.db.models.signals import post_save

from core.models import Comment


class CryptsyTransaction(models.Model):
    address = models.ForeignKey(
        'CoinAddress',
        related_name='cryptsy_transaction'
    )
    sender_credential = models.ForeignKey(
        'CryptsyCredential', related_name='cryptsy_transaction'
    )
    amount = models.PositiveIntegerField()
    fee = models.PositiveIntegerField()
    timestamp = models.PositiveIntegerField()
    timezone = models.CharField(max_length=3)
    trxid = models.CharField(max_length=255, null=True, blank=True)
    message = models.CharField(max_length=255)
    datetime = models.DateTimeField()
    created_on = models.DateTimeField(auto_now_add=True)
    matched_on = models.DateTimeField(null=True, blank=True)
    completed_on = models.DateTimeField(null=True, blank=True)
    comment = models.ForeignKey(Comment, related_name='cryptsy_transaction')


class CryptsyCredential(models.Model):
    privatekey = models.CharField(max_length=255, unique=True)
    publickey = models.CharField(max_length=255)
    tradekey = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='credential'
    )
    default = models.BooleanField(default=False)


def cryptsy_transaction_post_save_signal(sender, instance, **kwargs):
    instance.comment.sum_hours_donated()
    instance.comment.content_object.sum_hours()

post_save.connect(cryptsy_transaction_post_save_signal, sender=CryptsyTransaction)
