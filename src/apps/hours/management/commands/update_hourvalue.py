from django.core.management.base import BaseCommand, CommandError
from hours.models import HourValue
from django.conf import settings
from decimal import Decimal

import fred

class Command(BaseCommand):
    args = '<>'
    help = 'Updates the hour price.'

    def handle(self, *args, **options):
        try:
            fred.key(settings.FRED_KEY)
            last_observation = fred.observations(settings.FRED_SERIES)['observations'][-1]

            HourValue(value=Decimal(last_observation['value']),
                      date=last_observation['date']).save()

            self.stdout.write('Written HourValue update.')
        except:
            self.stdout.write('Problem writing HourValue.')
