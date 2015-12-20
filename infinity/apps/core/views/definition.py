import json

from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.views.generic import UpdateView
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.views.generic import CreateView
from django.http import HttpResponse

from enhanced_cbv.views import ListFilteredView
from pure_pagination.mixins import PaginationMixin
from braces.views import OrderableListMixin

from ..utils import CommentsContentTypeWrapper
from ..utils import ViewTypeWrapper, DetailViewWrapper
from ..utils import WikiDataSearch
from ..models import Definition, Language, Need
from ..forms import DefinitionUpdateForm, DefinitionCreateForm
from ..filters import DefinitionListViewFilter
from users.mixins import OwnerMixin
from users.forms import ConversationInviteForm
from users.decorators import ForbiddenUser


@ForbiddenUser(forbidden_usertypes=['AnonymousUser'])
class DefinitionUpdateView(OwnerMixin, UpdateView):

    """Definition update view"""
    model = Definition
    form_class = DefinitionUpdateForm
    slug_field = "pk"
    template_name = "definition/update.html"

    def dispatch(self, *args, **kwargs):
        owner = Definition.objects.get(pk=self.kwargs['slug']).user
        if self.request.user != owner:
            return redirect(reverse('definition-detail',
                                    kwargs={'slug': self.kwargs['slug']}))
        return super(DefinitionUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super(DefinitionUpdateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, _("Definition succesfully updated"))
        return reverse("definition-detail", args=[self.object.pk, ])


class DefinitionCreateView(CreateView):

    """Definition create view"""
    model = Definition
    form_class = DefinitionCreateForm
    template_name = "definition/create.html"

    def get(self, request, **kwargs):
        if request.is_ajax():
            find_language = request.GET.get('find_language', None)
            if find_language:
                try:
                    language = Language.objects.get(
                        http_accept_language=find_language)
                except Language.DoesNotExist:
                    language = Language.objects.get(
                        language_code=request.LANGUAGE_CODE)
                return HttpResponse(language.pk)

            hints = []
            similar_definitions = Definition.objects.filter(
                language__pk=request.GET['language'],
                name__iexact=request.GET['name']
            )
            for definition in similar_definitions:
                if definition.definition:
                    hints.append([definition.name,
                                  definition.definition,
                                  reverse('need-create', args=[definition.pk])])

            # Add suggestions from WikiData
            hints += WikiDataSearch(request.GET['name'], request.LANGUAGE_CODE)

            resp = json.dumps(hints[::-1])
            return HttpResponse(resp, content_type='application/json')
        form = DefinitionCreateForm(request=request)
        return render(request, 'definition/create.html',
                      {'form': form})

    def post(self, request, **kwargs):
        form = DefinitionCreateForm(request.POST, request=request)
        if form.is_valid():
            self.object = form.save(commit=False)
            self.object.user = self.request.user
            self.object.save()
            messages.success(self.request, _("Definition succesfully created"))
            return redirect(reverse('need-create', kwargs={'concept_q': self.object.pk}))

        return render(request, 'definition/create.html',
                      {'form': form})


class DefinitionListView(ViewTypeWrapper, PaginationMixin, OrderableListMixin, ListFilteredView):

    template_name = "definition/list.html"
    model = Definition
    paginate_by = 10
    orderable_columns = ["created_at", "type", "name", ]
    orderable_columns_default = "-id"
    ordering = ["-id"]
    filter_set = DefinitionListViewFilter


class DefinitionDetailView(DetailViewWrapper, CommentsContentTypeWrapper):

    """Definition detail view"""
    model = Definition
    slug_field = "pk"
    template_name = "definition/detail.html"

    def get_success_url(self):
        messages.success(
            self.request, _(
                "%s succesfully created" %
                self.form_class._meta.model.__name__))
        return self.request.path

    def get_context_data(self, **kwargs):
        context = super(DefinitionDetailView, self).get_context_data(**kwargs)
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
            'need_list': Need.objects.filter(definition=kwargs.get('object')).order_by('-id')
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
