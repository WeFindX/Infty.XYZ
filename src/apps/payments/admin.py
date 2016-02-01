from django.contrib import admin

from .models import PayPalTransaction
from .models import CryptsyCredential
from .models import CoinAddress
from .models import CryptsyTransaction


admin.site.register(PayPalTransaction)
admin.site.register(CryptsyCredential)
admin.site.register(CoinAddress)
admin.site.register(CryptsyTransaction)
