from django.core.management import BaseCommand
from django.contrib.contenttypes.models import ContentType

from core.models import Translation
from core.models import Need, Goal, Idea, Plan, Step, Task, Work
from core.models import Language


class Command(BaseCommand):
    help = 'generate default translation for each of content types'

    def handle(self, *args, **options):
        content_types = ContentType.objects.get_for_models(Need, Goal, Idea, Plan, Step, Task, Work)

        for model, content_type in list(content_types.items()):
            for instance in model.objects.all():

                translations = Translation.objects.filter(
                    content_type=content_type,
                    object_id=instance.pk
                )

                if translations:
                    continue

                fields = []

                ignored_fields = ['language', 'language_id', 'id']

                for translation_field in Translation._meta.get_all_field_names():
                    for instance_field in instance._meta.get_all_field_names():
                        if instance_field == translation_field:
                            if instance_field in ignored_fields:
                                continue
                            fields.append(translation_field)

                translation = Translation()
                translation.content_type = content_type
                translation.object_id = instance.id

                if not instance.language:
                    # [Assuming content that has no language set, is English]
                    instance.language = Language.objects.get(id=85)

                instance.save()

                translation.language = instance.language

                for field in fields:
                    setattr(translation, field, getattr(instance, field))

                translation.save()
