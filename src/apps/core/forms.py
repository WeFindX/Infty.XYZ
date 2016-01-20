from django.utils.translation import ugettext_lazy as _
from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Div, Button
from django.core.urlresolvers import reverse


from core.models import Language
from core.models import Definition
from core.models import Need
from core.models import Goal
from core.models import Idea
from core.models import Plan
from core.models import Step
from core.models import Task
from core.models import Work
from core.models import Type
from core.models import Comment

from django.contrib.contenttypes.models import ContentType
from django_select2.forms import ModelSelect2MultipleWidget
from django_select2.forms import ModelSelect2Widget
from django_markdown.widgets import MarkdownWidget

from decimal import Decimal
from core.models import Translation
from users.models import User


class ChangePriorityForm(forms.Form):
    steps = forms.CharField()


class ContentTypeSubscribeForm(forms.Form):
    object_id = forms.IntegerField()
    content_type = forms.ModelChoiceField(
        queryset=ContentType.objects.filter(
            model__in=[
                'need', 'goal', 'idea', 'plan', 'step', 'task','work'
            ]
        )
    )


class TranslationCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        content_type_instance = kwargs.pop('content_type_instance')
        super(TranslationCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        content_type = ContentType.objects.get_for_model(content_type_instance)
        translations = Translation.objects.filter(
            content_type=content_type,
            object_id=content_type_instance.pk
        )

        self.fields['language'] = forms.ModelChoiceField(
            widget=ModelSelect2Widget(
                queryset=Language.objects.all().exclude(id__in=[
                    translation.language.id for translation in translations
                ]),
                search_fields=['name__icontains']
            ),
            queryset=Language.objects.all().exclude(id__in=[
                translation.language.id for translation in translations
            ])
        )
        self.helper.layout.append(Submit('save', _('Create')))
        self.fields['name'] = forms.CharField()
        self.fields['content'] = forms.CharField(widget=MarkdownWidget())
        self.fields['summary'] = forms.CharField()
        self.fields['description'] = forms.CharField(widget=MarkdownWidget())
        self.fields['reason'] = forms.CharField(widget=MarkdownWidget())
        self.fields['objective'] = forms.CharField(widget=MarkdownWidget())
        self.fields['situation'] = forms.CharField(widget=MarkdownWidget())
        self.fields['deliverable'] = forms.CharField(widget=MarkdownWidget())
        self.fields['investables'] = forms.CharField()
        self.fields['deliverables'] = forms.CharField()

    class Meta:
        model = Translation
        exclude = ['content_type', 'object_id', 'content_object']


class TranslationUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        #content_type_instance = kwargs.pop('content_type_instance')
        super(TranslationUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout.append(Submit('save', _('Update')))
        self.fields['name'] = forms.CharField()
        self.fields['content'] = forms.CharField(widget=MarkdownWidget())
        self.fields['summary'] = forms.CharField()
        self.fields['description'] = forms.CharField(widget=MarkdownWidget())
        self.fields['reason'] = forms.CharField(widget=MarkdownWidget())
        self.fields['objective'] = forms.CharField(widget=MarkdownWidget())
        self.fields['situation'] = forms.CharField(widget=MarkdownWidget())
        self.fields['deliverable'] = forms.CharField(widget=MarkdownWidget())
        self.fields['investables'] = forms.CharField()
        self.fields['deliverables'] = forms.CharField()

    class Meta:
        model = Translation
        exclude = ['language', ]


class CommentCreateFormDetail(forms.ModelForm):

    amount = forms.DecimalField(required=False)

    USD = 0
    EUR = 1

    CURRENCIES = (
        (USD, _("USD")),
        (EUR, _("EUR"))
    )

    currency = forms.ChoiceField(choices=CURRENCIES, required=False)


    def __init__(self, *args, **kwargs):
        super(CommentCreateFormDetail, self).__init__(*args, **kwargs)

        self.fields['text'].label = _("""<b>Comment</b> (to claim hours, just
                                      enclose a number within curly braces, e.g.,
                                      {1.5} h. You can do it multiple times in
                                      one comment, and use {?1.5} to indicate
                                      estimates.""")
        self.fields['notify'].label = _('Notify mentioned users (e.g., <i>Hi [User], how are you?</i>) by e-mail.')
        self.fields['amount'].label = _('Amount')
        self.fields['currency'].label = _('Currency')
        self.fields['amount'].initial = Decimal(0)
        self.helper = FormHelper(self)

        self.helper.layout.append(Submit('save', _('Send Comment')))

    class Meta:
        model = Comment
        fields = [
            'text',
            'notify'
        ]
        widgets = {
            'text': MarkdownWidget,
        }


class CommentUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CommentUpdateForm, self).__init__(*args, **kwargs)
        self.fields['text'].label = _('Comment')
        self.fields['notify'].label = _('Notify mentioned users by e-mail.')

        self.helper = FormHelper(self)

        self.helper.layout.append(Submit('save', _('Update')))

    class Meta:
        model = Comment
        fields = [
            'text',
            'notify'
        ]
        widgets = {
            'text': MarkdownWidget,
        }


class NeedCreateForm(forms.ModelForm):

    content = forms.CharField(widget=MarkdownWidget())

    def __init__(self, *args, **kwargs):
        definition_instance = kwargs.pop('definition_instance')
        request = kwargs.pop('request')
        super(NeedCreateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        self.helper.layout.append(Submit('save', _('Create')))

        if definition_instance:
            self.initial['definition'] = definition_instance
            self.fields['definition'].widget = forms.HiddenInput()
        else:
            self.fields['definition'] = forms.ModelChoiceField(
                widget=ModelSelect2Widget(
                    queryset=Definition.objects.all(),
                    search_fields=['name__icontains', ]
                ),
                queryset=Definition.objects.all()
            )

        self.fields['language'] = forms.ModelChoiceField(
            widget=ModelSelect2Widget(
                queryset=Language.objects.all(),
                search_fields=['name__icontains']
            ),
            queryset=Language.objects.all()
        )

        self.fields['sharewith'] = forms.ModelMultipleChoiceField(
            widget=ModelSelect2MultipleWidget(
                queryset=User.objects.all(),
                search_fields=['username__icontains']
            ),
            queryset=User.objects.all(),
            required=False
        )

        self.fields['definition'].label = _("""<b>Topic:</b> (relevant to problem,
                                      <a href="/definition-create/">click here</a> to
                                      add if you can't find it.)""")
        self.fields['name'].label = _("""<b>Subject:</b>""")
        self.fields['name'].widget.attrs.update({'placeholder': _('e.g., "Hi friends, who would also want a spaceship?"')})
        self.fields['content'].label = _('')
        self.fields['content'].widget.attrs.update({'placeholder': _('e.g., "I have been dreaming about travelling to explore other planets since childhood. I would enjoy going on a long journey to the unknown together with a group of close friends living in the spaceship like one family. It is not impossible. Who would like to join me in an attempt to consider all possible ways how we could do it, from laws of physics to specific designs and logistics."')})
        self.fields['personal'].label = _('<b>Personal</b> (makes the entry visible only to a chosen set of people)')
        self.fields['language'].label = _('<b>Input Language</b> (the language you used to compose this post) ')
        self.initial['personal'] = True

        try:
            language = Language.objects.get(language_code=request.LANGUAGE_CODE)
            self.initial['language'] = language
        except Language.DoesNotExist:
            pass

    class Meta:
        model = Need
        exclude = [
            'user',
        ]
        fields = [
            'name',
            'definition',
            'content',
            'language',
            'personal',
            'sharewith',
        ]


class NeedUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NeedUpdateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        self.helper.layout.append(Submit('save', _('Update')))

        self.fields['name'].label = 'Description'
        self.fields['name'].widget.attrs['readonly'] = True

        self.fields['language'] = forms.ModelChoiceField(
            widget=ModelSelect2Widget(
                queryset=Language.objects.all(),
                search_fields=['name__icontains']
            ),
            queryset=Language.objects.all()
        )

        self.fields['sharewith'] = forms.ModelMultipleChoiceField(
            widget=ModelSelect2MultipleWidget(
                queryset=User.objects.all(),
                search_fields=['username__icontains']
            ),
            queryset=User.objects.all(), required=False)

        self.fields['language'].label = _('<b>Input Language</b> (the language you used to compose this post) ')
        self.fields['content'].widget.attrs['readonly'] = True

    class Meta:
        model = Need
        exclude = [
            'created_at',
            'user',
        ]
        fields = [
            'name',
            'content',
            'language',
            'personal',
            'sharewith',
        ]
        widgets = {
            'content': MarkdownWidget,
        }




class GoalCreateForm(forms.ModelForm):

    reason = forms.CharField(widget=MarkdownWidget())

#   hyper_equity = forms.ChoiceField(choices=[(Decimal(x*0.0001), '%.2f' % (x*0.01)+ '%') for x in range(1,11)])

    def __init__(self, *args, **kwargs):
        need_instance = kwargs.pop('need_instance')
        request = kwargs.pop('request')
        super(GoalCreateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        self.helper.layout.append(Submit('save', _('Create')))

        if need_instance:
            self.initial['need'] = need_instance

        self.fields['type'] = forms.ModelChoiceField(
            widget=ModelSelect2Widget(
                queryset=Type.objects.all(),
                search_fields=['name__icontains']
            ),
            queryset=Type.objects.all()
        )

        self.fields['need'] = forms.ModelChoiceField(
            widget=ModelSelect2Widget(
                queryset=Need.objects.all(),
                search_fields=['name__icontains']
            ),
            queryset=Need.objects.all(),
            required=False
        )

        self.fields['language'] = forms.ModelChoiceField(
            widget=ModelSelect2Widget(
                queryset=Language.objects.all(),
                search_fields=['name__icontains']
            ),
            queryset=Language.objects.all()
        )
        self.fields['sharewith'] = forms.ModelMultipleChoiceField(
            widget=ModelSelect2MultipleWidget(
                queryset=User.objects.all(),
                search_fields=['username__icontains']
            ),
            queryset=User.objects.all(),
            required=False
        )

        self.fields['type'].label = _("<b>Problem category:</b>")
        self.fields['need'].label = _("""<b>Related Need:</b> (Optional)""")
        self.fields['name'].label = _("""<b>Title:</b> (e.g., Potable Water
                                      Shortage, <a href="/goal/list/">check</a> if the problem is not
                                      defined yet.)""")
        self.fields['name'].widget.attrs.update({'placeholder': _('')})
        self.fields['reason'].label = _('<b>Description:</b> (e.g., Many people in the world lack clean potable water.)')
        self.fields['reason'].widget.attrs.update({'placeholder': \
        _('')})
        self.fields['personal'].label = _('<b>Personal</b> (makes the entry visible only to a chosen set of people)')
        self.fields['language'].label = _('<b>Input Language</b> (the language you used to compose this post) ')
#       self.fields['hyper_equity'].label = _('Hyper equity')
        self.fields['is_link'].label = _('<b>This is a link</b> (check if you are only linking to existing content)')
        self.fields['url'].label = _('<b>Origin:</b> (of the source)')
        self.fields['url'].widget.attrs.update({'placeholder': _('http://')})
        self.fields['is_historical'].label = _('<b>This is a history</b> (check if you are documenting a problem of the past)')
        self.initial['personal'] = True

        if need_instance:
            self.initial['sharewith'] = need_instance.sharewith.all
            self.initial['personal'] = need_instance.personal

        try:
            language = Language.objects.get(language_code=request.LANGUAGE_CODE)
            self.initial['language'] = language
        except Language.DoesNotExist:
            pass


    class Meta:
        model = Goal
        exclude = [
            'user',
        ]
        fields = [
            'is_link',
            'url',
            'is_historical',
            'type',
            'name',
            'need',
            'reason',
            'language',
            'personal',
            'sharewith',
        ]


class GoalUpdateForm(forms.ModelForm):

#   hyper_equity = forms.ChoiceField(choices=[(Decimal(x*0.0001), '%.2f' % (x*0.01)+ '%') for x in range(1,11)])

    def __init__(self, *args, **kwargs):
        super(GoalUpdateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        self.helper.layout.append(Submit('save', _('Update')))

        self.fields['name'].label = 'Description'
        self.fields['name'].widget.attrs['readonly'] = True
        self.fields['need'] = forms.ModelChoiceField(queryset=Need.objects.all())

        self.fields['type'] = forms.ModelChoiceField(
            widget=ModelSelect2Widget(
                queryset=Type.objects.all(),
                search_fields=['name__icontains']
            ),
            queryset=Type.objects.all()
        )

        self.fields['need'] = forms.ModelChoiceField(
            widget=ModelSelect2Widget(
                queryset=Need.objects.all(),
                search_fields=['name__icontains']
            ),
            queryset=Need.objects.all(),
            required=False
        )

        self.fields['language'] = forms.ModelChoiceField(
            widget=ModelSelect2Widget(
                queryset=Language.objects.all(),
                search_fields=['name__icontains']
            ),
            queryset=Language.objects.all()
        )

        self.fields['sharewith'] = forms.ModelMultipleChoiceField(
            widget=ModelSelect2MultipleWidget(
                queryset=User.objects.all(),
                search_fields=['username__icontains']
            ),
            queryset=User.objects.all(), required=False)

        self.fields['language'].label = _('<b>Input Language</b> (the language you used to compose this post) ')
#       self.fields['hyper_equity'].label = _('Hyper equity')
        self.fields['is_link'].label = _('<b>This is a link</b> (check if you are only linking to existing content)')
        self.fields['url'].label = _('<b>Origin:</b> (of the source)')
        self.fields['url'].widget.attrs.update({'placeholder': _('http://')})
        self.fields['is_historical'].label = _('<b>This is a history</b> (check if you are documenting a problem of the past)')
        self.fields['reason'].widget.attrs['readonly'] = True

    class Meta:
        model = Goal
        exclude = [
            'created_at',
            'user',
        ]
        fields = [
            'is_link',
            'url',
            'is_historical',
            'type',
            'name',
            'need',
            'reason',
            'language',
            'personal',
            'sharewith',
        ]
        widgets = {
            'reason': MarkdownWidget,
        }


class WorkUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(WorkUpdateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        self.helper.layout.append(Submit('save', _('Update')))

        self.fields['task'] = forms.ModelChoiceField(
            widget=ModelSelect2Widget(
                queryset=Task.objects.all(),
                search_fields=['name__icontains']
            ),
            queryset=Task.objects.all()
        )
        self.fields['sharewith'] = forms.ModelMultipleChoiceField(
            widget=ModelSelect2MultipleWidget(
                queryset=User.objects.all(),
                search_fields=['username__icontains']
            ),
            queryset=User.objects.all(), required=False)
        self.fields['language'] = forms.ModelChoiceField(
            widget=ModelSelect2Widget(
                queryset=Language.objects.all(),
                search_fields=['name__icontains']
            ),
            queryset=Language.objects.all()
        )

        self.fields['language'].label = _('<b>Input Language</b> (the language you used to compose this post) ')
        self.fields['is_link'].label = _('<b>This is a link</b> (check if you are only linking to existing content)')
        self.fields['url'].label = _('<b>Origin:</b> (of the source)')
        self.fields['url'].widget.attrs.update({'placeholder': _('http://')})
        self.fields['is_historical'].label = _('<b>This is a history</b> (check if you are documenting a historical work)')
        self.fields['name'].widget.attrs['readonly'] = True
        self.fields['description'].widget.attrs['readonly'] = True

    class Meta:
        model = Work
        exclude = [
            'created_at',
            'user',
        ]
        fields = [
            'task',
            'is_link',
            'url',
            'is_historical',
            'name',
            'file',
            'description',
            'parent_work_id',
            'language',
            'personal',
            'sharewith',
        ]
        widgets = {
            'description': MarkdownWidget,
        }


class WorkCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        task_instance = kwargs.pop('task_instance') 
        request = kwargs.pop('request')
        super(WorkCreateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        self.helper.layout.append(Submit('save', _('Create')))

        self.fields['language'] = forms.ModelChoiceField(
            widget=ModelSelect2Widget(
                queryset=Language.objects.all(),
                search_fields=['name__icontains']
            ),
            queryset=Language.objects.all()
        )

        self.fields['sharewith'] = forms.ModelMultipleChoiceField(
            widget=ModelSelect2MultipleWidget(
                queryset=User.objects.all(),
                search_fields=['name__icontains']
            ),
            queryset=User.objects.all()
        )

        self.fields['name'].label = _('<b>Name:</b> (e.g., "First attempt to assemble solar cells.", used in title.)')
        self.fields['name'].widget.attrs.update({'placeholder': _('Give a title to your work.')})
        self.fields['description'].label = _('<b>Description:</b> (details about the work, used as body.)')
        self.fields['description'].widget.attrs.update({'placeholder': _('Here is a little story of my work.')})
        self.fields['file'].label = _('<b>File:</b> (you can upload a file describing your work)')
        self.fields['file'].widget.attrs.update({'placeholder': _('http://')})
        self.fields['parent_work_id'].label = _('<b>Parent Work Id:</b> (integer referring to other work)')
        self.fields['parent_work_id'].widget.attrs.update({'placeholder': _('optional')})
        self.fields['personal'].label = _('<b>Personal</b> (makes the entry visible only to a chosen set of people)')
        self.fields['language'].label = _('<b>Input Language</b> (the language you used to compose this post) ')
        self.fields['is_link'].label = _('<b>This is a link</b> (check if you are only linking to existing content)')
        self.fields['url'].label = _('<b>Origin:</b> (of the source)')
        self.fields['url'].widget.attrs.update({'placeholder': _('http://')})
        self.fields['is_historical'].label = _('<b>This is a history</b> (check if you are documenting a historical work)')
        self.initial['personal'] = True

        if task_instance:
            self.initial['sharewith'] = task_instance.sharewith.all
            self.initial['personal'] = task_instance.personal

        try:
            language = Language.objects.get(language_code=request.LANGUAGE_CODE)
            self.initial['language'] = language
        except Language.DoesNotExist:
            pass

    class Meta:
        model = Work
        exclude = [
            'task',
            'user',
        ]
        fields = [
            'is_link',
            'url',
            'is_historical',
            'name',
            'description',
            'file',
            'parent_work_id',
            'language',
            'personal',
            'sharewith',
        ]
        widgets = {
            'description': MarkdownWidget,
        }


class IdeaUpdateForm(forms.ModelForm):

#   super_equity = forms.ChoiceField(
#       choices=[(Decimal(x*0.01), '%.0f' % (x*1.)+ '%') for x in range(1,11)]
#   )

    def __init__(self, *args, **kwargs):
        super(IdeaUpdateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        self.helper.layout.append(Submit('save', _('Update')))

        self.fields['goal'] = forms.ModelMultipleChoiceField(
            widget=ModelSelect2MultipleWidget(
                queryset=Goal.objects.all(),
                search_fields=['name__icontains']
            ),
            queryset=Goal.objects.all()
        )
        self.fields['language'] = forms.ModelChoiceField(
            widget=ModelSelect2Widget(
                queryset=Language.objects.all(),
                search_fields=['name__icontains']
            ),
            queryset=Language.objects.all()
        )
        self.fields['sharewith'] = forms.ModelMultipleChoiceField(
            widget=ModelSelect2MultipleWidget(
                queryset=User.objects.all(),
                search_fields=['username__icontains']
            ),
            queryset=User.objects.all(), required=False)

        self.fields['language'].label = _('<b>Input Language</b> (the language you used to compose this post) ')
        self.fields['is_link'].label = _('<b>This is a link</b> (check if you are only linking to existing content)')
        self.fields['url'].label = _('<b>Origin:</b> (of the source)')
        self.fields['url'].widget.attrs.update({'placeholder': _('http://')})
        self.fields['is_historical'].label = _('<b>This is a history</b> (check if you are documenting an idea of the past)')
        self.fields['name'].widget.attrs['readonly'] = True
        self.fields['summary'].widget.attrs['readonly'] = True
        self.fields['description'].widget.attrs['readonly'] = True

    class Meta:
        model = Idea
        exclude = [
            'created_at',
            'user',
        ]
        fields = [
            'is_link',
            'url',
            'is_historical',
            'goal',
            'name',
            'summary',
            'description',
            'language',
            'personal',
            'sharewith',
        ]
        widgets = {
            'description': MarkdownWidget,
        }


class IdeaCreateForm(forms.ModelForm):


#   super_equity = forms.ChoiceField(
#       choices=[(Decimal(x*0.01), '%.0f' % (x*1.)+ '%') for x in range(1,11)]
#   )

    def __init__(self, *args, **kwargs):
        goal_instance = kwargs.pop('goal_instance')
        request = kwargs.pop('request')

        super(IdeaCreateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        self.helper.layout.append(Submit('save', _('Create')))

        if goal_instance:
            self.initial['goal'] = [goal_instance, ]

        self.fields['goal'] = forms.ModelMultipleChoiceField(
            widget=ModelSelect2MultipleWidget(
                queryset=Goal.objects.all(),
                search_fields=['name__icontains']
            ),
            queryset=Goal.objects.all()
        )
        self.fields['language'] = forms.ModelChoiceField(
            widget=ModelSelect2Widget(
                queryset=Language.objects.all(),
                search_fields=['name__icontains']
            ),
            queryset=Language.objects.all()
        )
        self.fields['sharewith'] = forms.ModelMultipleChoiceField(
            widget=ModelSelect2MultipleWidget(
                queryset=User.objects.all(),
                search_fields=['username__icontains']
            ),
            queryset=User.objects.all(), required=False)
        self.fields['goal'].label = _('Goals')

        self.fields['name'].label = _('<b>Name:</b> (e.g., "Solar Water Condenser", used in title.)')
        self.fields['summary'].label = _('<b>Summary:</b> (e.g., "Use solar panels and Peltier effect to extract water from air.", appears as subtitle.)')
        self.fields['description'].label = _('<b>Description:</b> (write full description here, used as body.)')
        self.fields['personal'].label = _('<b>Personal</b> (makes the entry visible only to a chosen set of people)')
        self.fields['language'].label = _('<b>Input Language</b> (the language you used to compose this post) ')
#       self.fields['super_equity'].label = _('Super equity')
        self.fields['sharewith'].label = _('Share with:')
        self.fields['is_link'].label = _('<b>This is a link</b> (check if you are only linking to existing content)')
        self.fields['url'].label = _('<b>Origin:</b> (of the source)')
        self.fields['url'].widget.attrs.update({'placeholder': _('http://')})
        self.fields['is_historical'].label = _('<b>This is a history</b> (check if you are documenting an idea of the past)')
        self.initial['personal'] = True

        if goal_instance:
            self.initial['sharewith'] = goal_instance.sharewith.all
            self.initial['personal'] = goal_instance.personal

        try:
            language = Language.objects.get(language_code=request.LANGUAGE_CODE)
            self.initial['language'] = language
        except Language.DoesNotExist:
            pass

    class Meta:
        model = Idea
        exclude = [
            'created_at',
            'user',
        ]
        fields = [
            'is_link',
            'url',
            'is_historical',
            'goal',
            'name',
            'summary',
            'description',
            'language',
            'personal',
            'sharewith',
        ]
        widgets = {
            'description': MarkdownWidget,
        }


class StepUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(StepUpdateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        self.helper.layout.append(Submit('save', _('Update')))
        self.fields['sharewith'] = forms.ModelMultipleChoiceField(
            widget=ModelSelect2MultipleWidget(
                queryset=User.objects.all(),
                search_fields=['username__icontains']
            ),
            queryset=User.objects.all(), required=False)
        self.fields['plan'] = forms.ModelChoiceField(
            widget=ModelSelect2Widget(
                queryset=Plan.objects.all(),
                search_fields=['name__icontains']
            ),
            queryset=Plan.objects.all()
        )
        self.fields['language'] = forms.ModelChoiceField(
            widget=ModelSelect2Widget(
                queryset=Language.objects.all(),
                search_fields=['name__icontains']
            ),
            queryset=Language.objects.all()
        )
        self.fields['language'].label = _('<b>Input Language</b> (the language you used to compose this post) ')
        self.fields['is_link'].label = _('<b>This is a link</b> (check if you are only linking to existing content)')
        self.fields['url'].label = _('<b>Origin:</b> (of the source)')
        self.fields['url'].widget.attrs.update({'placeholder': _('http://')})
        self.fields['is_historical'].label = _('<b>This is a history</b> (check if you are documenting a milestone of the past)')
        self.fields['name'].widget.attrs['readonly'] = True
        self.fields['objective'].widget.attrs['readonly'] = True

    class Meta:
        model = Step
        exclude = [
            'created_at',
            'updated_at',
            'user',
        ]
        fields = [
            'plan',
            'is_link',
            'url',
            'is_historical',
            'name',
            'objective',
            'priority',
            'investables',
            'deliverables',
            'language',
            'personal',
            'sharewith',
        ]
        widgets = {
            'objective': MarkdownWidget,
        }


class StepCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        plan_instance = kwargs.pop('plan_instance')
        request = kwargs.pop('request')
        super(StepCreateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        self.helper.layout.append(Submit('save', _('Create')))
        self.fields['language'] = forms.ModelChoiceField(
            widget=ModelSelect2Widget(
                queryset=Language.objects.all(),
                search_fields=['name__icontains']
            ),
            queryset=Language.objects.all()
        )
        self.fields['sharewith'] = forms.ModelMultipleChoiceField(
            widget=ModelSelect2MultipleWidget(
                queryset=User.objects.all(),
                search_fields=['username__icontains']
            ),
            queryset=User.objects.all(), required=False)

        self.fields['name'].label = _('<b>Milestone:</b> (e.g., "assemble solar panels", used in title.)')
        self.fields['name'].widget.attrs.update({'placeholder': _('Type the name of the milestone.')})
        self.fields['objective'].label = _("<b>Objective:</b> (describe conditions, when you will consider the milestone to be 'achieved')")
        self.fields['objective'].widget.attrs.update({'placeholder': _("Example:\n\nWe have solar cell assembly, which:\n- Generates expected electric power output\n- Passes certain tests of reliability.")})
        self.fields['priority'].label = _("<b>Priority:</b> (integer, e.g., 1,2,3.. - used for ordering, smaller number means the milestone has to be done earlier)")
        self.fields['investables'].label = _('<b>Investables:</b> (e.g., enumerate the ranges of quantities you expect to invest on this milestone in <a href="https://github.com/mindey/IdeaLib#minimal">IDL syntax</a>, used used for value computation.)')
        self.fields['investables'].widget.attrs.update({'placeholder': _('people 1\\3, days 10\\20, usd 50\\70')})
        self.fields['deliverables'].label = _('<b>Deliverables:</b> (e.g., enumerate the ranges of quantities you expect to have by completion of this milestone in <a href="https://github.com/mindey/IdeaLib#minimal">IDL syntax</a>, used used for value computation.)')
        self.fields['deliverables'].widget.attrs.update({'placeholder': _('complete solar assembly drawings 0\\1, solar cell assembly 1\\2')})
        self.fields['personal'].label = _('<b>Personal</b> (makes the entry visible only to a chosen set of people)')
        self.fields['language'].label = _('<b>Input Language</b> (the language you used to compose this post) ')
        self.fields['is_link'].label = _('<b>This is a link</b> (check if you are only linking to existing content)')
        self.fields['url'].label = _('<b>Origin:</b> (of the source)')
        self.fields['url'].widget.attrs.update({'placeholder': _('http://')})
        self.fields['is_historical'].label = _('<b>This is a history</b> (check if you are documenting a milestone of the past)')
        self.initial['personal'] = True

        if plan_instance:
            self.initial['sharewith'] = plan_instance.sharewith.all
            self.initial['personal'] = plan_instance.personal

        try:
            language = Language.objects.get(language_code=request.LANGUAGE_CODE)
            self.initial['language'] = language
        except Language.DoesNotExist:
            pass

    class Meta:
        model = Step
        exclude = [
            'plan',
            'updated_at',
            'created_at',
            'user',
        ]
        fields = [
            'is_link',
            'url',
            'is_historical',
            'name',
            'objective',
            'priority',
            'investables',
            'deliverables',
            'language',
            'personal',
            'sharewith',
        ]
        widgets = {
            'objective': MarkdownWidget,
        }


class TaskUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(TaskUpdateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        self.helper.layout.append(Submit('save', _('Update')))
        self.fields['step'] = forms.ModelChoiceField(
            widget=ModelSelect2Widget(
                queryset=Step.objects.all(),
                search_fields=['name__icontains']
            ),
            queryset=Step.objects.all()
        )
        self.fields['sharewith'] = forms.ModelMultipleChoiceField(
            widget=ModelSelect2MultipleWidget(
                queryset=User.objects.all(),
                search_fields=['username__icontains']
            ),
            queryset=User.objects.all(), required=False)
        self.fields['language'] = forms.ModelChoiceField(
            widget=ModelSelect2Widget(
                queryset=Language.objects.all(),
                search_fields=['name__icontains']
            ),
            queryset=Language.objects.all()
        )

        self.fields['language'].label = _('<b>Input Language</b> (the language you used to compose this post) ')
        self.fields['is_link'].label = _('<b>This is a link</b> (check if you are only linking to existing content)')
        self.fields['url'].label = _('<b>Origin:</b> (of the source)')
        self.fields['url'].widget.attrs.update({'placeholder': _('http://')})
        self.fields['is_historical'].label = _('<b>This is a history</b> (check if you are documenting a historical task)')
        self.fields['name'].widget.attrs['readonly'] = True
        self.fields['description'].widget.attrs['readonly'] = True

    class Meta:
        model = Task
        exclude = [
            'created_at',
            'updated_at',
            'user',
        ]
        fields = [
            'step',
            'is_link',
            'url',
            'is_historical',
            'name',
            'description',
            'priority',
            'language',
            'personal',
            'sharewith',
        ]


class TaskCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        step_instance = kwargs.pop('step_instance')
        request = kwargs.pop('request')
        super(TaskCreateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        self.helper.layout.append(Submit('save', _('Create')))
        self.fields['language'] = forms.ModelChoiceField(
            widget=ModelSelect2Widget(
                queryset=Language.objects.all(),
                search_fields=['name__icontains']
            ),
            queryset=Language.objects.all()
        )
        self.fields['sharewith'] = forms.ModelMultipleChoiceField(
            widget=ModelSelect2MultipleWidget(
                queryset=User.objects.all(),
                search_fields=['username__icontains']
            ),
            queryset=User.objects.all(),
            required=False
        )
        self.fields['name'].label = _('<b>Task:</b> (e.g., "Purchase solar cells", text in title.)')
        self.fields['name'].widget.attrs.update({'placeholder': _('Type the name of the task.')})
        self.fields['priority'].label = _("<b>Priority:</b> (integer, e.g., 1,2,3.. - used for ordering, smaller number means the task has to be done earlier)")
        self.fields['language'].label = _('<b>Input Language</b> (the language you used to compose this post) ')
        self.fields['is_link'].label = _('<b>This is a link</b> (check if you are only linking to existing content)')
        self.fields['url'].label = _('<b>Origin:</b> (of the source)')
        self.fields['url'].widget.attrs.update({'placeholder': _('http://')})
        self.fields['is_historical'].label = _('<b>This is a history</b> (check if you are documenting a historical task)')
        self.initial['personal'] = True

        if step_instance:
            self.initial['sharewith'] = step_instance.sharewith.all
            self.initial['personal'] = step_instance.personal

        try:
            language = Language.objects.get(language_code=request.LANGUAGE_CODE)
            self.initial['language'] = language
        except Language.DoesNotExist:
            pass

    class Meta:
        model = Task
        exclude = [
            'step',
            'created_at',
            'updated_at',
            'user',
        ]
        fields = [
            'is_link',
            'url',
            'is_historical',
            'name',
            'description',
            'priority',
            'language',
            'personal',
            'sharewith',
        ]


class DefinitionCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(DefinitionCreateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.fields['language'] = forms.ModelChoiceField(
            widget=ModelSelect2Widget(
                queryset=Language.objects.all(),
                search_fields=['name__icontains']
            ),
            queryset=Language.objects.all()
        )
        self.fields['sharewith'] = forms.ModelMultipleChoiceField(
            widget=ModelSelect2MultipleWidget(
                queryset=User.objects.all(),
                search_fields=['username__icontains']
            ),
            queryset=User.objects.all(), required=False)

        if self.request.user.is_anonymous():
            submit_button = Div(
                Field(Button('register', _('Add & Go'),
                             onclick="window.location.assign('%s')" % reverse("account_signup"))),
                css_class='col-sm-2 create-button disabled',
            )
        else:
            submit_button = Div(
                Field(Submit('submit', _('Add & Go'))),
                css_class='col-sm-2 create-button',
            )

        self.helper.layout = Layout(
            Div(
                Div('language', css_class='col-sm-2',),
                Div(
                    Field('name', placeholder=kwargs.pop('query_placeholder',
                                                         _("")),
                          autocomplete='off',
                    ),
                    css_class='col-sm-10',
                ),
                css_class='row'
            ),
            Div(
                Div(
                    Div(
                        css_class='col-sm-12 hints-block',
                    ),
                    Div(
                        Field(
                            'definition', placeholder=kwargs.pop('query_placeholder', _("definition, e.g., 'spaceflight beyond the bounderies of galaxies'")),
                            autocomplete='off',
                        ),
                        css_class='col-sm-10',
                    ),
                    submit_button,
                ),
                css_class='row',
                css_id='div_id_define',
            ),
        )
        self.fields['name'].label = ''
        self.fields['language'].label = ''
        self.fields['definition'].label = ''
        self.initial['language'] = Language.objects.get(language_code=self.request.LANGUAGE_CODE)


    class Meta:
        model = Definition
        fields = [
            'name',
            'language',
            'definition',
            'sharewith',
        ]
        widgets = {
            'name': forms.TextInput,
            'definition': forms.TextInput,
        }


class DefinitionUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(DefinitionUpdateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        self.helper.layout.append(Submit('save', _('Update')))

    class Meta:
        model = Definition
        fields = [
            'name',
            'language',
            'definition',
            'sharewith',
        ]


class PlanUpdateForm(forms.ModelForm):

#   plain_equity = forms.ChoiceField(
#       choices=[(Decimal(x*.1), '%.0f' % (x*10.)+ '%') for x in range(1,11)]
#   )

    goal = forms.ModelChoiceField(
        widget=ModelSelect2Widget(
            queryset=Goal.objects.all(),
            search_fields=['name__icontains']
        ),
        queryset=Goal.objects.all()
    )

    idea = forms.ModelChoiceField(
        widget=ModelSelect2Widget(
            queryset=Idea.objects.all(),
            search_fields=['name__icontains']
        ),
        queryset=Idea.objects.all()
    )

    def __init__(self, *args, **kwargs):
        super(PlanUpdateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        self.helper.layout.append(Submit('save', _('Update')))
        self.fields['sharewith'] = forms.ModelMultipleChoiceField(
            widget=ModelSelect2MultipleWidget(
                queryset=User.objects.all(),
                search_fields=['username__icontains']
            ),
            queryset=User.objects.all(),
            required=False
        )
        self.fields['members'] = forms.ModelMultipleChoiceField(
            widget=ModelSelect2MultipleWidget(
                queryset=User.objects.all(),
                search_fields=['username__icontains']
            ),
            queryset=User.objects.all(),
            required=False
        )
        self.fields['language'].label = _('<b>Input Language</b> (the language you used to compose this post) ')
        self.fields['is_link'].label = _('<b>This is a link</b> (check if you are only linking to existing content)')
        self.fields['url'].label = _('<b>Origin:</b> (of the source)')
        self.fields['url'].widget.attrs.update({'placeholder': _('http://')})
        self.fields['is_historical'].label = _('<b>This is a history</b> (check if you are documenting a project of the past)')
        self.fields['name'].widget.attrs['readonly'] = True
        self.fields['situation'].widget.attrs['readonly'] = True
        self.fields['deliverable'].widget.attrs['readonly'] = True


    class Meta:
        model = Plan
        exclude = [
            'created_at',
            'updated_at',
            'user',
        ]
        fields = [
            'is_link',
            'url',
            'is_historical',
            'goal',
            'idea',
            'name',
            'situation',
            'deliverable',
            'members',
            'language',
            'personal',
            'sharewith',
        ]
        widgets = {
            'situation': MarkdownWidget,
            'deliverable': MarkdownWidget,
        }


class PlanCreateForm(forms.ModelForm):

#   plain_equity = forms.ChoiceField(
#       choices=[(Decimal(x*.1), '%.0f' % (x*10.)+ '%') for x in range(1,11)]
#   )

    goal = forms.ModelChoiceField(
        widget=ModelSelect2Widget(
            queryset=Goal.objects.all(),
            search_fields=['name__icontains']
        ),
        queryset=Goal.objects.all()
    )

    idea = forms.ModelChoiceField(
        widget=ModelSelect2Widget(
            queryset=Idea.objects.all(),
            search_fields=['name__icontains'],
            data_view='heavy_data_idea_chained'
        ),
        queryset=Idea.objects.all()
    )

    def __init__(self, *args, **kwargs):
        idea_instance = kwargs.pop('idea_instance')
        request = kwargs.pop('request')
        super(PlanCreateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout.append(Submit('save', _('Create')))

        if idea_instance:
            self.initial['idea'] = idea_instance
            self.initial['goal'] = idea_instance.goal.first()

        self.fields['sharewith'] = forms.ModelMultipleChoiceField(
            widget=ModelSelect2MultipleWidget(
                queryset=User.objects.all(),
                search_fields=['username__icontains']
            ),
            queryset=User.objects.all(), required=False)
        self.fields['members'] = forms.ModelMultipleChoiceField(
            widget=ModelSelect2MultipleWidget(
                queryset=User.objects.all(),
                search_fields=['username__icontains']
            ),
            queryset=User.objects.all(), required=False)

        self.fields['language'] = forms.ModelChoiceField(
            widget=ModelSelect2Widget(
                queryset=Language.objects.all(),
                search_fields=['name__icontains'],
            ),
            queryset=Language.objects.all()
        )


        self.fields['goal'].label = _('Goal')

        self.fields['idea'].label = _('Idea')

        self.fields['members'].label = _('Members')
        self.fields['sharewith'].label = _('Share with:')

        self.fields['name'].label = _('<b>Name:</b> (e.g., "Solar Water Project".)')
        self.fields['name'].widget.attrs.update({'placeholder': ""})
        self.fields['situation'].label = _('<b>Situation:</b> (Describe your current situation by listing the things that you have, including access.)')
        self.fields['situation'].widget.attrs.update({'placeholder': _("Example:\n\nWe are two people in a desert. We have:\n- Computer\n- Internet connection\n- Access to postal services\n- Access to 3D printing services 200 kilos away\n - A car\n - 150 USD for this project")})
        self.fields['deliverable'].label = _('<b>Deliverable:</b> (Describe what do you expect to get.)')
        self.fields['deliverable'].widget.attrs.update({'placeholder': _("Example:\n\nA working prototype of solar water condenser, and high quality open designs published on GitHub, so others could easily replicate.")})
        self.fields['personal'].label = _('<b>Personal</b> (makes the entry visible only to a chosen set of people)')
        self.fields['language'].label = _('<b>Input Language</b> (the language you used to compose this post) ')
        self.fields['is_link'].label = _('<b>This is a link</b> (check if you are only linking to existing content)')
        self.fields['url'].label = _('<b>Origin:</b> (of the source)')
        self.fields['url'].widget.attrs.update({'placeholder': _('http://')})
        self.fields['is_historical'].label = _('<b>This is a history</b> (check if you are documenting a project of the past)')
       #self.fields['plain_equity'].label = _('Plain equity')
        self.initial['personal'] = True

        if idea_instance:
            self.initial['sharewith'] = idea_instance.sharewith.all
            self.initial['personal'] = idea_instance.personal

        try:
            language = Language.objects.get(language_code=request.LANGUAGE_CODE)
            self.initial['language'] = language
        except Language.DoesNotExist:
            pass

    class Meta:
        model = Plan
        exclude = [
            'user',
        ]
        fields = [
            'is_link',
            'url',
            'is_historical',
            'goal',
            'idea',
            'name',
            'situation',
            'deliverable',
            'name',
            'members',
            'language',
            'personal',
            'sharewith'
        ]
        widgets = {
            'situation': MarkdownWidget,
            'deliverable': MarkdownWidget,
        }
