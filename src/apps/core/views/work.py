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
from ..forms import WorkCreateForm
from ..forms import WorkUpdateForm
from ..utils import UpdateViewWrapper
from ..utils import DetailViewWrapper
from ..utils import ViewTypeWrapper
from ..utils import CommentsContentTypeWrapper
from ..filters import WorkListViewFilter1
from ..filters import WorkListViewFilter2
from ..models import Task
from ..models import Work


@ForbiddenUser(forbidden_usertypes=[u'AnonymousUser'])
class WorkListView1(ViewTypeWrapper, PaginationMixin, OrderableListMixin, ListFilteredView):
    template_name = "work/list1.html"
    model = Work
    paginate_by = 10
    orderable_columns = [
        "task",
        "name",
        "url",
        "created_at",
        "updated_at",
        "user",
        "file",
        "parent_work_id",
        "description",
    ]
    orderable_columns_default = "-id"
    filter_set = WorkListViewFilter1

    def get_base_queryset(self):
        queryset = super(WorkListView1, self).get_base_queryset()
        queryset = queryset.filter(task__pk=self.kwargs['task'])
        return queryset


class WorkUpdateView(UpdateViewWrapper):

    """Work update view"""
    model = Work
    form_class = WorkUpdateForm
    slug_field = "pk"
    template_name = "work/update.html"

    def form_valid(self, form):
        return super(WorkUpdateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, _("Work succesfully updated"))
        return reverse("work-detail", args=[self.object.pk, ])


@ForbiddenUser(forbidden_usertypes=[u'AnonymousUser'])
class WorkCreateView(CreateViewWrapper):

    """Work create view"""
    model = Work
    form_class = WorkCreateForm
    template_name = "work/create.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.task = Task.objects.get(pk=self.kwargs['task'])
        self.object.save()
        return super(WorkCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, _("Work succesfully created"))
        return reverse("work-detail", args=[self.object.pk, ])

    def get_context_data(self, **kwargs):
        context = super(WorkCreateView, self).get_context_data(**kwargs)
        context.update({
            'task_object': Task.objects.get(pk=self.kwargs['task']),
        })
        return context

    def get_form_kwargs(self):
        kwargs = super(WorkCreateView, self).get_form_kwargs()
        kwargs['task_instance'] = Task.objects.get(pk=self.kwargs['task'])
        kwargs['request'] = self.request
        return kwargs


class WorkDeleteView(OwnerMixin, DeleteView):

    """Work delete view"""
    model = Work
    slug_field = "pk"
    template_name = "work/delete.html"

    def get_success_url(self):
        messages.success(self.request, _("Work succesfully deleted"))
        return reverse("work-list1", args=[self.object.task.pk, ])


class WorkListView2(ViewTypeWrapper, PaginationMixin, OrderableListMixin, ListFilteredView):
    template_name = "work/list2.html"
    model = Work
    paginate_by = 10
    orderable_columns = [
        "task",
        "name",
        "url",
        "created_at",
        "updated_at",
        "user",
        "file",
        "parent_work_id",
        "description",
    ]
    orderable_columns_default = "-id"
    filter_set = WorkListViewFilter2


class WorkDetailView(DetailViewWrapper, CommentsContentTypeWrapper):

    """Work detail view"""
    model = Work
    slug_field = "pk"
    template_name = "work/detail.html"

    def get_context_data(self, **kwargs):
        context = super(WorkDetailView, self).get_context_data(**kwargs)
        obj = self.get_object()
        form = None
        if self.request.user.__class__.__name__ not in [u'AnonymousUser']:
            form = self.get_form_class()
        context.update({
            'form': form,
        })
        context.update({
            'object_list': self.object_list,
        })
        context.update({
            'work_list': Work.objects.filter(parent_work_id=kwargs.get('object').id).order_by('-id')
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
