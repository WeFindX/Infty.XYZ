from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy
from django import forms

import requests
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from clever_selects.form_fields import ChainedModelChoiceField

from .models import CryptsyCredential
from .models import CoinAddress
from .fields import UserChoiceField
from .cryptsy.v2 import Cryptsy

from decimal import Decimal
from hours.models import HourValue

class CoinAddressForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CoinAddressForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout.append(Submit('save', _('Save')))

    class Meta:
        model = CoinAddress
        exclude = [
            'user'
        ]


class CryptsyTransactionForm(forms.Form):
    amount = forms.DecimalField()
    currency = forms.ChoiceField()
    recipient_username = UserChoiceField()
    recipient_address = ChainedModelChoiceField(
        parent_field='recipient_username',
        ajax_url=reverse_lazy('ajax_chained_view'),
        model=CoinAddress
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.comment_model = kwargs.pop('comment_model')
        super(CryptsyTransactionForm, self).__init__(*args, **kwargs)
        self.initial['recipient_username'] = self.comment_model.user.id
        cryptsy_credential = self.request.user.credential.get(default=True)
        cryptsy = Cryptsy(
            cryptsy_credential.publickey,
            cryptsy_credential.privatekey
        )
        response = requests.get('https://api.cryptsy.com/api/v2/currencies')
        currencies = response.json()
        balances = cryptsy.balances()['data']['available']

        balances_with_currencies = []

        for i, currency in enumerate(currencies['data']):
            if balances[currency['id']] > 0:
                tmp = currency['id'], '%s (%s)' % (currency['code'], balances[currency['id']])
                balances_with_currencies.append(tmp)

        self.fields['currency'].choices = balances_with_currencies

        self.helper = FormHelper(self)
        self.helper.layout.append(Submit('transaction_form', _('Send')))
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-8'


class PayPalTransactionForm(forms.Form):
    recipient_username = UserChoiceField()
    amount = forms.IntegerField()

    USD = 0
    EUR = 1

    CURRENCIES = (
        (USD, _("USD")),
        (EUR, _("EUR"))
    )

    currency = forms.ChoiceField(choices=CURRENCIES)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.comment_model = kwargs.pop('comment_model')
        super(PayPalTransactionForm, self).__init__(*args, **kwargs)
        self.initial['recipient_username'] = self.comment_model.user.id
        self.initial['amount'] = max(Decimal(0), round((self.comment_model.hours_assumed+\
                                                 self.comment_model.hours_claimed-\
                                                 self.comment_model.hours_donated)*\
                                                 HourValue.objects.latest('created_at').value,2))
                                

        self.helper = FormHelper(self)
        self.helper.layout.append(Submit('transaction_form', _('Send')))
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-8'


class CryptsyCredentialForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CryptsyCredentialForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout.append(Submit('transaction_form', _('Save')))
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-8'

    class Meta:
        model = CryptsyCredential
        exclude = ['user', 'default']
