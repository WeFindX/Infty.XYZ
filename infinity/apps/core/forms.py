from django.utils.translation import ugettext_lazy as _
from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Div
from django_select2.widgets import AutoHeavySelect2Widget
from django_select2.widgets import AutoHeavySelect2MultipleWidget
from django_select2.fields import AutoModelSelect2Field


from core.models import Comment
from core.models import Type
from core.models import Goal
from core.models import Work
from core.models import Idea
from core.models import Step
from core.models import Task
from core.models import Need
from core.models import Plan
from core.models import Language
from .fields import NeedChoiceField
from .fields import TypeChoiceField
from .fields import GoalChoiceField
from .fields import GoalChoiceFieldMultiple
from .fields import IdeaChoiceField
from .fields import MembersChoiceField

import django_select2
from django.contrib.contenttypes.models import ContentType

from django_markdown.widgets import MarkdownWidget

from decimal import Decimal
from core.models import Translation


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

        self.fields['language'] = django_select2.ModelSelect2Field(
            queryset=Language.objects.all().exclude(id__in=[
                translation.language.id for translation in translations
            ])
        )
        self.helper.layout.append(Submit('save', _('Create')))

    class Meta:
        model = Translation
        exclude = ['content_type', 'object_id', 'content_object']


class TranslationUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        #content_type_instance = kwargs.pop('content_type_instance')
        super(TranslationUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout.append(Submit('save', _('Update')))

    class Meta:
        model = Translation
        exclude = ['language', ]


class CommentCreateFormDetail(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CommentCreateFormDetail, self).__init__(*args, **kwargs)

        self.fields['text'].label = _("""<b>Comment</b> (to claim hours, just
                                      enclose a number within curly braces, e.g.,
                                      {1.5} h. You can do it multiple times in
                                      one comment, and use {?1.5} to indicate
                                      estimates.""")
        self.fields['notify'].label = _('Notify mentioned users (e.g., <i>Hi [User], how are you?</i>) by e-mail.')
        self.helper = FormHelper(self)

        self.helper.layout.append(Submit('save', _('Create')))

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
        self.fields['sharewith'] = MembersChoiceField(
            widget=AutoHeavySelect2MultipleWidget(
                select2_options={
                    'minimumInputLength': 1,
                    'placeholder': unicode(_('Select the users to share with:')),
                }
            ), required=False
        )

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


class CommentCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CommentCreateForm, self).__init__(*args, **kwargs)
        self.fields['text'].label = _('Comment')
        self.fields['notify'].label = _('Notify mentioned users by e-mail.')

        self.helper = FormHelper(self)

        self.helper.layout.append(Submit('save', _('Create')))

    class Meta:
        model = Comment
        exclude = [
            'created_at',
            'updated_at',
            'user',
        ]
        widgets = {
            'text': MarkdownWidget,
        }


class GoalCreateForm(forms.ModelForm):

    type = TypeChoiceField(
        queryset=Type.objects.all(),
        widget=AutoHeavySelect2Widget(
            select2_options={
                'minimumInputLength': 0,
                'placeholder': unicode(_('Select the type of your need...')),
            }
        ),
        required=False
    )

    reason = forms.CharField(widget=MarkdownWidget())

    hyper_equity = forms.ChoiceField(choices=[(Decimal(x*0.0001), '%.2f' % (x*0.01)+ '%') for x in range(1,11)])

    def __init__(self, *args, **kwargs):
        need_instance = kwargs.pop('need_instance')
        super(GoalCreateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        self.helper.layout.append(Submit('save', _('Create')))

        if need_instance:
            self.initial['need'] = need_instance
            self.initial['type'] = need_instance.type

        self.fields['need'] = NeedChoiceField(
            widget=AutoHeavySelect2Widget(
                select2_options={
                    'minimumInputLength': 1,
                    'placeholder': unicode(_('Select the thing that you need...')),
                    'ajax': {
                        'dataType': 'json',
                        'quietMillis': 100,
                        'data': '*START*django_select2.runInContextHelper(s2_endpoints_param_gen, selector)*END*',
                        'results': '*START*django_select2.runInContextHelper(django_select2.process_results, selector)*END*',
                    },
                }
            )
        )

        self.fields['sharewith'] = MembersChoiceField(
            widget=AutoHeavySelect2MultipleWidget(
                select2_options={
                    'minimumInputLength': 1,
                    'placeholder': unicode(_('Select the users to share with:')),
                }
            ), required=False,
            label=_('Share with:')
        )

        self.fields['need'].label = _("""<b>Topic:</b> (relevant to problem,
                                      <a href="/need-create/">click here</a> to
                                      add if you can't find it.)""")
        self.fields['type'].label = _("<b>Category:</b> (of the problem)")
        self.fields['name'].label = _("""<b>Title:</b> (e.g., Potable Water
                                      Shortage, <a href="/goal/list/">check</a> if the problem is not
                                      defined yet.)""")
        self.fields['name'].widget.attrs.update({'placeholder': _('')})
        self.fields['reason'].label = _('<b>Description:</b> (e.g., Many people in the world lack clean potable water.)')
        self.fields['reason'].widget.attrs.update({'placeholder': \
        _('')})
        self.fields['personal'].label = _('<b>Personal</b> (makes the entry visible only to a chosen set of people)')
        self.fields['language'].label = _('<b>Input Language</b> (the language you used to compose this post) ')
        self.fields['hyper_equity'].label = _('Hyper equity')
        self.initial['language'] = 85 # English


    class Meta:
        model = Goal
        exclude = [
            'user',
        ]
        fields = [
            'type',
            'need',
            'name',
            'reason',
            'hyper_equity',
            'language',
            'personal',
            'sharewith',
        ]


class GoalUpdateForm(forms.ModelForm):

    hyper_equity = forms.ChoiceField(choices=[(Decimal(x*0.0001), '%.2f' % (x*0.01)+ '%') for x in range(1,11)])

    def __init__(self, *args, **kwargs):
        super(GoalUpdateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        self.helper.layout.append(Submit('save', _('Update')))

        self.fields['name'].label = 'Description'
        self.fields['sharewith'] = MembersChoiceField(
            widget=AutoHeavySelect2MultipleWidget(
                select2_options={
                    'minimumInputLength': 1,
                    'placeholder': unicode(_('Select the users to share with:')),
                }
            ), required=False
        )

        self.fields['language'].label = _('<b>Input Language</b> (the language you used to compose this post) ')
        self.fields['hyper_equity'].label = _('Hyper equity')

    class Meta:
        model = Goal
        exclude = [
            'created_at',
            'user',
        ]
        fields = [
            'type',
            'name',
            'hyper_equity',
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
        self.fields['sharewith'] = MembersChoiceField(
            widget=AutoHeavySelect2MultipleWidget(
                select2_options={
                    'minimumInputLength': 1,
                    'placeholder': unicode(_('Select the users to share with:')),
                }
            ), required=False
        )

        self.fields['language'].label = _('<b>Input Language</b> (the language you used to compose this post) ')

    class Meta:
        model = Work
        exclude = [
            'created_at',
            'user',
        ]
        fields = [
            'name',
            'file',
            'description',
            'url',
            'parent_work_id',
            'task',
            'language',
            'personal',
            'sharewith',
        ]
        widgets = {
            'description': MarkdownWidget,
        }


class WorkCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(WorkCreateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        self.helper.layout.append(Submit('save', _('Create')))
        self.fields['sharewith'] = MembersChoiceField(
            widget=AutoHeavySelect2MultipleWidget(
                select2_options={
                    'minimumInputLength': 1,
                    'placeholder': unicode(_('Select the users to share with:')),
                }
            ), required=False
        )

        self.fields['name'].label = _('<b>Name:</b> (e.g., "First attempt to assemble solar cells.", used in title.)')
        self.fields['name'].widget.attrs.update({'placeholder': _('Give a title to your work.')})
        self.fields['description'].label = _('<b>Description:</b> (details about the work, used as body.)')
        self.fields['description'].widget.attrs.update({'placeholder': _('Here is a little story of my work.')})
        self.fields['url'].label = _('<b>Link:</b> (you can give external link to your work description)')
        self.fields['url'].widget.attrs.update({'placeholder': _('http://')})
        self.fields['file'].label = _('<b>File:</b> (you can upload a file describing your work)')
        self.fields['file'].widget.attrs.update({'placeholder': _('http://')})
        self.fields['parent_work_id'].label = _('<b>Parent Work Id:</b> (integer referring to other work)')
        self.fields['parent_work_id'].widget.attrs.update({'placeholder': _('optional')})
        self.fields['personal'].label = _('<b>Personal</b> (makes the entry visible only to a chosen set of people)')
        self.fields['language'].label = _('<b>Input Language</b> (the language you used to compose this post) ')
        self.initial['language'] = 85 # English

    class Meta:
        model = Work
        exclude = [
            'task',
            'user',
        ]
        fields = [
            'name',
            'description',
            'url',
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

    super_equity = forms.ChoiceField(
        choices=[(Decimal(x*0.01), '%.0f' % (x*1.)+ '%') for x in range(1,11)]
    )

    def __init__(self, *args, **kwargs):
        super(IdeaUpdateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.fields['sharewith'] = MembersChoiceField(
            widget=AutoHeavySelect2MultipleWidget(
                select2_options={
                    'minimumInputLength': 1,
                    'placeholder': unicode(_('Select the users to share with:')),
                }
            ), required=False
        )

        self.helper.layout.append(Submit('save', _('Update')))

        self.fields['language'].label = _('<b>Input Language</b> (the language you used to compose this post) ')

    class Meta:
        model = Idea
        exclude = [
            'created_at',
            'user',
        ]
        fields = [
            'name',
            'summary',
            'description',
            'goal',
            'super_equity',
            'language',
            'personal',
            'sharewith',
        ]
        widgets = {
            'description': MarkdownWidget,
        }


class IdeaCreateForm(forms.ModelForm):

    goal = GoalChoiceFieldMultiple()

    super_equity = forms.ChoiceField(
        choices=[(Decimal(x*0.01), '%.0f' % (x*1.)+ '%') for x in range(1,11)]
    )

    def __init__(self, *args, **kwargs):
        goal_instance = kwargs.pop('goal_instance')

        super(IdeaCreateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        self.helper.layout.append(Submit('save', _('Create')))

        if goal_instance:
            self.initial['goal'] = [goal_instance, ]

        self.fields['goal'] = GoalChoiceFieldMultiple(
            widget=AutoHeavySelect2MultipleWidget(
                select2_options={
                    'minimumInputLength': 0,
                    'placeholder': 'Select a goal',
                    'ajax': {
                        'dataType': 'json',
                        'quietMillis': 100,
                        'data': '*START*django_select2.runInContextHelper(s2_endpoints_param_gen_for_goal, selector)*END*',
                        'results': '*START*django_select2.runInContextHelper(django_select2.process_results, selector)*END*',
                    },
                }
            )
        )
        self.fields['sharewith'] = MembersChoiceField(
            widget=AutoHeavySelect2MultipleWidget(
                select2_options={
                    'minimumInputLength': 1,
                    'placeholder': unicode(_('Select the users to share with:')),
                }
            ), required=False
        )


        self.fields['name'].label = _('<b>Name:</b> (e.g., "Solar Water Condenser", used in title.)')
        self.fields['summary'].label = _('<b>Summary:</b> (e.g., "Use solar panels and Peltier effect to extract water from air.", appears as subtitle.)')
        self.fields['description'].label = _('<b>Description:</b> (write full description here, used as body.)')
        self.fields['personal'].label = _('<b>Personal</b> (makes the entry visible only to a chosen set of people)')
        self.fields['language'].label = _('<b>Input Language</b> (the language you used to compose this post) ')
        self.initial['language'] = 85 # English

    class Meta:
        model = Idea
        exclude = [
            'created_at',
            'user',
        ]
        fields = [
            'goal',
            'name',
            'summary',
            'description',
            'super_equity',
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
        self.fields['sharewith'] = MembersChoiceField(
            widget=AutoHeavySelect2MultipleWidget(
                select2_options={
                    'minimumInputLength': 1,
                    'placeholder': unicode(_('Select the users to share with:')),
                }
            ), required=False
        )

        self.fields['language'].label = _('<b>Input Language</b> (the language you used to compose this post) ')

    class Meta:
        model = Step
        exclude = [
            'created_at',
            'updated_at',
            'user',
        ]
        fields = [
            'name',
            'objective',
            'priority',
            'investables',
            'deliverables',
            'plan',
            'language',
            'personal',
            'sharewith',
        ]
        widgets = {
            'objective': MarkdownWidget,
        }


class StepCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(StepCreateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        self.helper.layout.append(Submit('save', _('Create')))
        self.fields['sharewith'] = MembersChoiceField(
            widget=AutoHeavySelect2MultipleWidget(
                select2_options={
                    'minimumInputLength': 1,
                    'placeholder': unicode(_('Select the users to share with:')),
                }
            ), required=False
        )

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
        self.initial['language'] = 85 # English

    class Meta:
        model = Step
        exclude = [
            'plan',
            'updated_at',
            'created_at',
            'user',
        ]
        fields = [
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
        self.fields['sharewith'] = MembersChoiceField(
            widget=AutoHeavySelect2MultipleWidget(
                select2_options={
                    'minimumInputLength': 1,
                    'placeholder': unicode(_('Select the users to share with:')),
                }
            ), required=False
        )

        self.fields['language'].label = _('<b>Input Language</b> (the language you used to compose this post) ')

    class Meta:
        model = Task
        exclude = [
            'created_at',
            'updated_at',
            'user',
        ]
        fields = [
            'name',
            'priority',
            'step',
            'language',
            'personal',
            'sharewith',
        ]


class TaskCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(TaskCreateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        self.helper.layout.append(Submit('save', _('Create')))
        self.fields['sharewith'] = MembersChoiceField(
            widget=AutoHeavySelect2MultipleWidget(
                select2_options={
                    'minimumInputLength': 1,
                    'placeholder': unicode(_('Select the users to share with:')),
                }
            ), required=False
        )

        self.fields['name'].label = _('<b>Task:</b> (e.g., "Purchase solar cells", text in title.)')
        self.fields['name'].widget.attrs.update({'placeholder': _('Type the name of the task.')})
        self.fields['priority'].label = _("<b>Priority:</b> (integer, e.g., 1,2,3.. - used for ordering, smaller number means the task has to be done earlier)")
        self.fields['language'].label = _('<b>Input Language</b> (the language you used to compose this post) ')
        self.initial['language'] = 85 # English

    class Meta:
        model = Task
        exclude = [
            'step',
            'created_at',
            'updated_at',
            'user',
        ]
        fields = [
            'name',
            'priority',
            'language',
            'personal',
            'sharewith',
        ]


class NeedCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NeedCreateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.fields['sharewith'] = MembersChoiceField(
            widget=AutoHeavySelect2MultipleWidget(
                select2_options={
                    'minimumInputLength': 1,
                    'placeholder': unicode(_('Select the users to share with:')),
                }
            ), required=False
        )

        self.helper.layout = Layout(
            Div(
                Div('language', css_class='col-sm-2',),
                Div(
                    Field('name', placeholder=kwargs.pop('query_placeholder',
                                                         "expression, e.g., 'interstellar spaceflight', 'water quality on Earth'")),
                    css_class='col-sm-10',
                ),
                css_class='row'
            ),
            Div(
                Div(
                    Div(
                        Field(
                            'definition', placeholder=kwargs.pop('query_placeholder', "definition, e.g., 'spaceflight to other star systems', 'water suitability for life on Earth'"),
                            # type="hidden",
                        ),
                        css_class='col-sm-10',
                    ),
                    Div(
                        Field(Submit('submit', _('Add & Go'))),
                        # css_class='col-sm-2 hidden create-button',
                        css_class='col-sm-2 create-button',
                    ),
                    css_class='col-sm-12 hints-block',
                ),
                css_class='row'
            ),
        )
        self.fields['name'].label = ''
        self.fields['language'].label = ''
        self.fields['definition'].label = ''

    class Meta:
        model = Need
        fields = [
            'name',
            'language',
            'definition',
            'sharewith',
        ]


class NeedUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NeedUpdateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        self.helper.layout.append(Submit('save', _('Update')))

    class Meta:
        model = Need
        fields = [
            'name',
            'language',
            'definition',
            'sharewith',
        ]


class PlanUpdateForm(forms.ModelForm):

    plain_equity = forms.ChoiceField(
        choices=[(Decimal(x*.1), '%.0f' % (x*10.)+ '%') for x in range(1,11)]
    )

    def __init__(self, *args, **kwargs):
        super(PlanUpdateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        self.fields['members'] = MembersChoiceField(
            widget=AutoHeavySelect2MultipleWidget(
                select2_options={
                    'minimumInputLength': 1,
                    'placeholder': 'Select the members for the equity...',
                }
            )
        )
        self.fields['sharewith'] = MembersChoiceField(
            widget=AutoHeavySelect2MultipleWidget(
                select2_options={
                    'minimumInputLength': 1,
                    'placeholder': unicode(_('Select the users to share with:')),
                }
            ), required=False
        )

        self.helper.layout.append(Submit('save', _('Update')))
        self.fields['language'].label = _('<b>Input Language</b> (the language you used to compose this post) ')


    class Meta:
        model = Plan
        exclude = [
            'created_at',
            'updated_at',
            'user',
        ]
        fields = [
            'name',
            'situation',
            'deliverable',
            'plain_equity',
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

    goal = GoalChoiceField()

    plain_equity = forms.ChoiceField(
        choices=[(Decimal(x*.1), '%.0f' % (x*10.)+ '%') for x in range(1,11)]
    )

    def __init__(self, *args, **kwargs):
        idea_instance = kwargs.pop('idea_instance')
        super(PlanCreateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.fields['sharewith'] = MembersChoiceField(
            widget=AutoHeavySelect2MultipleWidget(
                select2_options={
                    'minimumInputLength': 1,
                    'placeholder': unicode(_('Select the users to share with:')),
                }
            ), required=False
        )

        self.helper.layout.append(Submit('save', _('Create')))

        if idea_instance:
            self.initial['idea'] = idea_instance
            self.initial['goal'] = idea_instance.goal.first()

        self.fields['goal'] = GoalChoiceField(
            widget=AutoHeavySelect2Widget(
                select2_options={
                    'minimumInputLength': 0,
                    'placeholder': 'Select goal',
                    'ajax': {
                        'dataType': 'json',
                        'quietMillis': 100,
                        'data': '*START*django_select2.runInContextHelper(s2_endpoints_param_gen_for_goal, selector)*END*',
                        'results': '*START*django_select2.runInContextHelper(django_select2.process_results, selector)*END*',
                    },
                }
            )
        )


        self.fields['idea'] = IdeaChoiceField(
            widget=AutoHeavySelect2Widget(
                select2_options={
                    'minimumInputLength': 0,
                    'placeholder': 'Select idea',
                    'ajax': {
                        'dataType': 'json',
                        'quietMillis': 100,
                        'data': '*START*django_select2.runInContextHelper(s2_endpoints_param_gen_for_idea, selector)*END*',
                        'results': '*START*django_select2.runInContextHelper(django_select2.process_results, selector)*END*',
                    },
                }
            )
        )

        self.fields['members'] = MembersChoiceField(
            widget=AutoHeavySelect2MultipleWidget(
                select2_options={
                    'minimumInputLength': 1,
                    'placeholder': 'Select the members for the equity...',
                }
            )
        )

        self.fields['name'].label = _('<b>Means:</b> (e.g., "computer-aided design software, good CAD skills, electric soldering iron, glue, aluminium solder", used in title.)')
        self.fields['name'].widget.attrs.update({'placeholder': _("Main tools and/or methods you will use, comma-separated.")})
        self.fields['situation'].label = _('<b>Situation:</b> (Describe your current situation by listing the things that you have, including access.)')
        self.fields['situation'].widget.attrs.update({'placeholder': _("Example:\n\nWe are two people in a desert. We have:\n- Computer\n- Internet connection\n- Access to postal services\n- Access to 3D printing services 200 kilos away\n - A car\n - 150 USD for this project")})
        self.fields['deliverable'].label = _('<b>Deliverable:</b> (Describe what do you expect to get.)')
        self.fields['deliverable'].widget.attrs.update({'placeholder': _("Example:\n\nA working prototype of solar water condenser, and high quality open designs published on GitHub, so others could easily replicate.")})
        self.fields['personal'].label = _('<b>Personal</b> (makes the entry visible only to a chosen set of people)')
        self.fields['language'].label = _('<b>Input Language</b> (the language you used to compose this post) ')
        self.initial['language'] = 85 # English

    class Meta:
        model = Plan
        exclude = [
            'user',
        ]
        fields = [
            'goal',
            'idea',
            'name',
            'situation',
            'deliverable',
            'name',
            'plain_equity',
            'members',
            'language',
            'personal',
            'sharewith'
        ]
        widgets = {
            'situation': MarkdownWidget,
            'deliverable': MarkdownWidget,
        }


