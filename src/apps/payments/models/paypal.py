from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.db.models.signals import pre_save

from core.models import Comment
from djmoney_rates.utils import convert_money
from hours.models import HourValue


class PayPalTransaction(models.Model):
    CREATED = 'CREATED'
    COMPLETED = 'COMPLETED'
    INCOMPLETE = 'INCOMPLETE'
    ERROR = 'ERROR'
    REVERSALERROR = 'REVERSALERROR'

    PAYMENT_EXEC_STATUSES = (
        (CREATED, 'Created'),
        (COMPLETED, 'Completed'),
        (INCOMPLETE, 'Incomplete'),
        (ERROR, 'Error'),
        (REVERSALERROR, 'Reversalerror')
    )

    payKey = models.CharField(max_length=255)

    paymentExecStatus = models.CharField(
        choices=PAYMENT_EXEC_STATUSES,
        max_length=255
    )

    currency = models.CharField(max_length=3)

    created_at = models.DateTimeField(
        auto_now=True,
        unique=False,
        null=False,
        blank=False,
    )
    amount = models.DecimalField(
        null=False,
        max_digits=16,
        decimal_places=2,
        blank=False,
    )

    sender_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='sender_user_transaction',
        blank=True,
        null=True
    )

    receiver_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='receiver_user_transaction',
        blank=True,
        null=True
    )

    hours = models.DecimalField(
        null=False,
        max_digits=20,
        decimal_places=8,
        blank=False,
        default=0,
    )

    hours_matched = models.DecimalField(
        default=0.,
        decimal_places=8,
        max_digits=20,
        blank=False,
    )

    comment = models.ForeignKey(Comment, related_name='paypal_transaction')

    def __unicode__(self):
        return u"Transaction #%s" % self.id

    def get_absolute_url(self):
        return "/"

    def compute_hours(self):
        self.hours = convert_money(self.amount, self.currency,
                                   'USD')/HourValue.objects.latest('created_at').value


def comment_pre_save_signal(sender, instance, **kwargs):
    instance.compute_hours()

def comment_save_signal(sender, instance, **kwargs):
    instance.comment.sum_hours_donated()
    instance.comment.match_hours()
    instance.comment.content_object.sum_hours()

pre_save.connect(comment_pre_save_signal, sender=PayPalTransaction)
post_save.connect(comment_save_signal, sender=PayPalTransaction)
