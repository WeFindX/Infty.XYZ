from django.core.management import BaseCommand
from django.contrib.contenttypes.models import ContentType

from core.models import Translation
from core.models import Need, Goal, Idea, Plan, Step, Task, Work
from core.models import Language

class Command(BaseCommand):
    help = 'update BaseContentModel.lang based on existing translations for each of content item'


    def handle(self, *args, **options):
        content_types = ContentType.objects.get_for_models(Need, Goal, Idea, Plan, Step, Task, Work)

        for model, content_type in content_types.items():
            for instance in model.objects.all():

                translations = Translation.objects.filter(
                    content_type=content_type,
                    object_id=instance.pk
                )

                tr_languages = [translation.language 
                                for translation in translations]

                # add translations
                if translations:
                    for translation in translations:
                        instance.lang.add(translation.language)

                # remove translations
                for language in instance.lang.all():
                    if language not in tr_languages:
                        instance.lang.remove(language)

                instance.save()
