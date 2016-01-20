from re import finditer
from decimal import Decimal
from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django_markdown.models import MarkdownField
from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from hours.models import HourValue
from ..signals import _content_type_post_save
from ..signals import _translation_post_save
from ..signals import _translation_post_delete


class BaseContentModel(models.Model):
    is_link = models.BooleanField(default=False)
    is_historical = models.BooleanField(default=False)
    url = models.URLField(
        max_length=150,
        unique=False,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now=False,
        auto_now_add=True,
        unique=False,
        null=False,
        blank=False,
    )
    commented_at = models.DateTimeField(
        auto_now=False,
        auto_now_add=True,
        unique=False,
        null=False,
        blank=False,
    )

    hours_donated = models.DecimalField(
        default=0.,
        decimal_places=8,
        max_digits=20,
        blank=False,
    )
    hours_claimed = models.DecimalField(
        default=0.,
        decimal_places=8,
        max_digits=20,
        blank=False,
    )
    hours_assumed = models.DecimalField(
        default=0.,
        decimal_places=8,
        max_digits=20,
        blank=False,
    )
    hours_matched = models.DecimalField(
        default=0.,
        decimal_places=8,
        max_digits=20,
        blank=False,
    )
    name = models.CharField(
        unique=False,
        max_length=150,
        blank=False,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='user_%(class)ss',
        blank=False,
        null=False,
    )

    personal = models.BooleanField(default=False)

    sharewith = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True
    )

    language = models.ForeignKey(
        'Language',
        blank=True,
        null=True,
    )

    lang = models.ManyToManyField(
        'Language',
        blank=True,
        related_name='+',
    )

    total_donated = models.DecimalField(
        default=0.,
        decimal_places=8,
        max_digits=20,
        blank=False,
    )
    total_claimed = models.DecimalField(
        default=0.,
        decimal_places=8,
        max_digits=20,
        blank=False,
    )
    total_assumed = models.DecimalField(
        default=0.,
        decimal_places=8,
        max_digits=20,
        blank=False,
    )
    total_matched = models.DecimalField(
        default=0.,
        decimal_places=8,
        max_digits=20,
        blank=False,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        auto_now_add=False,
        unique=False,
        null=False,
        blank=False,
    )

    subscribers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="%(class)s_subscribers"
    )

    def sum_hours(self):
        self.hours_donated = Decimal(0.)
        self.hours_claimed = Decimal(0.)
        self.hours_assumed = Decimal(0.)
        self.hours_matched = Decimal(0.)
        comment_content_type = ContentType.objects.get_for_model(self)
        comments = Comment.objects.filter(
            content_type__pk=comment_content_type.pk,
            object_id=self.id
        )
        for comment in comments:
            self.hours_donated += comment.hours_donated
            self.hours_claimed += comment.hours_claimed
            self.hours_assumed += comment.hours_assumed
            self.hours_matched += Decimal(2.)*comment.hours_matched
        self.save()

    def sum_totals(self):
        self.total_donated = self.hours_donated
        self.total_claimed = self.hours_claimed
        self.total_assumed = self.hours_assumed
        self.total_matched = self.hours_matched
        if hasattr(self,'definition_goals'):
            child_objects = self.definition_goals.all()
        elif hasattr(self,'need_goals'):
            child_objects = self.definition_goals.all()
        elif hasattr(self,'goal_ideas'):
            child_objects = self.goal_ideas.all()
        elif hasattr(self,'idea_plans'):
            child_objects = self.idea_plans.all()
        elif hasattr(self, 'plan_steps'):
            child_objects = self.plan_steps.all()
        elif hasattr(self, 'step_tasks'):
            child_objects = self.step_tasks.all()
        elif hasattr(self, 'task_works'):
            child_objects = self.task_works.all()
        if 'child_objects' in locals():
            for content in child_objects:
                self.total_donated += content.total_donated
                self.total_claimed += content.total_claimed
                self.total_assumed += content.total_assumed
                self.total_matched += content.total_matched
        self.save()

    def get_remain_usd(self):
        return ((self.total_assumed+self.total_claimed)-self.total_donated)*\
            HourValue.objects.latest('created_at').value

    def not_funded_hours(self):
        return self.total_assumed+self.total_claimed-self.total_donated

    def comment_count(self):
        comment_content_type = ContentType.objects.get_for_model(self)
        return Comment.objects.filter(
            content_type__pk=comment_content_type.pk,
            object_id=self.id
        ).count()

    def __unicode__(self):
        return unicode(self.name[:50])

    def get_absolute_url(self):
        return "/"

    def get_usd(self):
        return self.total_donated*HourValue.objects.latest('created_at').value

    def translations(self):
        """
        Returns False if there is no translation
        """
        content_type = ContentType.objects.get_for_model(self)
        translations = Translation.objects.filter(
            content_type=content_type,
            object_id=self.pk
        ).exclude(default=True)

        return translations

    class Meta:
        abstract = True


class Comment(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    text = MarkdownField(blank=False)
    notify = models.BooleanField(default=True)
    created_at = models.DateTimeField(
        auto_now=False,
        auto_now_add=True,
        unique=False,
        null=False,
        blank=False,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        auto_now_add=False,
        unique=False,
        null=False,
        blank=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False,
        null=False,
    )
    hours_donated = models.DecimalField(
        default=0.,
        decimal_places=8,
        max_digits=20,
        blank=False,
    )
    hours_claimed = models.DecimalField(
        default=0.,
        decimal_places=8,
        max_digits=20,
        blank=False,
    )
    hours_assumed = models.DecimalField(
        default=0.,
        decimal_places=8,
        max_digits=20,
        blank=False,
    )
    hours_matched = models.DecimalField(
        default=0.,
        decimal_places=8,
        max_digits=20,
        blank=False,
    )

    def __unicode__(self):
        return u"Comment #%s" % self.id

    def get_absolute_url(self):
        return "/"

    def save(self, *args, **kwargs):
        "Save comment created date to parent object."
        self.sum_hours_claimed()
        self.match_hours()
        super(Comment, self).save(*args, **kwargs)
        if self.content_object:
            self.content_object.commented_at = self.created_at
            self.content_object.save()
            self.content_object.sum_hours()
            self.content_object.sum_totals()

    def delete(self, *args, **kwargs):
        "Update comment created date for parent object."
        super(Comment, self).delete(*args, **kwargs)
        comments = Comment.objects.filter(object_id=self.object_id)
        if comments:
            self.content_object.commented_at = comments.latest('created_at').created_at
        else:
            self.content_object.commented_at = self.content_object.created_at
        self.content_object.sum_totals()
        self.content_object.save()

    def sum_hours_donated(self):
        self.hours_donated = sum([tx.hours for tx in self.paypal_transaction.all()])
        #+= sum([tx.amount for tx in self.cryptsy_transaction.all()])
        self.match_hours()
        self.save()

    def sum_hours_claimed(self):
        self.hours_claimed = Decimal(0.)
        self.hours_assumed = Decimal(0.)
        for m in finditer('\{([^}]+)\}', self.text):
            token = m.group(1)
            if token:
                if token[0] == u'?':
                    try:
                        hours = float(token[1:])
                        self.hours_assumed += Decimal(hours)
                    except:
                        pass
                else:
                    try:
                        hours = float(token)
                        self.hours_claimed += Decimal(hours)
                    except:
                        pass

    def match_hours(self):
        if self.hours_claimed >= self.hours_donated:
            ratio = Decimal(1.)
        elif self.hours_claimed < self.hours_donated:
            ratio = self.hours_claimed/self.hours_donated

        self.hours_matched = Decimal(0.)
        for tx in self.paypal_transaction.all():
            tx.hours_matched = tx.hours * ratio
            self.hours_matched += tx.hours_matched

    def get_usd(self):
        return self.total_donated*HourValue.objects.latest('created_at').value

    def votes(self):
        return sum([vote.value for vote in Vote.objects.filter(comment_id=self.id)])

    def user_vote(self, user_id):
        try:
            vote = Vote.objects.get(
                comment_id=self.id,
                user_id=user_id
            )
        except Vote.DoesNotExist:
            vote = None
        return vote

    def comment_credit(self):
        return min([self.hours_claimed, self.votes()]) or Decimal(0.)


class Vote(models.Model):

    created_at = models.DateTimeField(
        auto_now=False,
        auto_now_add=True,
        unique=False,
        null=False,
        blank=False,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        auto_now_add=False,
        unique=False,
        null=False,
        blank=False,
    )

    POSITIVE = 1
    NEUTRAL = 0
    NEGATIVE = -1

    VOTE_STATES = (
        (POSITIVE, 'Positive'),
        (NEUTRAL, 'Neural'),
        (NEGATIVE, 'Negative'),
    )

    value = models.IntegerField(
        choices=VOTE_STATES,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='vote_user',
        blank=False,
        null=False
    )

    comment = models.ForeignKey(Comment, related_name='vote_comment')

    class Meta:
        unique_together = (('user', 'comment'))


class Type(models.Model):
    name = models.CharField(
        unique=False,
        max_length=150,
        blank=False,
    )

    def __unicode__(self):
        return unicode(self.name[:50])

    def get_absolute_url(self):
        return "/"


class Need(BaseContentModel):
    definition = models.ForeignKey(
    'Definition',
    blank=False,
    null=False,
    )
    content = MarkdownField(blank=False)


class Goal(BaseContentModel):
    type = models.ForeignKey(
        'Type',
        blank=False,
        null=False,
    )
    need = models.ForeignKey(
        'Need',
        blank=True,
        null=True,
    )
    reason = MarkdownField(blank=False)
    hyper_equity = models.DecimalField(
        default=0.0001,
        decimal_places=8,
        max_digits=20,
        blank=False
    )

    def get_equity(self):
        return self.hyper_equity*100


class Idea(BaseContentModel):
    description = MarkdownField(blank=False)
    summary = models.CharField(
        unique=False,
        max_length=150,
        blank=False,
    )
    goal = models.ManyToManyField(
        'Goal',
        related_name='goal_ideas',
        blank=False
    )
    super_equity = models.DecimalField(
        default=0.01,
        decimal_places=8,
        max_digits=20,
        blank=False
    )

    def get_equity(self):
        return self.super_equity*100


class Plan(BaseContentModel):
    idea = models.ForeignKey(
        'Idea',
        related_name='idea_plans',
        blank=False,
        null=False,
    )
    deliverable = MarkdownField(blank=False)
    situation = MarkdownField(blank=False)
    plain_equity = models.DecimalField(
        default=0.1,
        decimal_places=8,
        max_digits=20,
        blank=False
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='user_members',
        blank=False
    )

    def get_usd(self):
        return self.total_donated*HourValue.objects.latest('created_at').value

    def get_equity(self):
        return self.plain_equity*100


class Step(BaseContentModel):
    deliverables = models.CharField(
        unique=False,
        max_length=150,
        blank=False,
    )
    priority = models.IntegerField(
        unique=False,
        null=False,
        blank=False,
    )
    plan = models.ForeignKey(
        'Plan',
        related_name='plan_steps',
        blank=False,
        null=False,
    )
    objective = MarkdownField(blank=False)
    investables = models.CharField(
        unique=False,
        max_length=150,
        blank=False,
    )

    def get_usd(self):
        return self.total_donated*HourValue.objects.latest('created_at').value


class Task(BaseContentModel):
    priority = models.IntegerField(
            unique=False,
        null=False,
        blank=False,
    )
    step = models.ForeignKey(
        'Step',
        related_name='step_tasks',
        blank=False,
        null=False,
    )
    description = MarkdownField(blank=False)

    def get_usd(self):
        return self.total_donated*HourValue.objects.latest('created_at').value


class Work(BaseContentModel):
    task = models.ForeignKey(
        'Task',
        related_name='task_works',
        blank=False,
        null=False,
    )
    file = models.FileField(
        null=True,
        upload_to='files',
        blank=True,
    )
    parent_work_id = models.PositiveIntegerField(
        unique=False,
        null=True,
        blank=True,
    )
    description = MarkdownField(blank=False)

    def get_usd(self):
        return self.total_donated*HourValue.objects.latest('created_at').value


class Definition(models.Model):
    created_at = models.DateTimeField(
        auto_now=False,
        auto_now_add=True,
        unique=False,
        null=False,
        blank=False,
    )
    commented_at = models.DateTimeField(
        auto_now=False,
        auto_now_add=True,
        unique=False,
        null=False,
        blank=False,
    )
    defined_meaning_id = models.PositiveIntegerField(null=True, blank=True)
    definition = models.TextField()
    type = models.ForeignKey(
        'Type',
        blank=True,
        null=True,
    )
    language = models.ForeignKey(
        'Language',
        blank=True,
        null=True,
    )
    personal = models.BooleanField(default=False)
    name = models.TextField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='user_definitions',
        blank=False,
        null=False,
    )
    subscribers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="%(class)s_subscribers"
    )
    hours_donated = models.DecimalField(
        default=0.,
        decimal_places=8,
        max_digits=20,
        blank=False,
    )
    hours_claimed = models.DecimalField(
        default=0.,
        decimal_places=8,
        max_digits=20,
        blank=False,
    )
    hours_assumed = models.DecimalField(
        default=0.,
        decimal_places=8,
        max_digits=20,
        blank=False,
    )
    hours_matched = models.DecimalField(
        default=0.,
        decimal_places=8,
        max_digits=20,
        blank=False,
    )
    total_donated = models.DecimalField(
        default=0.,
        decimal_places=8,
        max_digits=20,
        blank=False,
    )
    total_claimed = models.DecimalField(
        default=0.,
        decimal_places=8,
        max_digits=20,
        blank=False,
    )
    total_assumed = models.DecimalField(
        default=0.,
        decimal_places=8,
        max_digits=20,
        blank=False,
    )
    total_matched = models.DecimalField(
        default=0.,
        decimal_places=8,
        max_digits=20,
        blank=False,
    )
    sharewith = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True
    )

    def __unicode__(self):
        return unicode(self.name[:50])

    def get_absolute_url(self):
        return "/"

    class Meta:
        unique_together = ('language', 'name', 'definition')

    def sum_hours(self):
        self.hours_donated = Decimal(0.)
        self.hours_claimed = Decimal(0.)
        self.hours_assumed = Decimal(0.)
        self.hours_matched = Decimal(0.)
        comment_content_type = ContentType.objects.get_for_model(self)
        comments = Comment.objects.filter(
            content_type__pk=comment_content_type.pk,
            object_id=self.id
        )
        for comment in comments:
            self.hours_donated += comment.hours_donated
            self.hours_claimed += comment.hours_claimed
            self.hours_assumed += comment.hours_assumed
            self.hours_matched += Decimal(2.)*comment.hours_matched
        self.save()

    def sum_totals(self):
        self.total_donated = self.hours_donated
        self.total_claimed = self.hours_claimed
        self.total_assumed = self.hours_assumed
        self.total_matched = self.hours_matched
       #for goal in self.definition_goals.all():
       #    self.total_donated += goal.hours_donated
       #    self.total_claimed += goal.hours_claimed
       #    self.total_assumed += goal.hours_assumed
       #    self.total_matched += goal.hours_matched
        self.save()

    def get_usd(self):
        return self.total_donated*HourValue.objects.latest('created_at').value

    def get_remain_usd(self):
        return ((self.total_assumed+self.total_claimed)-self.total_donated)*\
            HourValue.objects.latest('created_at').value

    def not_funded_hours(self):
        return self.total_assumed+self.total_claimed-self.total_donated

    def comment_count(self):
        comment_content_type = ContentType.objects.get_for_model(self)
        return Comment.objects.filter(
            content_type__pk=comment_content_type.pk,
            object_id=self.id
        ).count()


class Translation(models.Model):
    name = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    objective = models.TextField(blank=True, null=True)
    situation = models.TextField(blank=True, null=True)
    deliverable = models.TextField(blank=True, null=True)
    investables = models.TextField(blank=True, null=True)
    deliverables = models.TextField(blank=True, null=True)
    language = models.ForeignKey('Language')

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return "Language: %s, Content Type: %s, Object ID: %d" % (
            self.language.name,
            self.content_type,
            self.object_id
        )


class Language(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    http_accept_language = models.CharField(max_length=255, blank=True,
                                            null=True)
    omegawiki_language_id = models.PositiveIntegerField(null=True, blank=True)
    language_code = models.CharField(max_length=8)

    def __unicode__(self):
        try:
            return unicode(self.name[:50])
        except TypeError:
            return unicode(self.pk)

post_save.connect(_content_type_post_save, sender=Need)
post_save.connect(_content_type_post_save, sender=Goal)
post_save.connect(_content_type_post_save, sender=Idea)
post_save.connect(_content_type_post_save, sender=Plan)
post_save.connect(_content_type_post_save, sender=Step)
post_save.connect(_content_type_post_save, sender=Task)
post_save.connect(_content_type_post_save, sender=Work)
post_save.connect(_translation_post_save, sender=Translation)
post_delete.connect(_translation_post_delete, sender=Translation)
