from django.views.generic import FormView
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic.base import View
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from ..systems import PayPal
from ..systems import PayPalException
from ..models import PayPalTransaction
from ..forms import PayPalTransactionForm

from users.decorators import ForbiddenUser
from core.models import Comment


User = get_user_model()


@ForbiddenUser(forbidden_usertypes=['AnonymousUser'])
class PayPalTransactionView(FormView):
    template_name = 'paypal/transaction/create.html'
    form_class = PayPalTransactionForm

    def dispatch(self, request, *args, **kwargs):
        self.comment_id = kwargs.get('comment_id')
        self.comment_model = get_object_or_404(Comment, pk=self.comment_id)
        return super(PayPalTransactionView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        current_site = get_current_site(self.request)
        returnUrl = "http://%s%s" % (
            current_site.domain,
            reverse('payments:transaction_paypal_success')
        )

        currency = int(self.request.POST.get('currency'))

        if currency == PayPalTransactionForm.USD:
            currency = 'USD'
        elif currency == PayPalTransactionForm.EUR:
            currency = 'EUR'

        paypal = PayPal(
            returnUrl=returnUrl,
            currency=currency
        )

        try:
            user = User.objects.get(
                username=form.cleaned_data.get('recipient_username')
            )
        except User.DoesNotExist:
            messages.add_message(
                self.request,
                messages.ERROR,
                'User does not exist'
            )
            return super(PayPalTransactionView, self).form_invalid(form)

        try:
            result = paypal.adaptive_payment(
                comment_object=self.comment_model,
                receiver_amount=form.cleaned_data.get('amount'),
                receiver_user=user,
                sender_user=self.request.user
            )
        except PayPalException as e:
            messages.error(self.request, e)
            return super(PayPalTransactionView, self).form_invalid(form)

        self.payUrl = result['pay_url']
        self.request.session['paypal_comment_id'] = self.kwargs.get('comment_id')
        return super(PayPalTransactionView, self).form_valid(form)

    def get_success_url(self):
        return self.payUrl

    def get_form_kwargs(self):
        kwargs = super(PayPalTransactionView, self).get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['comment_model'] = self.comment_model
        return kwargs


class PayPalTransactionSuccessView(View):
    def get(self, request, *args, **kwargs):
        current_site = get_current_site(request)
        returnUrl = "http://%s%s" % (
            current_site.domain,
            reverse('payments:transaction_paypal_success')
        )
        paypal = PayPal(returnUrl=returnUrl)
        for transaction in PayPalTransaction.objects.filter(
                paymentExecStatus=PayPalTransaction.CREATED,
                sender_user=self.request.user
        ):
            paypal_payment_instance = paypal.get_payment_information(transaction.payKey)
            paymentExecStatus = paypal_payment_instance.get('status', False)

            if paymentExecStatus:
                paymentExecStatus = paymentExecStatus[0]
            else:
                messages.error(request, _('Internal fault of the payment process.\
                                          Please refer to the site\'s administration'))
                return redirect("/")

            if (paymentExecStatus != PayPalTransaction.CREATED and
                    transaction.paymentExecStatus == PayPalTransaction.CREATED):
                transaction.paymentExecStatus = paymentExecStatus

                transaction.save()

        if self.request.session.get('paypal_comment_id'):
            comment = Comment.objects.get(id=self.request.session.get('paypal_comment_id'))
            del self.request.session['paypal_comment_id']
            return redirect("%s#comment-%s" % (
                reverse("%s-detail" % comment.content_type.name,
                        kwargs={'slug': comment.object_id}), comment.id))

        return redirect('/')
