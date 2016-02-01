from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.core import validators
from django.utils import timezone
from django.db.models import signals
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.contrib.auth.models import (
    BaseUserManager, PermissionsMixin, AbstractBaseUser
)

from .signals import user_pre_save
from .signals import user_post_save
from .signals import conversation_post_save

from core.models import Comment
from decimal import Decimal


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, is_superuser, **extra_fields):
        email = self.normalize_email(email)

        user = self.model(
            email=email,
            is_superuser=is_superuser,
            is_staff=is_superuser,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        return self._create_user(email, password, True, **extra_fields)


class Relationship(models.Model):
    from_person = models.ForeignKey('User', related_name='from_people')
    to_person = models.ForeignKey('User', related_name='to_people')


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        _('username'),
        max_length=30,
        unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[
            validators.RegexValidator(
                r'^[\w.@+-]+$',
                _('Enter a valid username. This value may contain only '
                  'letters, numbers ' 'and @/./+/-/_ characters.')
            ),
        ],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), blank=True, unique=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    about = models.TextField(blank=True)
    friends = models.ManyToManyField('self', symmetrical=False, through='Relationship')

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        return unicode(self)

    def get_short_name(self):
        return unicode(self)

    def __unicode__(self):
        return unicode(self.username)

    def get_absolute_url(self):
        return "/"

    def add_relationship(self, person, symm=False):
        """ Add relationship with symmetrical False by default
        """
        relationship, created = Relationship.objects.get_or_create(
            from_person=self,
            to_person=person,
        )

        if symm:
            person.add_relationship(self, True)

        return relationship

    def remove_relationship(self, person, symm=False):
        """ Remove relationship with symmetrical False
        """
        Relationship.objects.filter(
            from_person=self,
            to_person=person,
        ).delete()
        if symm:
            # avoid recursion by passing `symm=True`
            person.remove_relationship(self, True)

    def get_relationships(self):
        """ Get all user relationships
        """
        return self.friends.filter(
            to_people__from_person=self
        )

    def have_relationship_with(self, person):
        """ Get relationship between users
        """
        rel = self.get_relationships().filter(
            to_people__to_person=person,
            from_people__from_person=person
        )

        return rel.exists()

    def get_comment_credit(self):
        credit = Decimal(0.)
        for comment in Comment.objects.filter(user_id=self.id):
            credit += comment.comment_credit()
        return credit


class ConversationInvite(models.Model):
    token = models.CharField(max_length=255)
    redirect_url = models.URLField()
    user = models.OneToOneField(User)
    expired = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    email = models.EmailField()

    def get_conversation_url(self):
        current_site_instance = Site.objects.get_current()
        return "http://%s%s" % (
            current_site_instance.domain,
            reverse('user-conversation-invite', kwargs={'token': self.token})
        )


signals.pre_save.connect(user_pre_save, sender=User)
signals.post_save.connect(user_post_save, sender=User)
signals.post_save.connect(conversation_post_save, sender=ConversationInvite)
