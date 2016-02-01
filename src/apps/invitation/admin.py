from django.contrib import admin

from .models import Invitation
from .models import InvitationLetterTemplate
from .models import InvitationOption


admin.site.register(Invitation)
admin.site.register(InvitationLetterTemplate)
admin.site.register(InvitationOption)
