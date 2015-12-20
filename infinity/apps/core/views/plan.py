from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
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
from ..forms import PlanCreateForm
from ..forms import PlanUpdateForm
from ..utils import UpdateViewWrapper
from ..utils import DetailViewWrapper
from ..utils import ViewTypeWrapper
from ..utils import CommentsContentTypeWrapper
from ..filters import PlanListViewFilter1
from ..filters import PlanListViewFilter2
from ..models import Plan
from ..models import Idea
from ..models import Step


@ForbiddenUser(forbidden_usertypes=['AnonymousUser'])
class PlanListView1(ViewTypeWrapper, PaginationMixin, OrderableListMixin, ListFilteredView):

    template_name = "plan/list1.html"
    model = Plan
    paginate_by = 10
    orderable_columns = [
        "name",
        "created_at",
        "updated_at",
        "idea",
        "deliverable",
        "user",
        "situation",
    ]
    orderable_columns_default = "-id"
    filter_set = PlanListViewFilter1

    def get_base_queryset(self):
        queryset = super(PlanListView1, self).get_base_queryset()
        queryset = queryset.filter(idea__pk=self.kwargs['idea'])
        return queryset


class PlanUpdateView(UpdateViewWrapper):

    """Plan update view"""
    model = Plan
    form_class = PlanUpdateForm
    slug_field = "pk"
    template_name = "plan/update.html"

    def form_valid(self, form):
        return super(PlanUpdateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, _("Plan succesfully updated"))
        return reverse("plan-detail", args=[self.object.pk, ])


@ForbiddenUser(forbidden_usertypes=['AnonymousUser'])
class PlanCreateView(CreateViewWrapper):

    """Plan create view"""
    model = Plan
    form_class = PlanCreateForm
    template_name = "plan/create.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.idea = form.cleaned_data.get('idea')
        self.object.save()
        return super(PlanCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, _("Plan succesfully created"))
        return reverse("plan-detail", args=[self.object.pk, ])

    def dispatch(self, request, *args, **kwargs):
        if kwargs.get('idea_id'):
            self.idea_instance = get_object_or_404(Idea, pk=kwargs['idea_id'])
        else:
            self.idea_instance = False
        return super(PlanCreateView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(PlanCreateView, self).get_form_kwargs()
        kwargs['idea_instance'] = self.idea_instance
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(PlanCreateView, self).get_context_data(**kwargs)
        context.update({'idea_object': self.idea_instance})
        return context


@ForbiddenUser(forbidden_usertypes=['AnonymousUser'])
class PlanDeleteView(OwnerMixin, DeleteView):

    """Plan delete view"""
    model = Plan
    slug_field = "pk"
    template_name = "plan/delete.html"

    def get_success_url(self):
        messages.success(self.request, _("Plan succesfully deleted"))
        return reverse("plan-list1", args=[self.object.idea.pk, ])


class PlanListView2(ViewTypeWrapper, PaginationMixin, OrderableListMixin, ListFilteredView):

    template_name = "plan/list2.html"
    model = Plan
    paginate_by = 10
    orderable_columns = [
        "name",
        "created_at",
        "updated_at",
        "idea",
        "deliverable",
        "user",
        "situation",
    ]
    orderable_columns_default = "-id"
    filter_set = PlanListViewFilter2


class PlanDetailView(DetailViewWrapper, CommentsContentTypeWrapper):

    """Plan detail view"""
    model = Plan
    slug_field = "pk"
    template_name = "plan/detail.html"

    def get_success_url(self):
        messages.success(
            self.request, _(
                "%s succesfully created" %
                self.form_class._meta.model.__name__))
        return self.request.path

    def get_context_data(self, **kwargs):
        context = super(PlanDetailView, self).get_context_data(**kwargs)
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
            'step_list': Step.objects.filter(plan=kwargs.get('object')).order_by('priority')
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
