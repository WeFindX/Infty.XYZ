import django_filters
import django_select2

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from crispy_forms.layout import Field
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


class CommentChoiceField(django_select2.AutoModelSelect2Field):
    queryset = Comment.objects.all()
    search_fields = ['text__icontains', ]


class GoalChoiceField(django_select2.AutoModelSelect2Field):
    queryset = Goal.objects.all()
    search_fields = ['name__icontains', 'reason__icontains', ]


class WorkChoiceField(django_select2.AutoModelSelect2Field):
    queryset = Work.objects.all()
    search_fields = ['name__icontains', 'description__icontains']


class IdeaChoiceField(django_select2.AutoModelSelect2Field):
    queryset = Idea.objects.all()
    search_fields = [
        'description__icontains',
        'name__icontains',
        'summary__icontains',
    ]


class StepChoiceField(django_select2.AutoModelSelect2Field):
    queryset = Step.objects.all()
    search_fields = [
        'name__icontains',
        'deliverables__icontains',
        'objective__icontains',
        'investables__icontains']


class TaskChoiceField(django_select2.AutoModelSelect2Field):
    queryset = Task.objects.all()
    search_fields = ['name__icontains', ]


class UserChoiceField(django_select2.AutoModelSelect2Field):
    queryset = User.objects.all()
    search_fields = ['introduction__icontains', ]


class DefinitionChoiceField(django_select2.AutoModelSelect2Field):
    queryset = Definition.objects.all()
    search_fields = ['name__icontains']


class TypeChoiceField(django_select2.AutoModelSelect2Field):
    queryset = Type.objects.all()
    search_fields = ['name__icontains']


class PlanChoiceField(django_select2.AutoModelSelect2Field):
    queryset = Plan.objects.all()
    search_fields = [
        'name__icontains',
        'deliverable__icontains',
        'situation__icontains']


class CommentChoiceFilter(django_filters.Filter):
    field_class = CommentChoiceField


class GoalChoiceFilter(django_filters.Filter):
    field_class = GoalChoiceField


class WorkChoiceFilter(django_filters.Filter):
    field_class = WorkChoiceField


class IdeaChoiceFilter(django_filters.Filter):
    field_class = IdeaChoiceField


class StepChoiceFilter(django_filters.Filter):
    field_class = StepChoiceField


class TaskChoiceFilter(django_filters.Filter):
    field_class = TaskChoiceField


class UserChoiceFilter(django_filters.Filter):
    field_class = UserChoiceField


class DefinitionChoiceFilter(django_filters.Filter):
    field_class = DefinitionChoiceField


class TypeChoiceFilter(django_filters.Filter):
    field_class = TypeChoiceField


class PlanChoiceFilter(django_filters.Filter):
    field_class = PlanChoiceField


class CommentListViewFilter1(django_filters.FilterSet):
    task = TaskChoiceFilter(
        widget=django_select2.AutoHeavySelect2Widget(
            select2_options={
                'placeholder': 'Task'}))
    goal = GoalChoiceFilter(
        widget=django_select2.AutoHeavySelect2Widget(
            select2_options={
                'placeholder': 'Goal'}))
    text = django_filters.CharFilter(lookup_type="icontains")
    work = WorkChoiceFilter(
        widget=django_select2.AutoHeavySelect2Widget(
            select2_options={
                'placeholder': 'Work'}))
    idea = IdeaChoiceFilter(
        widget=django_select2.AutoHeavySelect2Widget(
            select2_options={
                'placeholder': 'Idea'}))
    step = StepChoiceFilter(
        widget=django_select2.AutoHeavySelect2Widget(
            select2_options={
                'placeholder': 'Step'}))
    plan = PlanChoiceFilter(
        widget=django_select2.AutoHeavySelect2Widget(
            select2_options={
                'placeholder': 'Plan'}))

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
            'goal',
            'text',
            'created_at',
            'updated_at',
            'idea',
            'plan',
            'step',
            'task',
            'work']

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

        fields = ['text']

        exclude = []


class GoalListViewFilter1(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type="icontains")
    reason = django_filters.CharFilter(lookup_type="icontains")
    user = UserChoiceFilter(
        widget=django_select2.AutoHeavySelect2Widget(
            select2_options={
                'placeholder': 'User'}))

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

        fields = ['reason', 'name', 'user']

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
    user = UserChoiceFilter(
        widget=django_select2.AutoHeavySelect2Widget(
            select2_options={
                'placeholder': 'User'}))
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

        fields = ['name', 'description', 'url', 'parent_work_id', 'user']

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
    user = UserChoiceFilter(
        widget=django_select2.AutoHeavySelect2Widget(
            select2_options={
                'placeholder': 'User'}))

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

        fields = ['name', 'summary', 'description', 'user']

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
    user = UserChoiceFilter(
        widget=django_select2.AutoHeavySelect2Widget(
            select2_options={
                'placeholder': 'User'}))
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
            'name',
            'objective',
            'deliverables',
            'investables',
            'priority',
            'user']

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
    user = UserChoiceFilter(
        widget=django_select2.AutoHeavySelect2Widget(
            select2_options={
                'placeholder': 'User'}))

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

        fields = ['name', 'priority', 'user']

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
    user = UserChoiceFilter(
        widget=django_select2.AutoHeavySelect2Widget(
            select2_options={
                'placeholder': 'User'}))
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

        fields = ['name', 'name', 'deliverable', 'situation', 'user']

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


# Have to call it clearly to help django_select2 register fields
CommentChoiceField()
GoalChoiceField()
WorkChoiceField()
IdeaChoiceField()
StepChoiceField()
TaskChoiceField()
UserChoiceField()
DefinitionChoiceField()
TypeChoiceField()
PlanChoiceField()
