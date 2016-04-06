from itertools import chain

from django.db.models import Q
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.views.generic import FormView
from django.views.generic import TemplateView
from django.views.generic import RedirectView
from django.utils import timezone
from django.conf import settings
from django.utils import translation as trans_settings
from django.contrib.contenttypes.models import ContentType

from users.decorators import ForbiddenUser
from users.models import User
from hours.models import HourValue
from core.models import Language

from ..forms import ContentTypeSubscribeForm
from ..forms import SearchForm
from ..models import Translation
from ..models import Need
from ..models import Goal
from ..models import Idea
from ..models import Plan
from ..models import Step
from ..models import Task
from ..models import Work


class SetLanguageView(RedirectView):

    url = '/'

    def get(self, request, *args, **kwargs):
        response = super(SetLanguageView, self).get(request, *args, **kwargs)
        lang = kwargs.get('lang')
        if lang:
            # To set the language for this session
            request.session[trans_settings.LANGUAGE_SESSION_KEY] = lang
            # To set it as a cookie
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang,
                                max_age=settings.LANGUAGE_COOKIE_AGE,
                                path=settings.LANGUAGE_COOKIE_PATH,
                                domain=settings.LANGUAGE_COOKIE_DOMAIN)
        return response


@ForbiddenUser(forbidden_usertypes=[u'AnonymousUser'])
class ContentTypeSubscribeFormView(FormView):
    """
    Subscribe/unsubscribe view
    """
    form_class = ContentTypeSubscribeForm
    template_name = "content_type_subscribe_form.html"

    def get_success_url(self):
        form = self.get_form()
        content_type_id = form.data.get('content_type')
        object_id = form.data.get('object_id')

        content_type = ContentType.objects.get(pk=content_type_id)

        return reverse("%s-detail" % content_type.model, kwargs={
            'slug': object_id
        })

    def form_valid(self, form):
        content_type = form.cleaned_data.get('content_type')
        object_id = form.cleaned_data.get('object_id')
        model = content_type.model_class()
        try:
            object_instance = model.objects.get(id=object_id)
        except model.DoesNotExist:
            messages.error(self.request, "Object with this id not found")
            return super(ContentTypeSubscribeFormView, self).form_invalid(form)

        if object_instance.subscribers.filter(pk=self.request.user.id):
            object_instance.subscribers.remove(self.request.user)
        else:
            object_instance.subscribers.add(self.request.user)

        object_instance.save()

        return super(ContentTypeSubscribeFormView, self).form_valid(form)


class IndexView(TemplateView):
    template_name = 'home.html'
    dropdown_list = [0, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]

    def post(self, request, *args, **kwargs):
        if self.request.POST.get('needs'):
            self.request.session['needs_number'] = int(self.request.POST['needs'])
        if self.request.POST.get('goals'):
            self.request.session['goals_number'] = int(self.request.POST['goals'])
        if self.request.POST.get('ideas'):
            self.request.session['ideas_number'] = int(self.request.POST['ideas'])
        if self.request.POST.get('plans'):
            self.request.session['plans_number'] = int(self.request.POST['plans'])
        if self.request.POST.get('steps'):
            self.request.session['steps_number'] = int(self.request.POST['steps'])
        if self.request.POST.get('tasks'):
            self.request.session['tasks_number'] = int(self.request.POST['tasks'])
        if self.request.POST.get('works'):
            self.request.session['works_number'] = int(self.request.POST['works'])

        return redirect(reverse('home'))

    def get_translation_by_instance(self, instance, content_type, language):
        translation = Translation.objects.filter(
            content_type=content_type,
            object_id=instance.id,
            language=language.id
        )

        return translation.first()

    def get_context_data(self, **kwargs):

        current_time = timezone.now()
        language = Language.objects.get(language_code=self.request.LANGUAGE_CODE)

        items = {#'needs': 64,
                 'goals': 128,
                 'ideas': 128,
                 'plans': 128,
                 #'steps': 64,
                 #'tasks': 64,
                 #'works': 64
                }

        for i, key in enumerate(items.keys()):
            if self.request.session.get('%s_number' % key):
                items[key] = self.request.session['%s_number' % key]

        search_form = SearchForm(self.request.GET or None)
        if search_form.is_valid():
            search_query = search_form.cleaned_data.get('s')
            q_search = Q(name__icontains=search_query)
        else:
            q_search = Q()

        # Prepare base content access filters
        INBOX = False
        if self.request.user.is_authenticated():
            if self.request.resolver_match.url_name == 'inbox':
                INBOX = True
                q_object = (
                    (
                        Q(personal=True, user=self.request.user) |
                        Q(personal=True, sharewith=self.request.user)
                    )
                    & q_search
                )
            else:
                q_object = (
                    (
                    Q(personal=False)
                    )
#                     & Q(lang=language)
                    & q_search
                )
        else:
            q_object = (
                (
                Q(personal=False)
                )
#                 & Q(lang=language)
                & q_search
            )

        # Get Content Types for Goal, Idea, Plan, Step, Task
        instances = {}
        #content_types = ContentType.objects.get_for_models(Need, Goal, Idea, Plan, Step, Task, Work)
        content_types = ContentType.objects.get_for_models(Goal, Idea, Plan)

        for model_class, translations in content_types.items():
            model_class_lower_name = model_class.__name__.lower() + 's'
            instances[model_class_lower_name] = model_class.objects.filter(
                q_object
            ).order_by('-commented_at').distinct()[:items[model_class_lower_name]]

        instances_list = {}
        week_start = (current_time - timezone.timedelta(current_time.weekday()))

        for model, content_type in content_types.items():
            model_name = model.__name__.lower()
            instances_list[model_name + '_list'] = [{
                'object': instance,
                'is_new': instance.created_at > week_start.replace(hour=0, minute=0, second=0, microsecond=0),
                'translation': self.get_translation_by_instance(instance, content_type, INBOX and instance.language or language)
            } for instance in model.objects.filter(q_object).order_by('-commented_at').distinct()[:items[model_name + 's']]]

        try:
            hour_value = HourValue.objects.latest('created_at')
        except HourValue.DoesNotExist:
            hour_value = 0

        context = {
			'hour_value': hour_value,
            'dropdown_list': self.dropdown_list,
            'items': items,
            'search_form': search_form
        }

        context.update(instances_list)
        context.update(kwargs)

        return context
