from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.views.generic import DeleteView
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.db.models.loading import get_model
from django.shortcuts import redirect
from django.contrib.contenttypes.models import ContentType

from users.decorators import ForbiddenUser

from ..models import Translation
from ..forms import TranslationCreateForm
from ..forms import TranslationUpdateForm


@ForbiddenUser(forbidden_usertypes=['AnonymousUser'])
class TranslationCreateView(CreateView):
    model = Translation
    form_class = TranslationCreateForm
    template_name = 'translation/create.html'

    def dispatch(self, request, *args, **kwargs):
        self.content_type_model = get_model(app_label='core', model_name=self.kwargs.get('model_name'))
        self.content_type = ContentType.objects.get_for_model(self.content_type_model)
        self.content_type_instance = self.content_type_model.objects.get(pk=kwargs.get('object_id'))
        self.detail_url = "%s-detail" % kwargs.get('model_name')

        if self.content_type_instance.user.id != self.request.user.id:
            messages.error(request, 'You don\'t have access for this page')
            return redirect(reverse(self.detail_url, kwargs={'slug': self.content_type_instance.id}))

        return super(TranslationCreateView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        url = "%s?lang=%s" % (
            reverse(self.detail_url, kwargs={'slug': self.content_type_instance.id}),
            self.object.language.language_code
        )
        return url

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.content_type = self.content_type
        self.object.object_id = self.content_type_instance.id
        self.object.save()

        return super(TranslationCreateView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(TranslationCreateView, self).get_form_kwargs()
        kwargs['content_type_instance'] = self.content_type_instance
        return kwargs

    def get_form(self, form_class):
        form = super(TranslationCreateView, self).get_form(form_class)

        model_fields = [x.name for x in self.content_type_model._meta.fields]

        for field in form.fields:
            if field not in model_fields:
                form.fields.pop(field)

        return form


@ForbiddenUser(forbidden_usertypes=['AnonymousUser'])
class TranslationUpdateView(UpdateView):
    model = Translation
    form_class = TranslationUpdateForm
    slug_field = "pk"
    template_name = 'translation/update.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        return super(TranslationUpdateView, self).form_valid(form)

    def get_success_url(self):
        url = "%s-detail" % self.object.content_type.model
        url = "%s?lang=%s" % (
            reverse(url, kwargs={'slug': self.object.object_id}),
            self.object.language.language_code
        )
        messages.success(self.request, _("Translation succesfully updated"))
        return url

    def dispatch(self, request, *args, **kwargs):
        self.content_type_model = get_model(app_label='core', model_name=self.get_object().content_type.model)
        self.content_type = ContentType.objects.get_for_model(self.content_type_model)
        self.content_type_instance = self.content_type_model.objects.get(pk=self.get_object().content_object.pk)
        self.detail_url = "%s-detail" % self.get_object().content_type.model

        if self.content_type_instance.user.id != self.request.user.id:
            messages.error(request, 'You don\'t have access for this page')
            return redirect(reverse(self.detail_url, kwargs={'slug': self.content_type_instance.id}))
        return super(TranslationUpdateView, self).dispatch(request, *args, **kwargs)

    def get_form(self, form_class):
        form = super(TranslationUpdateView, self).get_form(form_class)

        model_fields = [x.name for x in self.content_type_model._meta.fields]

        for field in form.fields:
            if field not in model_fields:
                form.fields.pop(field)

        return form


@ForbiddenUser(forbidden_usertypes=['AnonymousUser'])
class TranslationDeleteView(DeleteView):

    """Goal delete view"""
    model = Translation
    slug_field = "pk"
    template_name = "translation/delete.html"

    def dispatch(self, request, *args, **kwargs):
        self.content_type_model = get_model(app_label='core', model_name=self.get_object().content_type.model)
        self.content_type = ContentType.objects.get_for_model(self.content_type_model)
        self.content_type_instance = self.content_type_model.objects.get(pk=self.get_object().content_object.pk)
        self.detail_url = "%s-detail" % self.get_object().content_type.model

        if self.content_type_instance.user.id != self.request.user.id:
            messages.error(request, 'You don\'t have access for this page')
            return redirect(reverse(self.detail_url, kwargs={'slug': self.content_type_instance.id}))
        return super(TranslationDeleteView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        url = "%s-detail" % self.object.content_type.model
        url = "%s" % (
            reverse(url, kwargs={'slug': self.object.object_id}),
        )
        messages.success(self.request, _("Translation succesfully deleted"))
        return url
