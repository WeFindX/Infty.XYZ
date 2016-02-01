from django_webtest import WebTest
from model_mommy import mommy
from django.core.urlresolvers import reverse
from allauth.account.models import EmailAddress, EmailConfirmation
from core.models import Language
from django.core import mail


class InvitationTest(WebTest):
    def setUp(self):
        self.user_with_invitations = mommy.make('users.User', email='qwewqe@sasda.com')
        self.user_without_invitations = mommy.make('users.User', email='fjlskjdf@ajdalsk.com')

        self.language = mommy.make(Language)

        self.user_with_invitations.set_password('test')
        self.user_with_invitations.save()

        self.user_without_invitations.set_password('test')
        self.user_without_invitations.save()

        self.email_first = mommy.make(EmailAddress, user=self.user_with_invitations, verified=True)
        self.email_second = mommy.make(EmailAddress, user=self.user_without_invitations, verified=True)

        mommy.make(EmailConfirmation, email_address=self.email_first)
        mommy.make(EmailConfirmation, email_address=self.email_second)

        self.user_without_invitations.invitationoption.invitations_left = 0
        self.user_without_invitations.invitationoption.save()

    def login(self, login, password):
        resp = self.app.get(reverse('account_login'))
        form = resp.forms[1]
        form['login'] = login
        form['password'] = password
        res = form.submit()
        return res

    def test_invitation_form_view_for_user_without_invitations(self):
        invitation_form_view_url = reverse('invite:send')

        self.login(self.email_second.email, 'test')
        response = self.app.get(invitation_form_view_url)
        form = response.forms[1]
        form['member_email'] = 'test@test.com'
        form['language'] = self.language.id
        form['email_body'] = 'Hello, World {{ invitation_url }}'
        form_response = form.submit()

        for message in form_response.context['messages']:
            self.assertEqual('You ran out of invites', str(message))

    def test_invitation_form_view(self):
        invitation_form_view_url = reverse('invite:send')

        self.login(self.email_first.email, 'test')
        response = self.app.get(invitation_form_view_url)
        form = response.forms[1]
        form['member_email'] = 'test@test1.com'
        form['language'] = self.language.id
        form['email_body'] = 'Hello, World {{ invitation_url }}'
        form_response = form.submit()

        # Check invitation url in outbox
        self.assertTrue(
            mail.outbox[0].body.find(form_response.context['invitation_url'])
        )

    def test_already_invited_user(self):
        invitation_form_view_url = reverse('invite:send')

        self.login(self.email_first.email, 'test')
        response = self.app.get(invitation_form_view_url)
        form = response.forms[1]
        form['member_email'] = self.email_first.email
        form['language'] = self.language.id
        form['email_body'] = 'Hello, World {{ invitation_url }}'
        form_response = form.submit()
        res = form.submit()
        form_from_context = res.context['form']
        self.assertEqual(form_from_context.errors['member_email'], ['This email address already invited'])
