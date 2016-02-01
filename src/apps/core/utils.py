from django.utils.translation import ugettext as _
from os import path
from re import finditer
from django.contrib.contenttypes.models import ContentType
from django.views.generic import CreateView
from django.core.exceptions import FieldError

from django.template.loader import render_to_string
from django.views.generic import DetailView
from django.views.generic import UpdateView
from django.views.generic import View
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags
from django.utils.translation import ugettext as _
from constance import config
from users.models import User
from users.forms import ConversationInviteForm
from core.models import Language

from .forms import CommentCreateFormDetail
from .models import Comment
from .models import Translation
from .models import Definition

from users.mixins import OwnerMixin

import json
import requests


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
        content_type = ContentType.objects.get_for_model(self.obj.__class__)

        try:
            language = Language.objects.get(language_code=self.request.GET.get('lang'))
        except Language.DoesNotExist:
            # Raise 404 if Language does not exist
            raise Http404

        try:
            translation = Translation.objects.get(
                language=language,
                object_id=self.obj.id,
                content_type=content_type
            )
        except Translation.DoesNotExist:
            translation = None

        return translation

    def get_context_data(self, **kwargs):
        context = super(DetailViewWrapper, self).get_context_data(**kwargs)
        form = None
        conversation_form = ConversationInviteForm()
        content_type = ContentType.objects.get_for_model(self.obj.__class__)
        next_url = "?next=%s" % self.request.path
        subscribers = self.obj.subscribers.filter(pk=self.request.user.id)

        translations = Translation.objects.filter(
            object_id=self.obj.id,
            content_type=ContentType.objects.get_for_model(
                self.get_object().__class__
            )
        )

        if self.request.user.__class__.__name__ not in [u'AnonymousUser']:
            form = self.get_form_class()

        conversation_form.helper.form_action = reverse('user-conversation-invite', kwargs={
            'object_name': self.obj.__class__.__name__,
            'object_id': self.obj.id
        }) + next_url

        translate_url = reverse('create-translation', kwargs={
            'model_name': self.obj.__class__.__name__.lower(),
            'object_id': self.obj.id
        })

        context.update({
            'form': form,
            'object_list': self.object_list,
            'is_subscribed': subscribers.exists(),
            'conversation_form': conversation_form,
            'translations': translations,
            'translate_url': translate_url,
            'content_type': content_type.id,
            'object_id': self.obj.id
        })

        if self.request.GET.get('lang'):
            context.update({
                'translation': self.translation
            })

        return context

    def dispatch(self, request, *args, **kwargs):
        self.obj = self.get_object()
        if not self.obj.user == request.user:
            if self.obj.personal and not request.user in self.obj.sharewith.all():
                messages.error(request, 'You don\'t have access for this page')
                return redirect('/')
        return super(DetailViewWrapper, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(
            self.request, _(
                "%s succesfully created" %
                self.form_class._meta.model.__name__))
        return self.request.path


class CommentsContentTypeWrapper(CreateView):
    model_for_list = Comment

    form_class = CommentCreateFormDetail

    def get_success_url(self):
        messages.success(
            self.request, _(
                "%s succesfully created" %
                self.form_class._meta.model.__name__))
        success_url = "%s#comment-%d" % (self.request.path, self.object.id)
        return success_url

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


class JsonView(View):

    def json(self, data={}):

        return JsonResponse(data, safe=False)


def WikiDataSearch(name, language, return_response=False):
    url = 'https://www.wikidata.org/w/api.php?action=wbsearchentities&search=%s&language=%s&format=json' % \
        (name, language)
    dicts = json.loads(requests.get(url).content)['search']

    if return_response:
        return dicts

    results = []

    for item in dicts:
        if 'match' in item.keys():
            expression = item['match']['text']
        if 'aliases' in item.keys():
            aliases = '; '.join(item['aliases'])
        if 'description' in item.keys():
            description = item['description']
        else:
            continue

        if 'description' in item.keys():
            if item['description'] == 'Wikimedia disambiguation page':
                continue
            if item['description'] == 'Wikipedia disambiguation page':
                continue

        try:
            if expression == aliases:
                aliases = ''
            else:
                aliases = ' - ' + aliases
        except:
            aliases = ''

        results.append([expression, aliases + description, item['title'][1:]])

    return results


def WikiDataGet(concept_q, language):
    url = 'https://www.wikidata.org/w/api.php?action=wbgetentities&ids=%s&languages=%s&format=json' % \
        (concept_q, language)
    dicts = json.loads(requests.get(url).content)

    try:
        expression = dicts['entities'][concept_q]['labels'][language]['value']
        try:
            try:
                definition = dicts['entities'][concept_q]['descriptions'][language]['value']
            except:
                dicts = WikiDataSearch(expression, language, return_response=True)
                item = dicts[next(index for (index, d) in enumerate(dicts) if d["id"] == concept_q)]
                expression = item['match']['text']
                definition = item['description']
            return {'expression': expression,
                    'definition': definition,
                    'success': True}
        except:
            return {'success': False}
    except:
        return {'success': False}

    return {'success': False}


def LookupCreateDefinition(defined_meaning_id, language):
    # try to retrieve by .defined_meaning_id and language
    definitions = Definition.objects.filter(defined_meaning_id=defined_meaning_id,
                                            language=language)
    if definitions.exists():
        return definitions.first()

    else:
        # query WikiData API, and create new definition based on response
        concept = WikiDataGet('Q' + str(defined_meaning_id), language.language_code)
        print concept
        if concept['success']:
            definition = Definition.objects.create(
                name=concept['expression'],
                definition=concept['definition'],
                language=language,
                defined_meaning_id=defined_meaning_id,
                user=User.objects.get(pk=1)
            )
            definition.save()
            return definition
