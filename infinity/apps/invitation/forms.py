from django.utils.translation import ugettext as _
from django import forms

from django_select2.widgets import AutoHeavySelect2Widget
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import (
    Submit, HTML, Layout, Fieldset
)

from core.models import Language
from .fields import MultipleEmailsField
from .fields import LanguageChoiceField


class InvitationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(InvitationForm, self).__init__(*args, **kwargs)

        self.fields['member_email'] = forms.EmailField()

        self.fields['email_body'] = forms.CharField(widget=forms.Textarea)
        self.fields['email_body'].help_text = _("You can use {{ invitation_url }} tag to past invitation url")
        self.fields['language'] = LanguageChoiceField(
            queryset=Language.objects.all(),
            widget=AutoHeavySelect2Widget(
                select2_options={
                    'minimumInputLength': 0
                }
            )
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
