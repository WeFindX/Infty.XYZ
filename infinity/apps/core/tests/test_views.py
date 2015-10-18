from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.utils import formats

from django_webtest import WebTest
from webtest import Upload
from model_mommy import mommy
from allauth.account.models import EmailAddress

from users.models import User
from core.models import Comment
from core.models import Goal
from core.models import Work
from core.models import Idea
from core.models import Step
from core.models import Task
from core.models import Need
from core.models import Type
from core.models import Plan


class AuthTestMixin(object):

    def init_users(self):
        # Create User object
        self.user, created = User.objects.get_or_create(
            username='asd', email='user@mail.com')
        self.user.set_password('test')
        self.user.save()
        # confirmation - sometimes it's required
        EmailAddress.objects.create(
            user=self.user,
            email='user@mail.com',
            primary=True,
            verified=True
        )

    def login(self, login, password):
        # TODO: need to fix this test
        # for languages
        resp = self.app.get(reverse('account_login'))
        form = resp.forms[0]
        form['login'] = login
        form['password'] = password
        form.submit()

    def logout(self):
        resp = self.app.get('/accounts/logout/')


class CommentTest(WebTest, AuthTestMixin):

    def test_list(self):
        """Create list of Comment in database,
        open list view and
        check that selected fields are visible
        for each object
        """
        self.init_users()
        self.login(self.user.email, 'test')

        comment_list = []
        goal = mommy.make('core.Goal')
        goal_type = ContentType.objects.get_for_model(Goal)
        goal_model = goal_type.model_class()
        comment = mommy.make(
            'core.Comment',
            content_type=goal_type,
            object_id=goal_model.objects.first().pk,
            user=self.user, _fill_optional=True
        )
        comment_list.append(comment)

        url = reverse('comment-list1')

        comment = mommy.make(
            'core.Comment',
            content_type=goal_type,
            object_id=goal_model.objects.first().pk,
            user=self.user, _fill_optional=True
        )
        comment_list.append(comment)

        resp = self.app.get(url)

        for comment in comment_list:
            self.assertContains(resp, comment.text)

    def test_udpate(self):
        """Update object using view
        Check database for updated object
        """
        self.init_users()
        self.login(self.user.email, 'test')

        goal = mommy.make('core.Goal')
        goal_type = ContentType.objects.get_for_model(Goal)
        goal_model = goal_type.model_class()
        comment = mommy.make(
            'core.Comment',
            content_type=goal_type,
            object_id=goal_model.objects.first().pk,
            user=self.user, _fill_optional=True
        )

        url = reverse('comment-update', kwargs={
            'slug': comment.pk, })

        comment_compare = mommy.make(
            'core.Comment',
            content_type=goal_type,
            object_id=goal_model.objects.first().pk,
            user=self.user, _fill_optional=True
        )

        resp = self.app.get(url)

        form = resp.form
        form['text'] = comment_compare.text
        form.submit()

        comment_updated = Comment.objects.get(pk=comment.pk)

        self.assertEqual(
            comment_compare.text,
            comment_updated.text
        )

    def test_delete(self):
        """Create Comment in database,
        open delete view and
        check that object was removed
        """
        self.init_users()
        self.login(self.user.email, 'test')

        goal = mommy.make('core.Goal')
        goal_type = ContentType.objects.get_for_model(Goal)
        goal_model = goal_type.model_class()
        comment = mommy.make(
            'core.Comment',
            content_type=goal_type,
            object_id=goal_model.objects.first().pk,
            user=self.user, _fill_optional=True
        )

        self.assertEqual(Comment.objects.count(), 1)
        url = reverse('comment-delete', args=(comment.pk,))

        resp = self.app.get(url)
        resp.form.submit()
        self.assertEqual(Comment.objects.count(), 0)

    def test_create(self):
        """Create Comment object using view
        Check database for created object
        """
        self.init_users()
        self.login(self.user.email, 'test')

        goal = mommy.make('core.Goal')
        goal_type = ContentType.objects.get_for_model(Goal)
        goal_model = goal_type.model_class()
        comment = mommy.make(
            'core.Comment',
            content_type=goal_type,
            object_id=goal_model.objects.first().pk,
            user=self.user, _fill_optional=True
        )


        url = reverse('comment-create', kwargs={
        })

        resp = self.app.get(url)

        form = resp.form
        form['text'] = comment.text
        form.submit()

        comment_created = Comment.objects.latest('id')

        self.assertEqual(
            comment_created.text,
            comment.text
        )


class GoalTest(WebTest, AuthTestMixin):

    def test_list(self):
        """Create list of Goal in database,
        open list view and
        check that selected fields are visible
        for each object
        """
        self.init_users()
        self.login(self.user.email, 'test')

        goal_list = []
        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, _fill_optional=True)
        goal = mommy.make('core.Goal', need=need, user=self.user, _fill_optional=True)
        goal_list.append(goal)

        url = reverse('goal-list')

        goal = mommy.make('core.Goal', need=need, user=self.user, _fill_optional=True)
        goal_list.append(goal)

        resp = self.app.get(url)

        for goal in goal_list:
            self.assertContains(resp, goal.name)

    def test_delete(self):
        """Create Goal in database,
        open delete view and
        check that object was removed
        """
        self.init_users()

        self.login(self.user.email, 'test')
        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, _fill_optional=True)
        goal = mommy.make('core.Goal', need=need, user=self.user, _fill_optional=True)
        self.assertEqual(Goal.objects.count(), 1)
        url = reverse('goal-delete', args=(goal.pk,))

        resp = self.app.get(url)
        resp.form.submit()
        self.assertEqual(Goal.objects.count(), 0)

    def test_udpate(self):
        """Update object using view
        Check database for updated object
        """
        self.init_users()

        self.login(self.user.email, 'test')
        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, _fill_optional=True)
        goal = mommy.make('core.Goal', need=need, user=self.user, _fill_optional=True)

        url = reverse('goal-update', kwargs={
            'slug': goal.pk, })

        goal_compare = mommy.make(
            'core.Goal',
            user=self.user,
            need=need,
            _fill_optional=True)

        resp = self.app.get(url)

        form = resp.form
        form['name'] = goal_compare.name
        form['personal'] = goal_compare.personal
        form['reason'] = goal_compare.reason
        form['sharewith'] = [self.user.id,]
        form.submit()

        goal_updated = Goal.objects.get(pk=goal.pk)

        self.assertEqual(
            goal_compare.name,
            goal_updated.name
        )
        self.assertEqual(
            goal_compare.personal,
            goal_updated.personal
        )
        self.assertEqual(
            goal_compare.reason,
            goal_updated.reason
        )

    def test_detail(self):
        """Create Goal in database,
        open detail view and
        check that selected fields are visible
        """
        self.init_users()

        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, _fill_optional=True)
        goal = mommy.make('core.Goal', need=need, personal=False, user=self.user, _fill_optional=True)

        url = reverse('goal-detail', args=(goal.pk,))

        resp = self.app.get(url)
        self.assertContains(resp, goal.name)

        #self.assertContains(resp, goal.personal)

        self.assertContains(resp, goal.reason)

        self.assertContains(resp, goal.user)

        self.assertContains(resp, goal.need)


    def test_create(self):
        """Create Goal object using view
        Check database for created object
        """
        self.init_users()

        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, _fill_optional=True)
        goal = mommy.make('core.Goal', need=need, user=self.user, _fill_optional=True)

        url = reverse('goal-create')

        # Access forbidden for AnonymousUser
        resp = self.app.get(url, status=302)

        self.login(self.user.email, 'test')

        resp = self.app.get(url)

        form = resp.form
        form['name'] = goal.name
        form['personal'] = goal.personal
        form['reason'] = goal.reason
        form['type'] = type.pk
        form['need'] = goal.need.pk
        form['sharewith'] = [self.user.id,]
        form.submit()

        goal_created = Goal.objects.latest('id')

        self.assertEqual(
            goal_created.name,
            goal.name
        )
        self.assertEqual(
            goal_created.personal,
            goal.personal
        )
        self.assertEqual(
            goal_created.reason,
            goal.reason
        )


class WorkTest(WebTest, AuthTestMixin):

    def test_list(self):
        """Create list of Work in database,
        open list view and
        check that selected fields are visible
        for each object
        """
        self.init_users()

        work_list = []
        work = mommy.make('core.Work', _fill_optional=True)
        work_list.append(work)

        url = reverse('work-list')

        resp = self.app.get(url)

        for work in work_list:
            self.assertContains(resp, work.task)
            self.assertContains(resp, work.name)
            self.assertContains(resp, work.url or "")
            pass
            pass
            self.assertContains(resp, work.user)
            self.assertContains(resp, work.file or "")
            self.assertContains(resp, work.parent_work_id or "")
            self.assertContains(resp, work.description)

        work.delete()

        self.logout()

    def test_udpate(self):
        """Update object using view
        Check database for updated object
        """
        self.init_users()
        self.login(self.user.email, 'test')

        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, _fill_optional=True)
        goal = mommy.make('core.Goal', need=need, user=self.user, _fill_optional=True)
        idea = mommy.make('core.Idea', goal=[goal, ], user=self.user, _fill_optional=True)
        plan = mommy.make('core.Plan', idea=idea, user=self.user, _fill_optional=True)
        step = mommy.make('core.Step', plan=plan, user=self.user, _fill_optional=True)
        task = mommy.make('core.Task', step=step, user=self.user, _fill_optional=True)
        work = mommy.make('core.Work', task=task, user=self.user, _fill_optional=True)

        url = reverse('work-update', kwargs={
            'slug': work.pk, })

        work_compare = mommy.make(
            'core.Work',
            user=self.user,
            task=task,
            _fill_optional=True)

        resp = self.app.get(url)

        form = resp.form
        form['task'] = work_compare.task.pk
        form['name'] = work_compare.name
        form['url'] = work_compare.url
        if work.file:
            form['file'] = Upload(work_compare.file.path)
        form['parent_work_id'] = str(work_compare.parent_work_id)
        form['description'] = work_compare.description
        form['personal'] = False
        form['sharewith'] = '1'
        form.submit()

        work_updated = Work.objects.get(pk=work.pk)

        self.assertEqual(
            work_compare.name,
            work_updated.name
        )
        self.assertEqual(
            work_compare.url,
            work_updated.url
        )
        if work.file:
            self.assertEqual(
                file(work_compare.file.path).read(),
                file(work_updated.file.path).read()
            )
        self.assertEqual(
            work_compare.parent_work_id,
            work_updated.parent_work_id
        )
        self.assertEqual(
            work_compare.description,
            work_updated.description
        )

    def test_create(self):
        """Create Work object using view
        Check database for created object
        """
        self.init_users()

        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, _fill_optional=True)
        goal = mommy.make('core.Goal', need=need, user=self.user, _fill_optional=True)
        idea = mommy.make('core.Idea', goal=[goal, ], user=self.user, _fill_optional=True)
        plan = mommy.make('core.Plan', idea=idea, user=self.user, _fill_optional=True)
        step = mommy.make('core.Step', plan=plan, user=self.user, _fill_optional=True)
        task = mommy.make('core.Task', step=step, user=self.user, _fill_optional=True)
        work = mommy.make('core.Work', task=task, user=self.user, _fill_optional=True)

        url = reverse('work-create', kwargs={
            'task': work.task.pk,
        })

        # Access forbidden for AnonymousUser
        resp = self.app.get(url, status=302)

        self.login(self.user.email, 'test')

        resp = self.app.get(url)

        form = resp.form
        form['name'] = work.name
        form['url'] = work.url
        form['file'] = work.file
        if work.file:
            form['file'] = Upload(work.file.path)
        form['parent_work_id'] = str(work.parent_work_id)
        form['description'] = work.description
        form['personal'] = work.personal
        form['sharewith'] = str(1)
        form.submit()

        work_created = Work.objects.latest('id')

        self.assertEqual(
            work_created.name,
            work.name
        )
        self.assertEqual(
            work_created.url,
            work.url
        )
        self.assertEqual(
            work_created.parent_work_id,
            work.parent_work_id
        )
        self.assertEqual(
            work_created.description,
            work.description
        )

    def test_delete(self):
        """Create Work in database,
        open delete view and
        check that object was removed
        """
        self.init_users()

        self.login(self.user.email, 'test')


        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, _fill_optional=True)
        goal = mommy.make('core.Goal', need=need, user=self.user, _fill_optional=True)
        idea = mommy.make('core.Idea', goal=[goal, ], user=self.user, _fill_optional=True)
        plan = mommy.make('core.Plan', idea=idea, user=self.user, _fill_optional=True)
        step = mommy.make('core.Step', plan=plan, user=self.user, _fill_optional=True)
        task = mommy.make('core.Task', step=step, user=self.user, _fill_optional=True)
        work = mommy.make('core.Work', task=task, user=self.user, _fill_optional=True)
        self.assertEqual(Work.objects.count(), 1)
        url = reverse('work-delete', args=(work.pk,))

        resp = self.app.get(url)
        resp.form.submit()
        self.assertEqual(Work.objects.count(), 0)

    def test_list(self):
        """Create list of Work in database,
        open list view and
        check that selected fields are visible
        for each object
        """
        self.init_users()

        self.login(self.user.email, 'test')

        work_list = []
        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, _fill_optional=True)
        goal = mommy.make('core.Goal', need=need, user=self.user, _fill_optional=True)
        idea = mommy.make('core.Idea', goal=[goal, ], user=self.user, _fill_optional=True)
        plan = mommy.make('core.Plan', idea=idea, user=self.user, _fill_optional=True)
        step = mommy.make('core.Step', plan=plan, user=self.user, _fill_optional=True)
        task = mommy.make('core.Task', step=step, user=self.user, _fill_optional=True)
        work = mommy.make('core.Work', task=task, user=self.user, _fill_optional=True)
        work_list.append(work)

        url = reverse('work-list')

        work = mommy.make('core.Work', user=self.user, task=task, _fill_optional=True)
        work_list.append(work)

        url = reverse('work-list')

        resp = self.app.get(url)

        for work in work_list:
            self.assertContains(resp, work.name)
            self.assertContains(resp, work.description)

    def test_detail(self):
        """Create Work in database,
        open detail view and
        check that selected fields are visible
        """
        self.init_users()

        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, personal=False, _fill_optional=True)
        goal = mommy.make('core.Goal', need=need, user=self.user, personal=False, _fill_optional=True)
        idea = mommy.make('core.Idea', goal=[goal, ], user=self.user, personal=False, _fill_optional=True)
        plan = mommy.make('core.Plan', idea=idea, user=self.user, personal=False, _fill_optional=True)
        step = mommy.make('core.Step', plan=plan, user=self.user, personal=False, _fill_optional=True)
        task = mommy.make('core.Task', step=step, user=self.user, personal=False, _fill_optional=True)
        work = mommy.make('core.Work', task=task, user=self.user, personal=False, _fill_optional=True)

        url = reverse('work-detail', args=(work.pk,))

        resp = self.app.get(url)
        self.assertContains(resp, work.task)

        self.assertContains(resp, work.name)

        self.assertContains(resp, work.url or "")

        self.assertContains(resp, work.user)

        self.assertContains(resp, work.file or "")

        self.assertContains(resp, work.description)


class IdeaTest(WebTest, AuthTestMixin):

    def test_list(self):
        """Create list of Idea in database,
        open list view and
        check that selected fields are visible
        for each object
        """
        self.init_users()

        self.login(self.user.email, 'test')

        idea_list = []
        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, _fill_optional=True)
        goal = mommy.make('core.Goal', need=need, user=self.user, _fill_optional=True)
        idea = mommy.make('core.Idea', goal=[goal,], user=self.user, _fill_optional=True)
        idea_list.append(idea)

        idea = mommy.make('core.Idea', goal=[goal, ], user=self.user, _fill_optional=True)
        idea_list.append(idea)

        url = reverse('idea-list')
        resp = self.app.get(url)

        for idea in idea_list:
            self.assertContains(resp, idea.name)

    def test_udpate(self):
        """Update object using view
        Check database for updated object
        """
        self.init_users()

        self.login(self.user.email, 'test')

        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, _fill_optional=True)
        goal = mommy.make('core.Goal', need=need, type=type, user=self.user, _fill_optional=True)
        idea = mommy.make('core.Idea', goal=[goal, ], user=self.user, _fill_optional=True)

        url = reverse('idea-update', kwargs={
            'slug': idea.pk, })

        idea_compare = mommy.make(
            'core.Idea',
            user=self.user,
            goal=[goal, ],
            _fill_optional=True)

        resp = self.app.get(url)

        form = resp.form
        form['description'] = idea_compare.description
        form['name'] = idea_compare.name
        form['summary'] = idea_compare.summary
        form['goal'] = [goal.id for goal in idea_compare.goal.all()]
        form['sharewith'] = [self.user.id,]
        form.submit()

        idea_updated = Idea.objects.get(pk=idea.pk)

        self.assertEqual(
            idea_compare.description,
            idea_updated.description
        )
        self.assertEqual(
            idea_compare.name,
            idea_updated.name
        )
        self.assertEqual(
            idea_compare.summary,
            idea_updated.summary
        )

    def test_create(self):
        """Create Idea object using view
        Check database for created object
        """
        self.init_users()

        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, _fill_optional=True)
        goal = mommy.make('core.Goal', need=need, user=self.user, _fill_optional=True)
        idea = mommy.make('core.Idea', goal=[goal, ], user=self.user, _fill_optional=True)

        url = reverse('idea-create')

        # Access forbidden for AnonymousUser
        resp = self.app.get(url, status=302)

        self.login(self.user.email, 'test')

        resp = self.app.get(url)

        form = resp.form
        form['description'] = idea.description
        form['name'] = idea.name
        form['summary'] = idea.summary
        form['goal'] = [goal.id, ]
        form['super_equity'] = form['super_equity'].options[0][0]
        form['sharewith'] = [self.user.id,]
        form.submit()

        idea_created = Idea.objects.latest('id')

        self.assertEqual(
            idea_created.description,
            idea.description
        )
        self.assertEqual(
            idea_created.name,
            idea.name
        )
        self.assertEqual(
            idea_created.summary,
            idea.summary
        )

    def test_delete(self):
        """Create Idea in database,
        open delete view and
        check that object was removed
        """
        self.init_users()
        self.login(self.user.email, 'test')

        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, _fill_optional=True)
        goal = mommy.make('core.Goal', need=need, type=type, user=self.user, _fill_optional=True)
        idea = mommy.make('core.Idea', goal=[goal, ], user=self.user, _fill_optional=True)
        self.assertEqual(Idea.objects.count(), 1)
        url = reverse('idea-delete', args=(idea.pk,))

        resp = self.app.get(url)
        resp.form.submit()
        self.assertEqual(Idea.objects.count(), 0)

    def test_detail(self):
        """Create Idea in database,
        open detail view and
        check that selected fields are visible
        """
        self.init_users()

        self.login(self.user.email, 'test')

        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, _fill_optional=True)
        goal = mommy.make('core.Goal', need=need, user=self.user, _fill_optional=True)
        idea = mommy.make('core.Idea', goal=[goal, ], user=self.user, _fill_optional=True)
        url = reverse('idea-detail', args=(idea.pk,))

        idea = mommy.make('core.Idea', goal=[goal,], user=self.user, _fill_optional=True)
        url = reverse('idea-detail', args=(idea.pk,))

        resp = self.app.get(url)
        self.assertContains(resp, idea.description)

        self.assertContains(resp, idea.name)

        self.assertContains(resp, idea.user)


class StepTest(WebTest, AuthTestMixin):

    def test_udpate(self):
        """Update object using view
        Check database for updated object
        """
        self.init_users()

        self.login(self.user.email, 'test')

        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, _fill_optional=True)
        goal = mommy.make('core.Goal', need=need, type=type, user=self.user, _fill_optional=True)
        idea = mommy.make('core.Idea', goal=[goal, ], user=self.user, _fill_optional=True)
        plan = mommy.make('core.Plan', idea=idea, user=self.user, _fill_optional=True)
        step = mommy.make('core.Step', plan=plan, user=self.user, _fill_optional=True)

        url = reverse('step-update', kwargs={
            'slug': step.pk, })

        step_compare = mommy.make(
            'core.Step',
            plan=plan,
            user=self.user,
            _fill_optional=True)

        resp = self.app.get(url)

        form = resp.form
        form['name'] = step_compare.name
        form['deliverables'] = step_compare.deliverables
        form['priority'] = step_compare.priority
        form['plan'] = step_compare.plan.pk
        form['objective'] = step_compare.objective
        form['investables'] = step_compare.investables
        form['sharewith'] = [self.user.id,]
        form.submit()

        step_updated = Step.objects.get(pk=step.pk)

        self.assertEqual(
            step_compare.name,
            step_updated.name
        )
        self.assertEqual(
            step_compare.deliverables,
            step_updated.deliverables
        )
        self.assertEqual(
            step_compare.priority,
            step_updated.priority
        )
        self.assertEqual(
            step_compare.objective,
            step_updated.objective
        )
        self.assertEqual(
            step_compare.investables,
            step_updated.investables
        )

    def test_create(self):
        """Create Step object using view
        Check database for created object
        """
        self.init_users()

        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, _fill_optional=True)
        goal = mommy.make('core.Goal', need=need, type=type, user=self.user, _fill_optional=True)
        idea = mommy.make('core.Idea', goal=[goal,], user=self.user, _fill_optional=True)
        plan = mommy.make('core.Plan', idea=idea, user=self.user, _fill_optional=True)
        step = mommy.make('core.Step', plan=plan, user=self.user, _fill_optional=True)

        url = reverse('step-create', kwargs={
            'plan': step.plan.pk,
        })

        # Access forbidden for AnonymousUser
        resp = self.app.get(url, status=302)

        self.login(self.user.email, 'test')

        resp = self.app.get(url)

        form = resp.form
        form['name'] = step.name
        form['deliverables'] = step.deliverables
        form['priority'] = step.priority
        form['objective'] = step.objective
        form['investables'] = step.investables
        form['sharewith'] = [self.user.id,]
        form.submit()

        step_created = Step.objects.latest('id')

        self.assertEqual(
            step_created.name,
            step.name
        )
        self.assertEqual(
            step_created.deliverables,
            step.deliverables
        )
        self.assertEqual(
            step_created.priority,
            step.priority
        )
        self.assertEqual(
            step_created.objective,
            step.objective
        )
        self.assertEqual(
            step_created.investables,
            step.investables
        )

    def test_delete(self):
        """Create Step in database,
        open delete view and
        check that object was removed
        """
        self.init_users()

        self.login(self.user.email, 'test')

        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, _fill_optional=True)
        goal = mommy.make('core.Goal', need=need, type=type, user=self.user, _fill_optional=True)
        idea = mommy.make('core.Idea', goal=[goal, ], user=self.user, _fill_optional=True)
        plan = mommy.make('core.Plan', idea=idea, user=self.user, _fill_optional=True)
        step = mommy.make('core.Step', plan=plan, user=self.user, _fill_optional=True)

        self.assertEqual(Step.objects.count(), 1)
        url = reverse('step-delete', args=(step.pk,))

        resp = self.app.get(url)
        resp.form.submit()
        self.assertEqual(Step.objects.count(), 0)

    def test_list(self):
        """Create list of Step in database,
        open list view and
        check that selected fields are visible
        for each object
        """
        self.init_users()

        step_list = []

        self.login(self.user.email, 'test')

        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, _fill_optional=True)
        goal = mommy.make('core.Goal', need=need, type=type, user=self.user, _fill_optional=True)
        idea = mommy.make('core.Idea', goal=[goal, ], user=self.user, _fill_optional=True)
        plan = mommy.make('core.Plan', idea=idea, user=self.user, _fill_optional=True)
        step = mommy.make('core.Step', plan=plan, user=self.user, _fill_optional=True)
        step_list.append(step)

        url = reverse('step-list')

        step = mommy.make('core.Step', plan=plan, user=self.user, _fill_optional=True)
        step_list.append(step)

        url = reverse('step-list')

        resp = self.app.get(url)

        for step in step_list:
            self.assertContains(resp, step.name)

    def test_detail(self):
        """Create Step in database,
        open detail view and
        check that selected fields are visible
        """
        self.init_users()

        self.login(self.user.email, 'test')

        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, _fill_optional=True)
        goal = mommy.make('core.Goal', need=need, type=type, user=self.user, _fill_optional=True)
        idea = mommy.make('core.Idea', goal=[goal, ], user=self.user, _fill_optional=True)
        plan = mommy.make('core.Plan', idea=idea, user=self.user, _fill_optional=True)
        step = mommy.make('core.Step', plan=plan, user=self.user, _fill_optional=True)

        url = reverse('step-detail', args=(step.pk,))

        resp = self.app.get(url)

        self.assertContains(resp, step.user)

        self.assertContains(resp, step.name)

        self.assertContains(resp, step.deliverables)

        #self.assertContains(resp, step.priority)

        self.assertContains(resp, step.plan)

        self.assertContains(resp, step.objective)

        self.assertContains(resp, step.investables)


class TaskTest(WebTest, AuthTestMixin):

    def test_udpate(self):
        """Update object using view
        Check database for updated object
        """
        self.init_users()

        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, _fill_optional=True)
        goal = mommy.make('core.Goal', need=need, type=type, user=self.user, _fill_optional=True)
        idea = mommy.make('core.Idea', goal=[goal, ], user=self.user, _fill_optional=True)
        plan = mommy.make('core.Plan', idea=idea, user=self.user, _fill_optional=True)
        step = mommy.make('core.Step', plan=plan, user=self.user, _fill_optional=True)
        task = mommy.make('core.Task', step=step, user=self.user, _fill_optional=True)

        url = reverse('task-update', kwargs={
            'slug': task.pk, })

        # Access forbidden for AnonymousUser
        resp = self.app.get(url, status=404)

        self.login(self.user.email, 'test')

        task_compare = mommy.make(
            'core.Task',
            step=step,
            user=self.user,
            _fill_optional=True)

        resp = self.app.get(url)

        form = resp.form
        form['name'] = task_compare.name
        form['priority'] = task_compare.priority
        form['step'] = task_compare.step.pk
        form['sharewith'] = [self.user.id,]
        form.submit()

        task_updated = Task.objects.get(pk=task.pk)

        self.assertEqual(
            task_compare.name,
            task_updated.name
        )
        self.assertEqual(
            task_compare.priority,
            task_updated.priority
        )

    def test_create(self):
        """Create Task object using view
        Check database for created object
        """
        self.init_users()

        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, _fill_optional=True)
        goal = mommy.make('core.Goal', need=need, type=type, user=self.user, _fill_optional=True)
        idea = mommy.make('core.Idea', goal=[goal, ], user=self.user, _fill_optional=True)
        plan = mommy.make('core.Plan', idea=idea, user=self.user, _fill_optional=True)
        step = mommy.make('core.Step', plan=plan, user=self.user, _fill_optional=True)
        task = mommy.make('core.Task', step=step, user=self.user, _fill_optional=True)

        url = reverse('task-create', kwargs={
            'step': task.step.pk,
        })

        # Access forbidden for AnonymousUser
        resp = self.app.get(url, status=302)

        self.login(self.user.email, 'test')

        resp = self.app.get(url)

        form = resp.form
        form['name'] = task.name
        form['priority'] = task.priority
        form['sharewith'] = [self.user.id,]
        form.submit()

        task_created = Task.objects.latest('id')

        self.assertEqual(
            task_created.name,
            task.name
        )
        self.assertEqual(
            task_created.priority,
            task.priority
        )

    def test_delete(self):
        """Create Task in database,
        open delete view and
        check that object was removed
        """
        self.init_users()

        self.login(self.user.email, 'test')

        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, _fill_optional=True)
        goal = mommy.make('core.Goal', need=need, type=type, user=self.user, _fill_optional=True)
        idea = mommy.make('core.Idea', goal=[goal, ], user=self.user, _fill_optional=True)
        plan = mommy.make('core.Plan', idea=idea, user=self.user, _fill_optional=True)
        step = mommy.make('core.Step', plan=plan, user=self.user, _fill_optional=True)
        task = mommy.make('core.Task', step=step, user=self.user, _fill_optional=True)
        self.assertEqual(Task.objects.count(), 1)

        url = reverse('task-delete', args=(task.pk,))

        resp = self.app.get(url)
        resp.form.submit()
        self.assertEqual(Task.objects.count(), 0)

    def test_list(self):
        """Create list of Task in database,
        open list view and
        check that selected fields are visible
        for each object
        """
        self.init_users()

        self.login(self.user.email, 'test')

        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, _fill_optional=True)
        goal = mommy.make('core.Goal', need=need, type=type, user=self.user, _fill_optional=True)
        idea = mommy.make('core.Idea', goal=[goal, ], user=self.user, _fill_optional=True)
        plan = mommy.make('core.Plan', idea=idea, user=self.user, _fill_optional=True)
        step = mommy.make('core.Step', plan=plan, user=self.user, _fill_optional=True)
        task = mommy.make('core.Task', step=step, user=self.user, _fill_optional=True)

        task_list = []
        task_list.append(task)
        task = mommy.make(
            'core.Task',
            step=step,
            user=self.user,
            _fill_optional=True)
        task_list.append(task)

        url = reverse('task-list')
        resp = self.app.get(url)

        for task in task_list:
            self.assertContains(resp, task.name)


    def test_detail(self):
        """Create Task in database,
        open detail view and
        check that selected fields are visible
        """
        self.init_users()

        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, _fill_optional=True)
        goal = mommy.make('core.Goal', need=need, type=type, user=self.user, personal=False, _fill_optional=True)
        idea = mommy.make('core.Idea', goal=[goal, ], user=self.user, personal=False, _fill_optional=True)
        plan = mommy.make('core.Plan', idea=idea, user=self.user, personal=False, _fill_optional=True)
        step = mommy.make('core.Step', plan=plan, user=self.user, personal=False, _fill_optional=True)
        task = mommy.make('core.Task', step=step, user=self.user, personal=False, _fill_optional=True)
        url = reverse('task-detail', args=(task.pk,))

        resp = self.app.get(url)
        self.assertContains(resp, task.name)

        #self.assertContains(resp, task.priority)

        self.assertContains(resp, task.step)

        self.assertContains(resp, task.user)


class UserTest(WebTest, AuthTestMixin):

    def test_detail(self):
        """Create User in database,
        open detail view and
        check that selected fields are visible
        """
        self.init_users()

        user = mommy.make('users.User', _fill_optional=True)
        url = reverse('user-detail', args=(user.username,))

        resp = self.app.get(url)
        self.assertContains(resp, user.about)

    def test_udpate(self):
        """Update object using view
        Check database for updated object
        """
        self.init_users()

        user = mommy.make('users.User', _fill_optional=True)

        url = reverse('user-update', kwargs={
        })

        # Access forbidden for AnonymousUser
        resp = self.app.get(url, status=302)

        self.login(self.user.email, 'test')

        user = self.user
        user_compare = mommy.make('users.User', _fill_optional=True)

        resp = self.app.get(url)

        form = resp.form
        form['about'] = user_compare.about
        form['email'] = user_compare.email
        form.submit()

        user_updated = User.objects.get(pk=user.pk)

        self.assertEqual(
            user_compare.about,
            user_updated.about
        )
        self.assertEqual(
            user_compare.email,
            user_updated.email
        )


class NeedTest(WebTest, AuthTestMixin):

    def test_create(self):
        """Create Need object using view
        Check database for created object
        """
        self.init_users()

        need = mommy.make('core.Need', _fill_optional=True)

        url = reverse('need-create', kwargs={
        })

        self.login(self.user.email, 'test')

        resp = self.app.get(url)

        form = resp.form
        form['name'] = need.name
        form['sharewith'] = [self.user.id,]
        form.submit()

        need_created = Need.objects.latest('id')

        self.assertEqual(
            need_created.name,
            need.name
        )

    def test_list(self):
        """Create list of Need in database,
        open list view and
        check that selected fields are visible
        for each object
        """
        self.init_users()
        self.login(self.user.email, 'test')

        need_list = []
        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, user=self.user, _fill_optional=True)
        need_list.append(need)

        url = reverse('need-list')

        need = mommy.make('core.Need', type=type, personal=False, user=self.user, _fill_optional=True)
        need_list.append(need)

        resp = self.app.get(url)

        for need in need_list:
            self.assertContains(resp, need.definition)

    def test_detail(self):
        """Create Need in database,
        open detail view and
        check that selected fields are visible
        """
        self.init_users()

        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, user=self.user, personal=False, _fill_optional=True)
        url = reverse('need-detail', args=(need.pk,))

        resp = self.app.get(url)

        #self.assertContains(resp, need.type or "")

        self.assertContains(resp, need.name)


class PlanTest(WebTest, AuthTestMixin):

    def test_list(self):
        """Create list of Plan in database,
        open list view and
        check that selected fields are visible
        for each object
        """
        self.init_users()

        plan_list = []
        self.login(self.user.email, 'test')

        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, _fill_optional=True)
        goal = mommy.make('core.Goal', need=need, type=type, user=self.user, _fill_optional=True)
        idea = mommy.make('core.Idea', goal=[goal, ], user=self.user, _fill_optional=True)
        plan = mommy.make('core.Plan', idea=idea, user=self.user, _fill_optional=True)
        plan_list.append(plan)

        url = reverse('plan-list')

        plan = mommy.make('core.Plan', idea=idea, user=self.user, _fill_optional=True)
        plan_list.append(plan)

        url = reverse('plan-list')
        resp = self.app.get(url)

        for plan in plan_list:
            self.assertContains(resp, plan.name)

    def test_udpate(self):
        """Update object using view
        Check database for updated object
        """
        self.init_users()

        self.login(self.user.email, 'test')

        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, _fill_optional=True)
        goal = mommy.make('core.Goal', need=need, type=type, user=self.user, _fill_optional=True)
        idea = mommy.make('core.Idea', goal=[goal, ], user=self.user, _fill_optional=True)
        plan = mommy.make('core.Plan', idea=idea, user=self.user, _fill_optional=True)

        url = reverse('plan-update', kwargs={
            'slug': plan.pk, })

        plan_compare = mommy.make(
            'core.Plan',
            idea=idea,
            user=self.user,
            _fill_optional=True)

        member = mommy.make('users.User')

        resp = self.app.get(url)

        form = resp.form
        form['name'] = plan_compare.name
        #form['idea'] = plan_compare.idea.pk
        form['deliverable'] = plan_compare.deliverable
        form['situation'] = plan_compare.situation
        form['members'] = [member.pk, ]
        form['sharewith'] = [self.user.id,]
        form.submit()

        plan_updated = Plan.objects.get(pk=plan.pk)

        self.assertEqual(
            plan_compare.name,
            plan_updated.name
        )
        self.assertEqual(
            plan_compare.deliverable,
            plan_updated.deliverable
        )
        self.assertEqual(
            plan_compare.situation,
            plan_updated.situation
        )

    def test_create(self):
        """Create Plan object using view
        Check database for created object
        """
        self.init_users()

        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, _fill_optional=True)
        goal = mommy.make('core.Goal', need=need, type=type, user=self.user, _fill_optional=True)
        idea = mommy.make('core.Idea', goal=[goal, ], user=self.user, _fill_optional=True)
        plan = mommy.make('core.Plan', idea=idea, user=self.user, _fill_optional=True)

        url = reverse('plan-create')

        # Access forbidden for AnonymousUser
        resp = self.app.get(url, status=302)

        self.login(self.user.email, 'test')

        resp = self.app.get(url)

        member = mommy.make('users.User')

        form = resp.form
        form['name'] = plan.name
        form['deliverable'] = plan.deliverable
        form['situation'] = plan.situation
        form['members'] = [member.pk, ]
        form['sharewith'] = [self.user.id,]
        form.submit()

        plan_created = Plan.objects.latest('id')

        self.assertEqual(
            plan_created.name,
            plan.name
        )
        self.assertEqual(
            plan_created.deliverable,
            plan.deliverable
        )
        self.assertEqual(
            plan_created.situation,
            plan.situation
        )

    def test_delete(self):
        """Create Plan in database,
        open delete view and
        check that object was removed
        """
        self.init_users()
        self.login(self.user.email, 'test')

        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, _fill_optional=True)
        goal = mommy.make('core.Goal', need=need, user=self.user, _fill_optional=True)
        idea = mommy.make('core.Idea', goal=[goal, ], user=self.user, _fill_optional=True)
        plan = mommy.make('core.Plan', idea=idea, user=self.user, _fill_optional=True)

        self.assertEqual(Plan.objects.count(), 1)

        url = reverse('plan-delete', args=(plan.pk,))

        resp = self.app.get(url)
        resp.form.submit()
        self.assertEqual(Plan.objects.count(), 0)

    def test_detail(self):
        """Create Plan in database,
        open detail view and
        check that selected fields are visible
        """
        self.init_users()

        type = mommy.make('core.Type', _fill_optional=True)
        need = mommy.make('core.Need', type=type, personal=False, _fill_optional=True)
        goal = mommy.make('core.Goal', need=need, personal=False, user=self.user, _fill_optional=True)
        idea = mommy.make('core.Idea', goal=[goal, ], personal=False, user=self.user, _fill_optional=True)
        plan = mommy.make('core.Plan', idea=idea, user=self.user, personal=False, _fill_optional=True)

        url = reverse('plan-detail', args=(plan.pk,))

        resp = self.app.get(url)
        self.assertContains(resp, plan.name)

        self.assertContains(resp, plan.idea)

        self.assertContains(resp, plan.deliverable)

        self.assertContains(resp, plan.user)

        self.assertContains(resp, plan.situation)
