# -*- coding: utf-8 -*-

from django import forms
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import (
    Submit, HTML, Layout, Fieldset, Field
)
from allauth.account.forms import SignupForm as AllAuthSignupForm
from allauth.account.forms import LoginForm as AllAuthLoginForm

from .models import User
from .models import ConversationInvite


class ConversationInviteForm(forms.ModelForm):
    invitation_text = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(ConversationInviteForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Fieldset(
                _('Invite to this conversation'),
                Field('name'),
                Field('email'),
                Field('invitation_text'),
                FormActions(
                    Submit('invite', _('Send invite'))
                )
            )
        )

        self.fields['name'].label = _('New Username')
        self.fields['email'].label = _('Email')
        self.fields['invitation_text'].label = _('Invitation text')
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-8'

    class Meta:
        model = ConversationInvite
        fields = [
            'name',
            'email',
            'invitation_text',
        ]


class UserUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        self.helper.layout.append(Submit('save', _('Update')))

    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'about',
        ]


class LoginForm(AllAuthLoginForm):

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout.append(Submit('login_form', _('Login')))
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-8'


class SignUpUserForm(AllAuthSignupForm):

    email = forms.EmailField(
        max_length=150,
        required=True,
    )

    username = forms.CharField(
        max_length=100,
        required=True,
    )

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(SignUpUserForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout.append(Submit('signup_user_form', _('SignUp')))
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-8'
        self.helper.form_action = reverse('register') + '?user_type=user'
        self.helper.form_action += "&next=%s" % request.GET.get('next', '')

    def save(self, request):
        user = super(SignUpUserForm, self).save(request)
        setattr(user, 'email', self.cleaned_data.get('email'))
        setattr(user, 'username', self.cleaned_data.get('username'))
        user.save()
        return user
