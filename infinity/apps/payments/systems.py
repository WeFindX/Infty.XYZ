from urllib.parse import urlencode
from urllib.parse import parse_qs
import collections

from http import client

from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

from .models import PayPalTransaction
from .models import CryptsyCredential
from .models import CoinAddress
from .models import CryptsyTransaction
from .cryptsy import v2
from .exceptions import PayPalException

from constance import config


class PayPalException(Exception):
    pass


class CryptsyPay(object):
    def __init__(self, publickey):
        self.credential = CryptsyCredential.objects.get(
            publickey=publickey
        )

        self.private_key = self.credential.privatekey
        self.public_key = self.credential.publickey
        self.trade_key = self.credential.tradekey
        current_site = Site.objects.get_current()
        notificationtoken = 'http://%s%s' % (
            current_site.domain, reverse('cryptsy_notification_token', kwargs={
                'username': self.credential.user.username,
                'credential_id': self.credential.id
            })
        )
        self.notification_token = notificationtoken

    def make_payment(self, comment_object, address, amount, currency_id):
        cryptsy = v2.Cryptsy(self.public_key, self.private_key)
        result = cryptsy.withdraw(
            self.trade_key,
            address,
            amount,
            self.notification_token,
            currency_id
        )

        currency = next((item for item in cryptsy.currencies()['data']
                    if item["id"] == str(currency_id)))

        try:
            destination_address = CoinAddress.objects.get(
                address=address
            )
        except CoinAddress.DoesNotExist:
            destination_address = CoinAddress.objects.create(
                address=address,
                currency_code=currency['code']
            )

        transaction = cryptsy.withdrawals(limit=1)
        transaction = transaction["data"][0]

        if result['success']:
            CryptsyTransaction.objects.create(
                address=destination_address,
                amount=amount,
                message=result['data']['withdraw_id'],
                timestamp=transaction['timestamp'],
                datetime=transaction['datetime'],
                fee=transaction['fee'],
                timezone=transaction['timezone'],
                comment=comment_object,
                sender_credential=self.credential
            )

        return result


class PayPal(object):
    def __init__(self, returnUrl, currency='USD', error_language='en_US'):
        # Set our headers
        self.headers = {
            'X-PAYPAL-SECURITY-USERID': config.PAYPAL_SECURITY_USERID,
            'X-PAYPAL-SECURITY-PASSWORD': config.PAYPAL_SECURITY_PASSWORD,
            'X-PAYPAL-SECURITY-SIGNATURE': config.PAYPAL_SECURITY_SIGNATURE,
            'X-PAYPAL-SERVICE-VERSION': '1.1.0',
            'X-PAYPAL-REQUEST-DATA-FORMAT': 'NV',
            'X-PAYPAL-RESPONSE-DATA-FORMAT': 'NV'
        }

        if config.PAYPAL_MODE == 'live':
            self.sandbox = False
        elif config.PAYPAL_MODE == 'sandbox':
            self.sandbox = True

        if self.sandbox:
            self.headers['X-PAYPAL-APPLICATION-ID'] = 'APP-80W284485P519543T'
        else:
            self.headers['X-PAYPAL-APPLICATION-ID'] = config.PAYPAL_APPLICATION_ID

        self.returnUrl = returnUrl
        self.cancelUrl = config.PAYPAL_CANCEL_URL
        self.currency = currency
        self.error_language = error_language

    def get_payment_information(self, payKey):
        """ Get payment information by payKey
        """
        if self.sandbox:
            conn = client.HTTPConnection("svcs.sandbox.paypal.com", port=443)
        else:
            conn = client.HTTPConnection("svcs.paypal.com", port=443)
        params = collections.OrderedDict()
        params['payKey'] = payKey
        params['requestEnvelope.errorLanguage'] = self.error_language
        enc_params = urlencode(params)
        conn.request(
            "POST",
            "/AdaptivePayments/PaymentDetails/",
            enc_params,
            self.headers
        )
        response = conn.getresponse()
        data = parse_qs(response.read())
        return data

    def adaptive_payment(self,
                         comment_object,
                         receiver_amount,
                         receiver_user,
                         sender_user
                         ):
        """ Make adaprive payments
        Returns:
            dict
        """

        # Set our POST Parameters
        params = collections.OrderedDict()
        params['requestEnvelope.errorLanguage'] = self.error_language
        params['requestEnvelope.detailLevel'] = 'ReturnAll'
        params['reverseAllParallelPaymentsOnError'] = 'true'
        params['returnUrl'] = self.returnUrl
        params['cancelUrl'] = self.cancelUrl
        params['actionType'] = 'PAY'
        params['currencyCode'] = self.currency
        params['feesPayer'] = 'EACHRECEIVER'

        params['receiverList.receiver(0).email'] = receiver_user.email
        params['receiverList.receiver(0).amount'] = receiver_amount

        # Add Client Details
        params['clientDetails.ipAddress'] = '127.0.0.1'
        params['clientDetails.deviceId'] = 'mydevice'
        params['clientDetails.applicationId'] = 'PayNvpDemo'

        enc_params = urlencode(params)

        # Connect to sand box and POST.
        if self.sandbox:
            conn = client.HTTPSConnection("svcs.sandbox.paypal.com", port=443)
        else:
            conn = client.HTTPSConnection("svcs.paypal.com", port=443)

        conn.request(
            "POST",
            "/AdaptivePayments/Pay/",
            enc_params,
            self.headers
        )
        response = conn.getresponse()

        # Get the reply and print it out.
        data = parse_qs(response.read())

        if data.get('error(0).message'):
            raise PayPalException(data.get('error(0).message'))

        # Set pay key

        try:
            payKey = data['payKey'][0]
        except KeyError:
            raise PayPalException(data)

        transaction = PayPalTransaction.objects.create(
            comment=comment_object,
            currency=self.currency,
            amount=receiver_amount,
            sender_user=sender_user,
            receiver_user=receiver_user,
            paymentExecStatus=getattr(PayPalTransaction,
                                      data['paymentExecStatus'][0]),
            payKey=data['payKey'][0]
        )

        result = {
            'status': response.status,
            'reason': response.reason,
            'data': data,
            'transaction_object': transaction
        }

        if self.sandbox:
            result['pay_url'] = 'https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_ap-payment&paykey=%s' % payKey
        else:
            result['pay_url'] = 'https://www.paypal.com/cgi-bin/webscr?cmd=_ap-payment&paykey=%s' % payKey

        return result
