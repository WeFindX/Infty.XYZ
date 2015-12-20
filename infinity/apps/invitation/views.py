from django.views.generic import View
from django.views.generic import FormView
from django.views.generic import DetailView
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.template import Context, Template
from django.core.mail import EmailMessage
from django.contrib import messages
from django.db.models import F
from django import forms

from users.decorators import ForbiddenUser
from users.models import User
from .app_settings import app_settings
from .models import Invitation
from .models import InvitationLetterTemplate
from .forms import InvitationForm


class InviteView(View):
    def get(self, request, *args, **kwargs):
        """
        Set invitation session
        Redirect to the register page
        """
        invitation_object = Invitation.objects.filter(
            token=kwargs.get('token'),
            invited=False
        )
        if invitation_object.exists():
            request.session['invitation'] = True
            invitation_object = invitation_object.first()
            invitation_object.invited = True
            invitation_object.save()

        return redirect(reverse('account_signup'))


@ForbiddenUser(forbidden_usertypes=['AnonymousUser'])
class InvitationFormView(FormView):
    form_class = InvitationForm
    template_name = "invitation/invite.html"

    def get_form_kwargs(self):
        kwargs = super(InvitationFormView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse("invite:send")

    def form_valid(self, form):

        user = self.request.user
        user_invitation_option = user.invitationoption

        try:
            User.objects.get(email=form.cleaned_data.get('member_email'))
            form.add_error('member_email', forms.ValidationError("Already using Infty, you can't invite him"))
            return super(InvitationFormView, self).form_invalid(form)
        except User.DoesNotExist:
            pass

        if user_invitation_option.invitations_left:
            invitation, created = Invitation.objects.get_or_create(
                sender=self.request.user,
                email=form.cleaned_data.get('member_email')
            )
        else:
            messages.error(self.request, "You ran out of invites")
            return super(InvitationFormView, self).form_invalid(form)

        if created:
            user_invitation_option.invitations_left = F('invitations_left') - 1
            user_invitation_option.save()
            ctx = {
                'invitation_url': invitation.get_invitation_url()
            }

            template = Template(form.cleaned_data.get('email_body'))
            context = Context(ctx)
            subject = app_settings.SUBJECT
            from_email = app_settings.FROM_EMAIL
            message = template.render(context)
            EmailMessage(
                subject,
                message,
                to=[form.cleaned_data.get('member_email')],
                from_email=from_email
            ).send()
            messages.success(self.request, "Invite was sent")
        else:
            form.add_error('member_email', forms.ValidationError("This email address already invited"))
            return super(InvitationFormView, self).form_invalid(form)

        return redirect(self.get_success_url())


@ForbiddenUser(forbidden_usertypes=['AnonymousUser'])
class InvitationLetterTemplateView(DetailView):
    model = InvitationLetterTemplate
    slug_field = "language__omegawiki_language_id"
