from django.db import models
from django.conf import settings


class CoinAddress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='address',
        null=True,
        blank=True
    )

    currency_code = models.CharField(max_length=6)
    address = models.CharField(max_length=255)

    class Meta:
        unique_together = (('currency_code', 'address'),)
