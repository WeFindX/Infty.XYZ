import json

from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.views.generic import DeleteView

from pure_pagination.mixins import PaginationMixin
from braces.views import OrderableListMixin
from enhanced_cbv.views import ListFilteredView

from users.decorators import ForbiddenUser
from users.mixins import OwnerMixin
from users.forms import ConversationInviteForm

from ..utils import CreateViewWrapper
from ..forms import StepCreateForm
from ..forms import StepUpdateForm
from ..forms import ChangePriorityForm
from ..utils import UpdateViewWrapper
from ..utils import DetailViewWrapper
from ..utils import ViewTypeWrapper
from ..utils import CommentsContentTypeWrapper
from ..utils import JsonView
from ..filters import StepListViewFilter1
from ..filters import StepListViewFilter2
from ..models import Plan
from ..models import Step
from ..models import Task


@ForbiddenUser(forbidden_usertypes=['AnonymousUser'])
class StepListView1(ViewTypeWrapper, PaginationMixin, OrderableListMixin, ListFilteredView):
    template_name = "step/list1.html"
    model = Step
    paginate_by = 10
    orderable_columns = [
        "user",
        "name",
        "created_at",
        "updated_at",
        "deliverables",
        "priority",
        "plan",
        "objective",
        "investables",
    ]
    orderable_columns_default = "-id"
    filter_set = StepListViewFilter1

    def get_base_queryset(self):
        queryset = super(StepListView1, self).get_base_queryset()
        queryset = queryset.filter(plan__pk=self.kwargs['plan'])
        return queryset


class StepUpdateView(UpdateViewWrapper):

    """Step update view"""
    model = Step
    form_class = StepUpdateForm
    slug_field = "pk"
    template_name = "step/update.html"

    def form_valid(self, form):
        return super(StepUpdateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, _("Step succesfully updated"))
        return reverse("plan-detail", args=[self.object.plan.pk, ])


@ForbiddenUser(forbidden_usertypes=['AnonymousUser'])
class StepCreateView(CreateViewWrapper):

    """Step create view"""
    model = Step
    form_class = StepCreateForm
    template_name = "step/create.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.plan = Plan.objects.get(pk=self.kwargs['plan'])
        self.object.save()
        return super(StepCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, _("Step succesfully created"))
        return reverse("plan-detail", args=[self.object.plan.pk, ])

    def get_context_data(self, **kwargs):
        context = super(StepCreateView, self).get_context_data(**kwargs)
        context.update({
                    'plan_object': Plan.objects.get(pk=self.kwargs['plan']),
        })
        return context

    def get_form_kwargs(self):
        kwargs = super(StepCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class StepDeleteView(OwnerMixin, DeleteView):

    """Step delete view"""
    model = Step
    slug_field = "pk"
    template_name = "step/delete.html"

    def get_success_url(self):
        messages.success(self.request, _("Step succesfully deleted"))
        return reverse("step-list1", args=[self.object.plan.pk, ])


class StepListView2(ViewTypeWrapper, PaginationMixin, OrderableListMixin, ListFilteredView):

    template_name = "step/list2.html"
    model = Step
    paginate_by = 10
    orderable_columns = [
        "user",
        "name",
        "created_at",
        "updated_at",
        "deliverables",
        "priority",
        "plan",
        "objective",
        "investables",
    ]
    orderable_columns_default = "-id"
    filter_set = StepListViewFilter2

    def get_base_queryset(self):
        queryset = super(StepListView2, self).get_base_queryset()
        queryset = queryset.filter(user=self.request.user.pk)
        return queryset


class StepDetailView(DetailViewWrapper, CommentsContentTypeWrapper):

    """Step detail view"""
    model = Step
    slug_field = "pk"
    template_name = "step/detail.html"

    def get_success_url(self):
        messages.success(
            self.request, _(
                "%s succesfully created" %
                self.form_class._meta.model.__name__))
        return self.request.path

    def get_context_data(self, **kwargs):
        context = super(StepDetailView, self).get_context_data(**kwargs)
        obj = self.get_object()
        form = None
        if self.request.user.__class__.__name__ not in ['AnonymousUser']:
            form = self.get_form_class()
        context.update({
            'form': form,
        })
        context.update({
            'object_list': self.object_list,
        })
        context.update({
            'task_list': Task.objects.filter(step=kwargs.get('object')).order_by('id')
        })
        context.update({
            'is_subscribed': kwargs.get('object').subscribers.filter(pk=self.request.user.id) and True or False
        })

        conversation_form = ConversationInviteForm()
        next_url = "?next=%s" % self.request.path
        obj = kwargs.get('object')
        conversation_form.helper.form_action = reverse('user-conversation-invite', kwargs={
            'object_name': obj.__class__.__name__,
            'object_id': obj.id
        }) + next_url
        context.update({
            'conversation_form': conversation_form
        })

        return context


@ForbiddenUser(forbidden_usertypes=['AnonymousUser'])
class ChangeStepPriorityView(JsonView):
    def post(self, request, *args, **kwargs):
        form = ChangePriorityForm(request.POST)
        if form.is_valid():
            steps = json.loads(form.data.get('steps'))
            for step in steps:
                try:
                    step_instance = Step.objects.get(id=step['id'])

                    if not step_instance.plan.user == request.user:
                        return self.json({'error': True, 'message': 'Access error'})

                    step_instance.priority = step['index']
                    step_instance.save()
                    data = {'error': False}
                except Step.DoesNotExist as e:
                    data = {'error': True, 'message': e.message}
        else:
            data = {'error': True, 'message': form.errors }

        return self.json(data)
