from django.contrib import admin

from .models import Language
from .models import Definition
from .models import Vote
from .models import Type
from .models import Goal
from .models import Need
from .models import Idea
from .models import Plan
from .models import Step
from .models import Task
from .models import Work
from .models import Comment
from .models import Translation


class LanguageAdmin(admin.ModelAdmin):
    list_display = ('omegawiki_language_id', 'name',)


admin.site.register(Language, LanguageAdmin)
admin.site.register(Definition)
admin.site.register(Comment)
admin.site.register(Vote)
admin.site.register(Type)
admin.site.register(Need)
admin.site.register(Goal)
admin.site.register(Idea)
admin.site.register(Plan)
admin.site.register(Step)
admin.site.register(Task)
admin.site.register(Work)
admin.site.register(Translation)
