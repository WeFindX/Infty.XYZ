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

from clever_selects.views import ChainedSelectChoicesView

from users.decorators import ForbiddenUser
from users.models import User
from hours.models import HourValue
from core.models import Language

from ..forms import ContentTypeSubscribeForm
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


@ForbiddenUser(forbidden_usertypes=['AnonymousUser'])
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

    def get_translation_by_instance(self, instance, content_type):
        language = Language.objects.get(language_code=self.request.LANGUAGE_CODE)
        translation = Translation.objects.filter(
            content_type=content_type,
            object_id=instance.id,
            language=language.id
        )

        return translation.first()

    def get_context_data(self, **kwargs):
        items = {'needs': 32,
                 'goals': 64,
                 'ideas': 128,
                 'plans': 256,
                 'steps': 512,
                 'tasks': 1024,
                 'works': 2048}

        if self.request.session.get('needs_number'):
            items['goals'] = self.request.session['needs_number']
        if self.request.session.get('goals_number'):
            items['goals'] = self.request.session['goals_number']
        if self.request.session.get('ideas_number'):
            items['ideas'] = self.request.session['ideas_number']
        if self.request.session.get('plans_number'):
            items['plans'] = self.request.session['plans_number']
        if self.request.session.get('steps_number'):
            items['steps'] = self.request.session['steps_number']
        if self.request.session.get('tasks_number'):
            items['tasks'] = self.request.session['tasks_number']
        if self.request.session.get('works_number'):
            items['works'] = self.request.session['works_number']


        # Prepare base content access filters
        if self.request.user.is_authenticated():
            if self.request.resolver_match.url_name == 'inbox':
                q_object = (
                    Q(personal=True, user=self.request.user) |
                    Q(personal=True, sharewith=self.request.user)
                )
            else:
                q_object = (
                    Q(personal=False) |
                    Q(personal=True, user=self.request.user) |
                    Q(personal=True, sharewith=self.request.user)
                )
        else:
            q_object = (
                Q(personal=False)
            )

        # Get Content Types for Goal, Idea, Plan, Step, Task
        content_types = ContentType.objects.get_for_models(Need, Goal, Idea, Plan, Step, Task, Work)

        now = timezone.now()
        in_days = lambda x: float(x.seconds/86400.)
        in_hours = lambda x: float(x.seconds/3600.)

        instances = {}

        for model_class, translations in list(content_types.items()):
            model_class_lower_name = model_class.__name__.lower() + 's'
            instances[model_class_lower_name] = model_class.objects.filter(
                q_object
            ).order_by('-commented_at').distinct()[:items[model_class_lower_name]]


        needs = instances['needs']
        goals = instances['goals']
        ideas = instances['ideas']
        plans = instances['plans']
        steps = instances['steps']
        tasks = instances['tasks']
        works = instances['works']

        commented_at = lambda items: [obj.commented_at for obj in items]

        objects_list = list(chain(needs, goals, ideas, plans, steps, tasks, works))
        dates = commented_at(objects_list)

        if dates:
            start = min(dates)
            days = in_days(now-start)
        else:
            start = timezone.now()
            days = 0.

        try:
            hour_value = HourValue.objects.latest('created_at')
        except HourValue.DoesNotExist:
            hour_value = 0

        instances_list = {}

        for model, content_type in list(content_types.items()):
            model_name = model.__name__.lower()
            instances_list[model_name + '_list'] = [{
                'object': instance,
                'is_new': instance.created_at > start,
                'translation': self.get_translation_by_instance(instance, content_type)
            } for instance in model.objects.filter(q_object).order_by('-commented_at').distinct()[:items[model_name + 's']]]

        context = {
            'need_hours': needs and
            '%0.2f' % in_hours(now-max(commented_at(list(needs)))) or 0.,
            'goal_hours': goals and
            '%0.2f' % in_hours(now-max(commented_at(list(goals)))) or 0.,
            'idea_hours': ideas and
            '%0.2f' % in_hours(now-max(commented_at(list(ideas)))) or 0.,
            'plan_hours': plans and
            '%0.2f' % in_hours(now-max(commented_at(list(plans)))) or 0.,
            'step_hours': steps and
            '%0.2f' % in_hours(now-max(commented_at(list(steps)))) or 0.,
            'task_hours': tasks and
            '%0.2f' % in_hours(now-max(commented_at(list(tasks)))) or 0.,
            'work_hours': works and
            '%0.2f' % in_hours(now-max(commented_at(list(works)))) or 0.,
            'last_days': '%0.2f' % days,
            'number_of_items': len(objects_list),
            'hour_value': hour_value,
            'dropdown_list': self.dropdown_list,
            'items': items,
        }

        context.update(instances_list)
        context.update(kwargs)

        return context


class AjaxChainedView(ChainedSelectChoicesView):
    def get_choices(self):
        vals_list = []
        for x in range(1, 6):
            vals_list.append(x*int(self.parent_value))
        address = User.objects.get(pk=self.parent_value).address.all()
        res = tuple(
            zip(
                [x.pk for x in address],
                ['(%s) %s' % (x.currency_code, x.address) for x in address]
            )
        )
        return res
