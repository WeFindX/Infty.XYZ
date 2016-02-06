from django.utils.translation import ugettext as _
from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import (
    Submit, HTML, Layout, Fieldset, ButtonHolder
)
from django_select2.forms import ModelSelect2Widget

from core.models import Language


class InvitationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(InvitationForm, self).__init__(*args, **kwargs)

        self.fields['member_email'] = forms.EmailField()

        self.fields['email_body'] = forms.CharField(widget=forms.Textarea)
        self.fields['email_body'].help_text = _("You can use {{ invitation_url }} tag to past invitation url")
        self.fields['language'] = forms.ModelChoiceField(
            widget=ModelSelect2Widget(
                queryset=Language.objects.all(),
                search_fields=['name__icontains']
            ),
            queryset=Language.objects.all()
        )

        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Fieldset(
                'Send Invitation',
                'member_email',
                'language',
                'email_body',
                HTML("Invitations left: %s" % user.invitationoption.invitations_left),
                FormActions(
                    Submit('submit', 'Send', css_class='button')
                )
            )
        )
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-8'
