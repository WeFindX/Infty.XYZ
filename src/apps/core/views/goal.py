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
from ..utils import ViewTypeWrapper
from ..forms import GoalCreateForm
from ..forms import GoalUpdateForm
from ..utils import UpdateViewWrapper
from ..utils import DetailViewWrapper
from ..utils import CommentsContentTypeWrapper
from ..filters import GoalListViewFilter1
from ..filters import GoalListViewFilter2
from ..models import Goal
from ..models import Idea
from ..models import Need


@ForbiddenUser(forbidden_usertypes=[u'AnonymousUser'])
class GoalCreateView(CreateViewWrapper):

    """Goal create view"""
    model = Goal
    form_class = GoalCreateForm
    template_name = "goal/create.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        #self.object.definition = form.cleaned_data.get('definition')
        self.object.save()
        return super(GoalCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, _("Goal succesfully created"))
        if self.object.personal:
            return reverse("inbox")
        else:
            return reverse("goal-detail", args=[self.object.pk, ])

    def get_context_data(self, **kwargs):
        context = super(GoalCreateView, self).get_context_data(**kwargs)
       #context.update({'definition_object': self.definition_instance})
        return context

    def dispatch(self, *args, **kwargs):
        if kwargs.get('need_id'):
            self.need_instance = get_object_or_404(Need, pk=int(kwargs['need_id']))
        else:
            self.need_instance = False
        return super(GoalCreateView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(GoalCreateView, self).get_form_kwargs()
        kwargs['need_instance'] = self.need_instance
        kwargs['request'] = self.request
        return kwargs


class GoalListView1(ViewTypeWrapper, PaginationMixin, OrderableListMixin, ListFilteredView):
    template_name = "goal/list1.html"
    model = Goal
    paginate_by = 10
    orderable_columns = [
        "name",
        "personal",
        "created_at",
        "updated_at",
        "reason",
        "user",
        "definition",
    ]
    orderable_columns_default = "-id"
    filter_set = GoalListViewFilter1


class GoalDeleteView(OwnerMixin, DeleteView):

    """Goal delete view"""
    model = Goal
    slug_field = "pk"
    template_name = "goal/delete.html"

    def get_success_url(self):
        messages.success(self.request, _("Goal succesfully deleted"))
        return reverse("home") #reverse("definition-detail", args=[self.object.definition.pk, ])


class GoalUpdateView(UpdateViewWrapper):

    """Goal update view"""
    model = Goal
    form_class = GoalUpdateForm
    slug_field = "pk"
    template_name = "goal/update.html"

    def form_valid(self, form):
        return super(GoalUpdateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, _("Goal succesfully updated"))
        return reverse("goal-detail", args=[self.object.pk, ])


class GoalDetailView(DetailViewWrapper, CommentsContentTypeWrapper):

    """Goal detail view"""
    model = Goal
    slug_field = "pk"
    template_name = "goal/detail.html"

    def get_context_data(self, **kwargs):
        context = super(GoalDetailView, self).get_context_data(**kwargs)
        context.update({
            'idea_list': Idea.objects.filter(goal=kwargs.get('object')).order_by('-id')
        })

        return context


class GoalListView2(ViewTypeWrapper, PaginationMixin, OrderableListMixin, ListFilteredView):
    template_name = "goal/list2.html"
    model = Goal
    paginate_by = 10
    orderable_columns = [
        "id",
    ]
    orderable_columns_default = "-id"
    filter_set = GoalListViewFilter2

    # def get_base_queryset(self):
    #     queryset = super(GoalListView2, self).get_base_queryset()
    #     queryset = queryset.filter(definition=self.kwargs.get('definition'))
    #     return queryset
