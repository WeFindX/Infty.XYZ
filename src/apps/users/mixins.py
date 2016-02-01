from django.http import Http404
from django.views.generic.detail import SingleObjectMixin


class OwnerMixin(SingleObjectMixin):
    def get_object(self, queryset=None):
        obj = super(OwnerMixin, self).get_object(queryset)
        if obj.user.pk != self.request.user.pk:
            raise Http404()
        return obj
