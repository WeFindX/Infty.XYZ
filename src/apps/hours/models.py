from django.db import models
from django.conf import settings

UserModelName = settings.AUTH_USER_MODEL

class HourValue(models.Model):

    value = models.DecimalField(
        default=25.,
        decimal_places=8,
        max_digits=20,
        blank=False,
    )

    date = models.CharField(
        unique=False,
        max_length=15,
        blank=False,
    )

    created_at = models.DateTimeField(
        auto_now=False,
        auto_now_add=True,
        unique=False,
        null=False,
        blank=False,
    )
    updated_at = models.DateTimeField(
        auto_now=False,
        auto_now_add=True,
        unique=False,
        null=False,
        blank=False,
    )

    def __unicode__(self):
        return "%s, value: (%s, %s)" % (self.created_at, self.date, self.value)
