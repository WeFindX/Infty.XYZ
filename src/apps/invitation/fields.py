from django import forms
from django.core.validators import EmailValidator


class MultipleEmailsField(forms.Field):
    def clean(self, value):
        """
        Check that the field contains one or more comma-separated emails
        and normalizes the data to a list of the email strings.
        """
        if not value:
            raise forms.ValidationError('Enter at least one e-mail address separated by comma.')
        emails = [email.strip() for email in value.split(',')]
        email_validator = EmailValidator()
        for email in emails:
            email_validator(email)

        # Always return the cleaned data.
        return emails
