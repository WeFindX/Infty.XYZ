import django_filters

from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from crispy_forms.layout import Field
from crispy_forms.layout import HTML
from crispy_forms.bootstrap import StrictButton
from crispy_forms.bootstrap import FieldWithButtons
from django.contrib.auth import get_user_model

from django import forms

from .models import Comment
from .models import Goal
from .models import Work
from .models import Idea
from .models import Step
from .models import Task
from .models import Definition
from .models import Type
from .models import Plan

User = get_user_model()


class CommentListViewFilter1(django_filters.FilterSet):
    @property
    def form(self):
        form = super(CommentListViewFilter1, self).form
        form.helper = FormHelper()
        form.helper.form_method = 'get'
        form.helper.form_class = 'form-inline'
        form.helper.field_template = 'bootstrap3/layout/inline_field.html'
        form.helper.add_input(Submit('submit', 'Search'))

        return form

    class Meta:
        model = Comment

        fields = [
        ]

        exclude = []


class CommentListViewFilter2(django_filters.FilterSet):
    text = django_filters.CharFilter(lookup_type="icontains")

    @property
    def form(self):
        form = super(CommentListViewFilter2, self).form
        form.helper = FormHelper()
        form.helper.form_method = 'get'
        form.helper.form_class = 'form-inline'
        form.helper.field_template = 'bootstrap3/layout/inline_field.html'
        form.helper.add_input(Submit('submit', 'Search'))

        return form

    class Meta:
        model = Comment

        fields = [u'text']

        exclude = []


class GoalListViewFilter1(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type="icontains")
    reason = django_filters.CharFilter(lookup_type="icontains")

    @property
    def form(self):
        form = super(GoalListViewFilter1, self).form
        form.helper = FormHelper()
        form.helper.form_method = 'get'
        form.helper.form_class = 'form-inline'
        form.helper.field_template = 'bootstrap3/layout/inline_field.html'
        form.helper.add_input(Submit('submit', 'Search'))

        return form

    class Meta:
        model = Goal

        fields = [u'reason', u'name',]

        exclude = []


class GoalListViewFilter2(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type="icontains")

    @property
    def form(self):
        form = super(GoalListViewFilter2, self).form
        form.helper = FormHelper()
        form.helper.form_method = 'get'
        form.helper.form_class = 'form-inline'
        form.helper.field_template = 'bootstrap3/layout/inline_field.html'
        form.helper.add_input(Submit('submit', 'Search'))

        return form

    class Meta:
        model = Goal

        fields = ['name']

        exclude = []


class WorkListViewFilter1(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type="icontains")
    description = django_filters.CharFilter(lookup_type="icontains")

    @property
    def form(self):
        form = super(WorkListViewFilter1, self).form
        form.helper = FormHelper()
        form.helper.form_method = 'get'
        form.helper.form_class = 'form-inline'
        form.helper.field_template = 'bootstrap3/layout/inline_field.html'
        form.helper.add_input(Submit('submit', 'Search'))

        return form

    class Meta:
        model = Work

        fields = [u'name', u'description', u'url', u'parent_work_id',]

        exclude = []


class WorkListViewFilter2(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type="icontains")

    @property
    def form(self):
        form = super(WorkListViewFilter2, self).form
        form.helper = FormHelper()
        form.helper.form_method = 'get'
        form.helper.form_class = 'form-inline'
        form.helper.field_template = 'bootstrap3/layout/inline_field.html'
        form.helper.add_input(Submit('submit', 'Search'))

        return form

    class Meta:
        model = Work

        fields = ['name']

        exclude = []


class IdeaListViewFilter1(django_filters.FilterSet):
    description = django_filters.CharFilter(lookup_type="icontains")
    name = django_filters.CharFilter(lookup_type="icontains")
    summary = django_filters.CharFilter(lookup_type="icontains")

    @property
    def form(self):
        form = super(IdeaListViewFilter1, self).form
        form.helper = FormHelper()
        form.helper.form_method = 'get'
        form.helper.form_class = 'form-inline'
        form.helper.field_template = 'bootstrap3/layout/inline_field.html'
        form.helper.add_input(Submit('submit', 'Search'))

        return form

    class Meta:
        model = Idea

        fields = [u'name', u'summary', u'description', ]

        exclude = []


class IdeaListViewFilter2(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type="icontains")

    @property
    def form(self):
        form = super(IdeaListViewFilter2, self).form
        form.helper = FormHelper()
        form.helper.form_method = 'get'
        form.helper.form_class = 'form-inline'
        form.helper.field_template = 'bootstrap3/layout/inline_field.html'
        form.helper.add_input(Submit('submit', 'Search'))

        return form

    class Meta:
        model = Idea

        fields = ['name']


class StepListViewFilter1(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type="icontains")
    deliverables = django_filters.CharFilter(lookup_type="icontains")
    objective = django_filters.CharFilter(lookup_type="icontains")
    investables = django_filters.CharFilter(lookup_type="icontains")

    @property
    def form(self):
        form = super(StepListViewFilter1, self).form
        form.helper = FormHelper()
        form.helper.form_method = 'get'
        form.helper.form_class = 'form-inline'
        form.helper.field_template = 'bootstrap3/layout/inline_field.html'
        form.helper.add_input(Submit('submit', 'Search'))

        return form

    class Meta:
        model = Step

        fields = [
            u'name',
            u'objective',
            u'deliverables',
            u'investables',
            u'priority',
        ]

        exclude = []


class StepListViewFilter2(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type="icontains")

    @property
    def form(self):
        form = super(StepListViewFilter2, self).form
        form.helper = FormHelper()
        form.helper.form_method = 'get'
        form.helper.form_class = 'form-inline'
        form.helper.field_template = 'bootstrap3/layout/inline_field.html'
        form.helper.add_input(Submit('submit', 'Search'))

        return form

    class Meta:
        model = Step

        fields = ['name']


class TaskListViewFilter1(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type="icontains")

    @property
    def form(self):
        form = super(TaskListViewFilter1, self).form
        form.helper = FormHelper()
        form.helper.form_method = 'get'
        form.helper.form_class = 'form-inline'
        form.helper.field_template = 'bootstrap3/layout/inline_field.html'
        form.helper.add_input(Submit('submit', 'Search'))

        return form

    class Meta:
        model = Task

        fields = [u'name', u'priority',]

        exclude = []


class TaskListViewFilter2(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type="icontains")

    @property
    def form(self):
        form = super(TaskListViewFilter2, self).form
        form.helper = FormHelper()
        form.helper.form_method = 'get'
        form.helper.form_class = 'form-inline'
        form.helper.field_template = 'bootstrap3/layout/inline_field.html'
        form.helper.add_input(Submit('submit', 'Search'))

        return form

    class Meta:
        model = Task

        fields = ['name']

        exclude = []


class DefinitionLimitChoiceFilter(django_filters.Filter):
    field_class = forms.ChoiceField

    def filter(self, qs, value):
        if value:
            values = qs.values_list('pk')[:value]
            qs = qs.filter(pk__in=values)
            return qs
        values = qs.values_list('pk')[:100]
        qs = qs.filter(pk__in=values)
        return qs


class DefinitionListViewFilter(django_filters.FilterSet):
    OBJECTS_LIMITS = (
        (-1, 'ALL'),
        (100, '100'),
        (1000, '1000'),
        (10000, '10000'),
    )
    name = django_filters.CharFilter(lookup_type="icontains")
    number_of_definitions = DefinitionLimitChoiceFilter(choices=OBJECTS_LIMITS)

    @property
    def form(self):
        form = super(DefinitionListViewFilter, self).form
        form.helper = FormHelper()
        form.helper.form_method = 'get'
        form.helper.form_class = 'form-inline'
        form.helper.field_template = 'bootstrap3/layout/inline_field.html'
        form.helper.layout = Layout(
            FieldWithButtons(Field('name'), Submit('submit', 'Search', css_class='button white')),
            Field('number_of_definitions'),
        )

        return form

    class Meta:
        model = Definition

        fields = ['name']

        exclude = []


class PlanListViewFilter1(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type="icontains")
    deliverable = django_filters.CharFilter(lookup_type="icontains")
    situation = django_filters.CharFilter(lookup_type="icontains")

    @property
    def form(self):
        form = super(PlanListViewFilter1, self).form
        form.helper = FormHelper()
        form.helper.form_method = 'get'
        form.helper.form_class = 'form-inline'
        form.helper.field_template = 'bootstrap3/layout/inline_field.html'
        form.helper.add_input(Submit('submit', 'Search'))

        return form

    class Meta:
        model = Plan

        fields = [u'name', u'name', u'deliverable', u'situation', ]

        exclude = []


class PlanListViewFilter2(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type="icontains")

    @property
    def form(self):
        form = super(PlanListViewFilter2, self).form
        form.helper = FormHelper()
        form.helper.form_method = 'get'
        form.helper.form_class = 'form-inline'
        form.helper.field_template = 'bootstrap3/layout/inline_field.html'
        form.helper.add_input(Submit('submit', 'Search'))

        return form

    class Meta:
        model = Plan

        fields = ['name']

        exclude = []

