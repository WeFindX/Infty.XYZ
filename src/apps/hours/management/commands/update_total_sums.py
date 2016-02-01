from django.core.management.base import BaseCommand, CommandError

from core.models import Goal, Idea, Plan, Step, Task, Work

class Command(BaseCommand):
    args = '<>'
    help = 'Updates the totals hours on each content type from Work to Goal.'

    def handle(self, *args, **options):
        try:
            for w in Work.objects.all():
                w.sum_totals()
                w.save()

            for t in Task.objects.all():
                t.sum_totals()
                t.save()

            for s in Step.objects.all():
                s.sum_totals()
                s.save()

            for p in Plan.objects.all():
                p.sum_totals()
                p.save()

            for i in Idea.objects.all():
                i.sum_totals()
                i.save()

            for g in Goal.objects.all():
                g.sum_totals()
                g.save()
            self.stdout.write('Sums update succeeded.')
        except:
            self.stdout.write('Sums update failed.')
