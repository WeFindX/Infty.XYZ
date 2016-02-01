from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save

from allauth.account.adapter import DefaultAccountAdapter
from users.models import User
from core.models import Language
from .app_settings import app_settings


UserModelName = settings.AUTH_USER_MODEL


class InvitationLetterTemplate(models.Model):
    language = models.OneToOneField(Language)
    body = models.TextField()

    def __unicode__(self):
        return "%s" % self.language


class InvitationOption(models.Model):
    user = models.OneToOneField(UserModelName)
    invitations_left = models.PositiveIntegerField(default=3)

    def __unicode__(self):
        return "User: %s, Invitations left: %s" % (self.user, self.invitations_left)


class Invitation(models.Model):
    sender = models.ForeignKey(
        UserModelName,
        related_name='sender_invites'
    )

    email = models.EmailField()

    invited = models.BooleanField(default=False)

    token = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    def __unicode__(self):
        return "Invitation for: %s" % self.email

    def get_invitation_url(self):
        from django.contrib.sites.models import Site
        from django.core.urlresolvers import reverse
        site = Site.objects.get_current()
        return "http://%s%s" % (
            site.domain,
            reverse('invite:token', kwargs={'token': self.token})
        )


class InvitationsAdapter(DefaultAccountAdapter):

    def is_open_for_signup(self, request):

        social_account = request.session.get('socialaccount_sociallogin')
        if social_account:
            social_account = social_account.get('account')
            if social_account:
                if social_account.get('provider') == 'github':
                    return True

        if hasattr(request, 'session') and request.session.get('invitation'):
            return True
        elif app_settings.INVITATION_ONLY is True:
            # Site is ONLY open for invites
            return False
        else:
            # Site is open to signup
            return True


def _invitation_created(sender, instance, created, *args, **kwargs):
    from uuid import uuid4
    if created:
        instance.token = uuid4().hex
        instance.save()


def _user_created(sender, instance, created, *args, **kwargs):
    if created:
        InvitationOption.objects.create(user=instance)

post_save.connect(_invitation_created, sender=Invitation)
post_save.connect(_user_created, sender=User)
