import json

from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.views.generic import DeleteView

from users.decorators import ForbiddenUser
from users.mixins import OwnerMixin
from users.forms import ConversationInviteForm

from ..utils import CreateViewWrapper
from ..utils import LookupCreateDefinition
from ..forms import NeedCreateForm
from ..forms import NeedUpdateForm
from ..utils import UpdateViewWrapper
from ..utils import DetailViewWrapper
from ..utils import CommentsContentTypeWrapper
from ..models import Goal
from ..models import Need
from ..models import Definition
from ..models import Language

@ForbiddenUser(forbidden_usertypes=[u'AnonymousUser'])
class NeedCreateView(CreateViewWrapper):

    """Need create view"""
    model = Need
    form_class = NeedCreateForm
    template_name = "need/create.html"

    def form_valid(self, form):
        request = self.request
        self.object = form.save(commit=False)
        self.object.user = self.request.user

        if form.cleaned_data.get('definition'):
            self.object.definition = form.cleaned_data.get('definition')
        else:
            definition_data = request.POST.get('select_definition')
            definition_data = json.loads(definition_data)
            definition_data.update({
                'user': request.user,
                'language': Language.objects.get(language_code=request.LANGUAGE_CODE)
            })

            definition, created = Definition.objects.get_or_create(**definition_data)

            self.object.definition = definition

        self.object.save()
        return super(NeedCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, _("Need succesfully created"))
        if self.object.personal:
            return reverse("inbox")
        else:
            return reverse("need-detail", args=[self.object.pk, ])

    def get_context_data(self, **kwargs):
        context = super(NeedCreateView, self).get_context_data(**kwargs)
        context.update({'definition_object': self.definition_instance})
        return context

    def dispatch(self, *args, **kwargs):
        language = Language.objects.get(language_code=self.request.LANGUAGE_CODE)

        if kwargs.get('concept_q'):

            if kwargs['concept_q'].isdigit():
                # Lookup or Create Definition by .pk
                definitions = Definition.objects.filter(pk=int(kwargs['concept_q']), language=language)

                if definitions:
                    self.definition_instance = definitions[0]
                else:
                    definitions = Definition.objects.filter(pk=int(kwargs['concept_q']))
                    if definitions:
                        if definitions[0].defined_meaning_id:
                            self.definition_instance = LookupCreateDefinition(definitions[0].defined_meaning_id, language)
                        else:
                            self.definition_instance = definitions[0]

            elif kwargs['concept_q'][1:].isdigit():
                # Lookup Definition by .defined_meaning_id
                definitions = Definition.objects.filter(defined_meaning_id=int(kwargs['concept_q'][1:]),language=language)

                if definitions:
                    self.definition_instance = definitions[0]
                else:
                    self.definition_instance = LookupCreateDefinition(int(kwargs['concept_q'][1:]),language=language)

        else:
            self.definition_instance = False

        return super(NeedCreateView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(NeedCreateView, self).get_form_kwargs()
        kwargs['definition_instance'] = self.definition_instance
        kwargs['request'] = self.request
        return kwargs


class NeedDeleteView(OwnerMixin, DeleteView):

    """Need delete view"""
    model = Need
    slug_field = "pk"
    template_name = "need/delete.html"

    def get_success_url(self):
        messages.success(self.request, _("Need succesfully deleted"))
        return reverse("definition-detail", args=[self.object.definition.pk, ])


class NeedUpdateView(UpdateViewWrapper):

    """Need update view"""
    model = Need
    form_class = NeedUpdateForm
    slug_field = "pk"
    template_name = "need/update.html"

    def form_valid(self, form):
        return super(NeedUpdateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, _("Need succesfully updated"))
        return reverse("need-detail", args=[self.object.pk, ])


class NeedDetailView(DetailViewWrapper, CommentsContentTypeWrapper):

    """Need detail view"""
    model = Need
    slug_field = "pk"
    template_name = "need/detail.html"

    def get_context_data(self, **kwargs):
        context = super(NeedDetailView, self).get_context_data(**kwargs)

        context.update({
            'goal_list': Goal.objects.filter(need=kwargs.get('object')).order_by('-id')
        })

        return context
