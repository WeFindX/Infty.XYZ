from django.contrib import admin

from .models import User
from .models import ConversationInvite

admin.site.register(User)
admin.site.register(ConversationInvite)
