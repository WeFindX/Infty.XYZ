def _translation_post_save(sender, instance, created, *args, **kwargs):
    """
    Do after translation save
    """
    # Copy fields to parent content object, if language match
    if instance.language == instance.content_object.language:
        ignored_fields = ['language', 'language_id', 'id']
        for field in instance._meta.get_all_field_names():
            if field in instance.content_object._meta.get_all_field_names():
                if field in ignored_fields:
                    continue
                if getattr(instance.content_object, field) != getattr(instance, field):
                    setattr(instance.content_object, field, getattr(instance, field))
    
    # Save the translation language to object itself for faster filtering
   #instance.content_object.lang.add(instance.language)
    instance.content_object.save()
    pass

def _translation_post_delete(sender, instance, *args, **kwargs):
	# Remove the translation language upon deletion of translation
   #instance.content_object.lang.remove(instance.language)
   #instance.content_object.save()
    pass

def _content_type_post_save(sender, instance, created, *args, **kwargs):
    """
    Create default translation
    """
    from django.contrib.contenttypes.models import ContentType
    from .models import Translation
    content_type = ContentType.objects.get_for_model(sender)

    # Get Field List from Translation model
    fields = []
    ignored_fields = ['language', 'language_id', 'id']
    for translation_field in Translation._meta.get_all_field_names():
        for instance_field in instance._meta.get_all_field_names():
            if instance_field == translation_field:
                if instance_field in ignored_fields:
                    continue
                fields.append(translation_field)

    if created:
        translation = Translation()
        translation.content_type = content_type
        translation.object_id = instance.id
        translation.language = instance.language

        for field in fields:
            setattr(translation, field, getattr(instance, field))

        translation.save()
