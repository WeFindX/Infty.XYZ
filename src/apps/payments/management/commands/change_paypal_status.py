from django.core.management.base import BaseCommand
from ...models import PayPalTransaction
from ...payment.systems import PayPal


class Command(BaseCommand):

    help = """
    Update payment status for each transaction if the PayPal transaction has been changed
    """

    def handle(self, *args, **kwargs):
        paypal = PayPal()
        for transaction in PayPalTransaction.objects.filter(
                paymentExecStatus=PayPalTransaction.CREATED
        ):
            paymentExecStatus = paypal.get_payment_information(
                transaction.payKey)['status'][0]

            if (paymentExecStatus != PayPalTransaction.CREATED and
                    transaction.paymentExecStatus == PayPalTransaction.CREATED):
                transaction.paymentExecStatus = paymentExecStatus

                transaction.save()

                if paymentExecStatus == transaction.paymentExecStatus:
                    self.stdout.write('Updated transaction with %d id' % transaction.id)
