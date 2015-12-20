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
from ..forms import TaskCreateForm
from ..forms import TaskUpdateForm
from ..utils import UpdateViewWrapper
from ..utils import DetailViewWrapper
from ..utils import ViewTypeWrapper
from ..utils import CommentsContentTypeWrapper
from ..filters import TaskListViewFilter1
from ..filters import TaskListViewFilter2
from ..models import Step
from ..models import Task
from ..models import Work


@ForbiddenUser(forbidden_usertypes=['AnonymousUser'])
class TaskListView1(ViewTypeWrapper, PaginationMixin, OrderableListMixin, ListFilteredView):

    template_name = "task/list1.html"
    model = Task
    paginate_by = 10
    orderable_columns = [
        "name",
        "created_at",
        "updated_at",
        "priority",
        "step",
        "user",
    ]
    orderable_columns_default = "-id"
    filter_set = TaskListViewFilter1

    def get_base_queryset(self):
        queryset = super(TaskListView1, self).get_base_queryset()
        queryset = queryset.filter(step__pk=self.kwargs['step'])
        return queryset


class TaskUpdateView(UpdateViewWrapper):

    """Task update view"""
    model = Task
    form_class = TaskUpdateForm
    slug_field = "pk"
    template_name = "task/update.html"

    def form_valid(self, form):
        return super(TaskUpdateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, _("Task succesfully updated"))
        return reverse("step-detail", args=[self.object.step.pk, ])


@ForbiddenUser(forbidden_usertypes=['AnonymousUser'])
class TaskCreateView(CreateViewWrapper):

    """Task create view"""
    model = Task
    form_class = TaskCreateForm
    template_name = "task/create.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.step = Step.objects.get(pk=self.kwargs['step'])
        self.object.save()
        return super(TaskCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, _("Task succesfully created"))
        return reverse("step-detail", args=[self.object.step.pk, ])

    def get_context_data(self, **kwargs):
        context = super(TaskCreateView, self).get_context_data(**kwargs)
        context.update({
                    'step_object': Step.objects.get(pk=self.kwargs['step']),
        })
        return context

    def get_form_kwargs(self):
        kwargs = super(TaskCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class TaskDeleteView(OwnerMixin, DeleteView):

    """Task delete view"""
    model = Task
    slug_field = "pk"
    template_name = "task/delete.html"

    def get_success_url(self):
        messages.success(self.request, _("Task succesfully deleted"))
        return reverse("task-list1", args=[self.object.step.pk, ])


class TaskListView2(ViewTypeWrapper, PaginationMixin, OrderableListMixin, ListFilteredView):

    """Task list view"""

    template_name = "task/list2.html"

    model = Task
    paginate_by = 10
    orderable_columns = [
        "name",
        "created_at",
        "updated_at",
        "priority",
        "step",
        "user",
    ]
    orderable_columns_default = "-id"
    filter_set = TaskListViewFilter2


class TaskDetailView(DetailViewWrapper, CommentsContentTypeWrapper):

    """Task detail view"""
    model = Task
    slug_field = "pk"
    template_name = "task/detail.html"

    def get_success_url(self):
        messages.success(
            self.request, _(
                "%s succesfully created" %
                self.form_class._meta.model.__name__))
        return self.request.path

    def get_context_data(self, **kwargs):
        context = super(TaskDetailView, self).get_context_data(**kwargs)
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
            'work_list': Work.objects.filter(task=kwargs.get('object')).order_by('id')
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
