from django.views.generic import FormView
from django.views.generic import UpdateView
from django.views.generic import ListView
from django.views.generic import DeleteView
from django.contrib import messages
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.http import HttpResponseForbidden

from pure_pagination.mixins import PaginationMixin

from ..forms import CryptsyTransactionForm
from ..systems import CryptsyPay
from ..forms import CryptsyCredentialForm
from ..forms import CoinAddressForm
from ..models import CryptsyCredential
from ..models import CoinAddress

from users.decorators import ForbiddenUser
from users.mixins import OwnerMixin
from core.models import Comment


class CoinAddressUpdateView(OwnerMixin, UpdateView):
    model = CoinAddress
    form_class = CoinAddressForm
    slug_field = "pk"
    template_name = "coin/update.html"

    def get_success_url(self):
        messages.success(self.request, _("Coin address succesfully updated"))
        return reverse("payments:coin_address_list")


@ForbiddenUser(forbidden_usertypes=['AnonymousUser'])
class CoinAddressCreateView(FormView):
    model = CoinAddress
    form_class = CoinAddressForm
    template_name = "coin/create.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super(CoinAddressCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, _("CoinAddress succesfully created"))
        return reverse("payments:coin_address_list")


class CoinAddressDeleteView(OwnerMixin, DeleteView):
    model = CoinAddress
    slug_field = "pk"
    template_name = "coin/delete.html"

    def get_success_url(self):
        messages.success(self.request, _("CoinAddress succesfully deleted"))
        return reverse("payments:coin_address_list")


@ForbiddenUser(forbidden_usertypes=['AnonymousUser'])
class CoinAddressListView(PaginationMixin, ListView):
    template_name = "coin/list.html"
    model = CoinAddress
    paginate_by = 10

    def get_queryset(self):
        qs = super(CoinAddressListView, self).get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs


class CryptsyCredentialUpdateView(OwnerMixin, UpdateView):
    form_class = CryptsyCredentialForm
    slug_field = 'pk'
    template_name = 'cryptsy/credential/update.html'
    model = CryptsyCredential

    def form_valid(self, form):
        form_object = form.save(commit=False)
        form_object.user = self.request.user
        form_object.save()
        return super(CryptsyCredentialUpdateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, _("Credential succesfully updated"))
        return reverse("payments:cryptsy_credential_list")


@ForbiddenUser(forbidden_usertypes=['AnonymousUser'])
class CryptsyCredentialListView(PaginationMixin, ListView):
    model = CryptsyCredential
    paginate_by = 10
    template_name = 'cryptsy/credential/list.html'

    def post(self, request, *args, **kwargs):
        user_credential = self.request.user.credential
        # Set all credentials to False
        user_credential.filter(default=True).update(default=False)

        # Set the obtained by id credential "default" field in False
        credential_id = int(request.POST.get('credential_id'))
        credential = user_credential.get(id=credential_id)
        credential.default = True
        credential.save()

        # Redirect to the current page
        return redirect(reverse("payments:cryptsy_credential_list"))

    def get_queryset(self):
        qs = super(CryptsyCredentialListView, self).get_queryset()

        qs = qs.filter(user=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context = super(CryptsyCredentialListView, self).get_context_data(**kwargs)
        context['current_domain'] = Site.objects.get_current().domain
        return context

    def get_base_queryset(self):
        queryset = super(CryptsyCredentialListView, self).get_base_queryset()
        queryset = queryset.filter(user=self.request.user.pk)
        return queryset


class CryptsyCredentialDeleteView(OwnerMixin, DeleteView):
    model = CryptsyCredential
    slug_field = 'pk'
    template_name = 'cryptsy/credential/delete.html'

    def get_success_url(self):
        messages.success(self.request, _("Credential succesfully deleted"))
        return reverse("payments:cryptsy_credential_list")


@ForbiddenUser(forbidden_usertypes=['AnonymousUser'])
class CryptsyCredentialCreateView(FormView):
    form_class = CryptsyCredentialForm
    template_name = 'cryptsy/credential/create.html'

    def form_valid(self, form):
        # from django import forms
        # form.add_error('notificationtoken', forms.ValidationError('asd'))
        # return super(CryptsyCredentialCreateView, self).form_invalid(form)
        form_object = form.save(commit=False)
        form_object.user = self.request.user
        current_site = Site.objects.get_current()
        form_object.save()
        form_object.notificationtoken = 'https://%s%s' % (
            current_site.domain, reverse('cryptsy_notification_token', kwargs={
                'username': self.request.user.username,
                'credential_id': form_object.id
            })
        )
        form_object.save()
        return super(CryptsyCredentialCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, _("Credential succesfully created"))
        return reverse("payments:cryptsy_credential_list")


@ForbiddenUser(forbidden_usertypes=['AnonymousUser'])
class CryptsyTransactionCreateView(FormView):
    form_class = CryptsyTransactionForm
    template_name = 'cryptsy/transaction/create.html'

    def dispatch(self, request, *args, **kwargs):
        self.comment_id = kwargs.get('comment_id')
        self.comment_model = get_object_or_404(Comment, pk=self.comment_id)
        cryptsy_credential = request.user.credential.filter(default=True)
        if not cryptsy_credential.exists():
            messages.add_message(self.request, messages.INFO, _('You have not added any credential. Please create a Credential or select default'))
            return redirect(reverse('payments:cryptsy_credential_list'))
        else:
            cryptsy_credential = request.user.credential.get(default=True)
            self.cryptsy_publickey = cryptsy_credential.publickey
        if self.comment_model.hours_claimed:
            # Adding Transactions to Comment should only be possible
            # if the comment has hours claimed.
            return super(CryptsyTransactionCreateView, self).dispatch(
                request, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    def form_valid(self, form):
        recipient_address = form.cleaned_data.get('recipient_address')
        amount = form.cleaned_data.get('amount')
        currency = form.cleaned_data.get('currency')
        cryptsy = CryptsyPay(publickey=self.cryptsy_publickey)
        response = cryptsy.make_payment(
            comment_object=self.comment_model,
            address=recipient_address.address,
            amount=amount,
            currency_id=currency,
        )
        if response["success"]:
            messages.add_message(
                self.request,
                messages.INFO,
                response["data"]["withdraw_id"]
            )
        else:
            messages.add_message(
                self.request,
                messages.ERROR,
                response["error"][0]
            )

        return redirect("%s#comment-%s" % (
            reverse("%s-detail" % self.comment_model.content_type.name,
                    kwargs={'slug': self.comment_model.object_id}), self.comment_model.id))

    def get_success_url(self):
        return reverse('payments:transaction_cryptsy', kwargs={'comment_id': self.comment_id})

    def get_form_kwargs(self):
        kwargs = super(CryptsyTransactionCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['comment_model'] = self.comment_model
        return kwargs
