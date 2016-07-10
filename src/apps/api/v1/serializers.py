from rest_framework import serializers
from core.models import Goal, Idea, Plan, Translation, Language
from django.contrib.contenttypes.models import ContentType


def get_object_translation(obj, language_code):
    language = Language.objects.get(language_code=language_code)
    content_type = ContentType.objects.get_for_model(obj)
    translation = Translation.objects.get(language=language, content_type=content_type, object_id=obj.id)
    return translation


class GoalSerializer(serializers.ModelSerializer):
    detail_url = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    short_content = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()

    def get_detail_url(self, obj):
        return obj.get_absolute_url()

    def get_comments_count(self, obj):
        return obj.comment_count()

    def get_title(self, obj):
        language_code = self.context['request'].LANGUAGE_CODE
        translation = get_object_translation(obj, language_code)
        return translation.name

    def get_short_content(self, obj):
        language_code = self.context['request'].LANGUAGE_CODE
        translation = get_object_translation(obj, language_code)
        return translation.reason[:34]

    class Meta:
        model = Goal
        fields = [
            'title',
            'created_at',
            'detail_url',
            'comments_count',
            'is_link',
            'is_historical',
            'short_content',
            'id'
        ]


class IdeaSerializer(serializers.ModelSerializer):
    detail_url = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    short_content = serializers.SerializerMethodField()
    # goal = GoalSerializer(many=True)
    title = serializers.SerializerMethodField()

    def get_title(self, obj):
        language_code = self.context['request'].LANGUAGE_CODE
        translation = get_object_translation(obj, language_code)
        return translation.name

    def get_detail_url(self, obj):
        return obj.get_absolute_url()

    def get_comments_count(self, obj):
        return obj.comment_count()

    def get_short_content(self, obj):
        language_code = self.context['request'].LANGUAGE_CODE
        translation = get_object_translation(obj, language_code)
        return translation.summary[:34]

    class Meta:
        model = Idea
        fields = [
            'detail_url',
            'comments_count',
            'short_content',
            'created_at',
            'id',
            'is_link',
            'is_historical',
            'title',
        ]


class PlanSerializer(serializers.ModelSerializer):
    detail_url = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    short_content = serializers.SerializerMethodField()
    # idea = IdeaSerializer()
    remain_usd = serializers.SerializerMethodField()
    usd = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()

    def get_title(self, obj):
        language_code = self.context['request'].LANGUAGE_CODE
        translation = get_object_translation(obj, language_code)
        return translation.name

    def get_remain_usd(self, obj):
        return obj.get_remain_usd()

    def get_usd(self, obj):
        return obj.get_usd()

    def get_detail_url(self, obj):
        return obj.get_absolute_url()

    def get_comments_count(self, obj):
        return obj.comment_count()

    def get_short_content(self, obj):
        language_code = self.context['request'].LANGUAGE_CODE
        translation = get_object_translation(obj, language_code)
        return translation.deliverable[:34]

    class Meta:
        model = Plan
        fields = [
            'detail_url',
            'comments_count',
            'short_content',
            'created_at',
            'id',
            'is_link',
            'is_historical',
            'title',
            'idea',
            'remain_usd',
            'usd',
            'personal',
        ]
