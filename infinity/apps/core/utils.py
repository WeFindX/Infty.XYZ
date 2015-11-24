from os import path
from re import finditer
from django.contrib.contenttypes.models import ContentType
from django.views.generic import CreateView
from django.core.exceptions import FieldError

from django.template.loader import render_to_string
from django.views.generic import DetailView
from django.views.generic import UpdateView
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404
from django.contrib import messages
from django.shortcuts import redirect
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags

from constance import config
from users.models import User
from core.models import Language

from .forms import CommentCreateFormDetail
from .models import Comment
from .models import Translation

from users.mixins import OwnerMixin


def notify_mentioned_users(comment_instance):
    """
	notify mentioned users and unmentioned subscribers other than owner of comment
    """
    from .utils import send_mail_template
    from django.contrib.sites.models import Site

    comment = comment_instance.text
    usernames = [m.group(1) for m in finditer('\[([^]]+)\]', comment)]
    usernames = usernames[:config.MAX_MENTIONS_PER_COMMENT]

    subject_template_path = 'mail/comments/mention_notification_subject.txt'
    email_template_path = 'mail/comments/mention_notification.html'
    url = "%s/%s/detail/#comment-%s" % (comment_instance.content_type,
							  comment_instance.content_object.id,
							  comment_instance.id)
    link = path.join(path.join('http://', Site.objects.get_current().domain), url)

    mentioned_users = User.objects.filter(username__in=usernames)

    if mentioned_users.exists():
        for user in mentioned_users.iterator():
            send_mail_template(subject_template_path,
                               email_template_path,
                               recipient_list=[user.email],
                               context={'user': comment_instance.user.username,
                                        'comment': comment_instance.text,
                                        'link': link})

    unmentioned_subscribers = comment_instance.content_object.subscribers.exclude(id__in=mentioned_users)

    subject_template_path = 'mail/comments/subscriber_notification_subject.txt'
    email_template_path = 'mail/comments/subscriber_notification.html'

    for user in unmentioned_subscribers:
        if user.id != comment_instance.user.id:
            send_mail_template(subject_template_path,
                 email_template_path,
                 recipient_list=[user.email],
                 context={'user': comment_instance.user.username,
                         'comment': comment_instance.text,
                         'link': link})


def send_mail_template(
        subject_template_path,
        email_template_path,
        recipient_list,
        from_email=settings.DEFAULT_FROM_EMAIL,
        context={}):
    """
        Send email with template
    Args:
        subject_template_path(str): Subject
        email_template_path(str): Template Path
        recipient_list(list): 
        email_from(str): Email from with default argument from DEFAULT_EMAIL_FROM option
        context(dict): Django Template context
    """
    subject = render_to_string(subject_template_path, context)
    subject = ''.join(subject.splitlines())
    email = strip_tags(render_to_string(email_template_path, context))
    html_message = render_to_string(email_template_path, context)
    send_mail(subject, email, from_email, recipient_list, html_message=html_message)


class ViewTypeWrapper(object):
    def get_base_queryset(self):
        qs = super(ViewTypeWrapper, self).get_base_queryset()
        if self.request.user.is_anonymous():
            # Show entries with personal = False for anonymous users
            qs = qs.filter(personal=False)
        else:
            # Conditions description
            # Show entries with personal = False
            # Show entries with personal = True for content owners only
            # Show entries with personal = True if content shared with current user
            qs = qs.filter(
                Q(personal=False) |
                Q(personal=True, user=self.request.user) |
                Q(personal=True, sharewith=self.request.user)
            )
        return qs


class DetailViewWrapper(DetailView):
    @property
    def translation(self):
        obj = self.get_object()
        content_type = ContentType.objects.get_for_model(obj.__class__)

        try:
            language = Language.objects.get(language_code=self.request.GET.get('lang'))
        except Language.DoesNotExist:
            # Raise 404 if Language does not exist
            raise Http404

        try:
            translation = Translation.objects.get(
                language=language,
                object_id=obj.id,
                content_type=content_type
            )
        except Translation.DoesNotExist:
            translation = None

        return translation

    def get_context_data(self, **kwargs):
        context = super(DetailViewWrapper, self).get_context_data(**kwargs)

        context.update({
            'translations': Translation.objects.filter(
                object_id=self.get_object().id,
                content_type=ContentType.objects.get_for_model(
                    self.get_object().__class__
                )
            )
        })

        context.update({
            'translate_url': reverse('create-translation', kwargs={
                'model_name': self.get_object().__class__.__name__.lower(),
                'object_id': self.get_object().id
            })
        })

        content_type = ContentType.objects.get_for_model(self.get_object().__class__)
        context.update({
            'content_type': content_type.id,
            'object_id': self.get_object().id
        })

        if self.request.GET.get('lang'):
            context.update({
                'translation': self.translation
            })

        return context

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj.user == request.user:
            if obj.personal and not request.user in obj.sharewith.all():
                messages.error(request, 'You don\'t have access for this page')
                return redirect('/')
        return super(DetailViewWrapper, self).dispatch(request, *args, **kwargs)


class CommentsContentTypeWrapper(CreateView):
    model_for_list = Comment

    form_class = CommentCreateFormDetail

    @property
    def object_list(self):
        content_type = ContentType.objects.get_for_model(
            self.get_object()
        )
        object_list = self.model_for_list.objects.filter(
            content_type__pk=content_type.pk,
            object_id=self.get_object().id
        )

        return object_list.order_by('id')

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.content_type = ContentType.objects.get_for_model(self.get_object())
        self.object.object_id = self.get_object().id
        self.object.save()

        notify_mentioned_users(self.object)

		# temporary: subscribe commenter
        self.object.content_object.subscribers.add(self.request.user)
        self.object.content_object.save()

        # payments fields
        amount = form.cleaned_data.get('amount', False)
        currency = form.cleaned_data.get('currency', False)

        if amount and currency:
            self.request.session['amount'] = str(amount)
            self.request.session['currency'] = currency
            return redirect(reverse("payments:transaction_paypal", kwargs={'comment_id': self.object.id}))

        return super(CommentsContentTypeWrapper, self).form_valid(form)


def notify_new_sharewith_users(list_of_users, object_instance):

    from django.contrib.sites.models import Site
    subject_template_path = 'mail/content/sharewith_notification_subject.txt'
    email_template_path = 'mail/content/sharewith_notification.html'
    url = '%s/%s/detail' % (object_instance.__class__.__name__.lower(),
							object_instance.id)
    link = path.join(path.join('http://', Site.objects.get_current().domain), url)

    for user in list_of_users:
        send_mail_template(subject_template_path,
            email_template_path,
            recipient_list=[user.email],
            context={'user': user.username,
                    'content_object': object_instance,
                    'link': link})

class UpdateViewWrapper(OwnerMixin, UpdateView):

    def form_valid(self, form):
        """
        If the form is valid, send notifications.
        """

        all_sharewith_users = form.cleaned_data.get('sharewith', False)
        if all_sharewith_users:
            new_sharewith_users = all_sharewith_users.exclude(id__in=self.object.sharewith.all())
            # Send email logick here
            notify_new_sharewith_users(new_sharewith_users, self.object)
		# The rest:
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super(UpdateViewWrapper, self).form_valid(form)


class CreateViewWrapper(CreateView):

    def form_valid(self, form):
        """
        If the form is valid, send notifications.
        """

        all_sharewith_users = form.cleaned_data.get('sharewith', False)
        if all_sharewith_users:
            # Send email logick here
            notify_new_sharewith_users(all_sharewith_users, self.object)
        self.object.subscribers.add(self.request.user)
        return super(CreateViewWrapper, self).form_valid(form)

