from django.core.management.base import BaseCommand
from ...models import CryptsyTransaction
from ...cryptsy.v2 import Cryptsy


class Command(BaseCommand):
    help = "Synchronize local cryptsy transactions"

    def handle(self, *args, **kwargs):

        local_transactions = CryptsyTransaction.objects.filter(trxid=None)

        for local_transaction in local_transactions:
            cryptsy = Cryptsy(
                local_transaction.sender_credential.publickey,
                local_transaction.sender_credential.privatekey
            )
            cryptsy_transactions = cryptsy.withdrawals()['data']

            for cryptsy_transaction in cryptsy_transactions:
                if cryptsy_transaction['timestamp'] == local_transaction.timestamp:
                    local_transaction.trxid = cryptsy_transaction['trxid']
                    local_transaction.save()

                    if local_transaction.trxid:
                        self.stdout.write('Transaction updated')
