# test.py
import os
import unittest

from project import app, db
from project._config import basedir
from project.models import User

TEST_DB = 'test.db'


class AllTests(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
                                                os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def login(self, name, password):
        return self.app.post('/', data=dict(
            name=name, password=password), follow_redirects=True
                             )

    def create_user(self, name, email, password):
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

    def create_admin_user(self, name, email, password):
        new_user = User(name=name, email=email, password=password, role='admin')
        db.session.add(new_user)
        db.session.commit()

    def logout(self):
        return self.app.get('logout/', follow_redirects=True)

    def register(self, name, email, password, confirm):
        return self.app.post(
            'register/',
            data=dict(name=name, email=email, password=password, confirm_password=confirm),
            follow_redirects=True
        )

    def create_task(self):
        return self.app.post('/add/', data=dict(
            name='Go to the bank',
            due_date='2016-08-10',
            priority='1'
        ), follow_redirects=True)

    def delete_task(self, task_id):
        return self.app.get(f'/delete/{task_id}', follow_redirects=True)

    def test_user_can_register(self):
        new_user = User('michael', 'michael@mherman.org', 'michaelherman')
        db.session.add(new_user)
        db.session.commit()
        test = db.session.query(User).first()
        assert test.name == 'michael'

    def test_form_is_present(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please sign in to access your task list<', response.data)

    def test_users_cannot_login_unless_registered(self):
        response = self.login('foo', 'bar')
        self.assertIn(b'Invalid username or password', response.data)

    def test_if_user_can_login(self):
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        response = self.login('Michael', 'python')
        self.assertIn(b'Welcome', response.data)

    def test_invalid_form_data(self):
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        response = self.login('alert("alert box!");', 'foo')
        self.assertIn(b'Invalid username or password', response.data)

    def test_form_is_present_on_register_page(self):
        response = self.app.get('/register/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please register to access the task list', response.data)

    def test_user_registration(self):
        self.app.get('register/', follow_redirects=True)
        response = self.register(
            'Michael', 'michael@realpython.com', 'python', 'python')
        self.assertIn(b'Thanks for registering. Please login', response.data)

    def test_user_registration_error(self):
        self.app.get('register/', follow_redirects=True)
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        self.app.get('register/', follow_redirects=True)
        response = self.register(
            'Michael', 'michael@realpython.com', 'python', 'python'
        )
        self.assertIn(
            b'That username and/or email already exist.',
            response.data
        )

    def test_logged_in_users_can_logout(self):
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        self.login('Michael', 'python')
        response = self.logout()
        self.assertIn(b'Goodbye!', response.data)

    def test_logged_in_users_can_access_tasks_page(self):
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        self.login('Michael', 'python')
        response = self.app.get('/tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Add a new task:', response.data)

    def test_not_logged_in_users_cannot_access_tasks_page(self):
        response = self.app.get('tasks/', follow_redirects=True)
        self.assertIn(b'You are not authorized to view this page', response.data)

    def test_users_can_add_tasks(self):
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        response = self.create_task()
        self.assertIn(
            b'New entry was successfully posted. Thanks.', response.data
        )

    def test_users_can_add_tasks(self):
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.post('/add/', data=dict(
            name='Go to the bank',
            due_date='2016-08-10',
        ), follow_redirects=True)
        self.assertIn(
            b'This field is required.', response.data
        )

    def test_users_can_complete_and_delete_tasks(self):
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        self.login('Michael', 'python')
        self.app.get('/tasks/', follow_redirects=True)
        self.create_task()
        response = self.app.get('/complete/1', follow_redirects=True)
        self.assertIn(b'The task was marked as complete', response.data)
        response = self.app.get('/delete/1', follow_redirects=True)
        self.assertIn(b'The task was deleted.', response.data)

    def test_users_cannot_complete_tasks_that_are_not_created_by_them(self):
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_user('Fletcher', 'fletcher@realpython.com', 'python101')
        self.login('Fletcher', 'python101')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get("complete/1/", follow_redirects=True)
        self.assertNotIn(
            b'The task was marked as complete', response.data
        )
        self.assertIn(b'You can only update tasks that belong to you.', response.data)

    def test_users_cannot_delete_tasks_that_are_not_created_by_them(self):
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_user('Fletcher', 'fletcher@realpython.com', 'python101')
        self.login('Fletcher', 'python101')
        self.app.get('tasks/', follow_redirects=True)
        response = self.delete_task(1)
        self.assertNotIn(
            b'The task was deleted.', response.data
        )
        self.assertNotIn(b'You can only update tasks that belong to you.', response.data)
        self.assertIn(b'You can only delete tasks that belong to you.', response.data)

    def test_user_role(self):
        db.session.add(
            User(
                "Johnny",
                "john@doe.com",
                "johnny"
            )
        )
        db.session.commit()
        users = db.session.query(User).all()
        print(users)
        for user in users:
            self.assertEqual(user.role, 'user')

    def test_admin_users_can_complete_and_delete_not_created_by_them_tasks(self):
        self.create_admin_user('Michael', 'michael@realpython.com', 'python')
        self.create_user('Fletcher', 'fletcher@realpython.com', 'python101')
        self.login('Fletcher', 'python101')
        self.app.get('/tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.login('Michael', 'python')
        response = self.app.get('/complete/1', follow_redirects=True)
        self.assertIn(b'The task was marked as complete', response.data)
        response = self.app.get('/delete/1', follow_redirects=True)
        self.assertIn(b'The task was deleted.', response.data)

    def test_task_template_displays_logged_in_user_name(self):
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        response = self.app.get('tasks/', follow_redirects=True)
        self.assertIn(b'Michael', response.data)

    def test_users_cannot_see_task_modify_links_for_tasks_not_created_by_them(self):
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('task/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_user('Michael1', 'michael1@realpython.com', 'python')
        self.login('Michael1', 'python')
        response = self.app.get('/task', follow_redirects=True)
        self.assertNotIn(b'Delete', response.data)
        self.assertNotIn(b'Mark as Complete', response.data)

    def test_users_can_see_task_modify_links_for_tasks_created_by_them(self):
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.create_task()
        response = self.app.get('/tasks', follow_redirects=True)
        self.assertIn(b'Delete', response.data)
        self.assertIn(b'Mark as Complete', response.data)

    def test_admin_users_can_see_task_modify_links_for_all_tasks(self):
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user('Michael1', 'michael1@realpython.com', 'python')
        self.login('Michael1', 'python')
        response = self.app.get('/tasks', follow_redirects=True)
        self.assertIn(b'Delete', response.data)
        self.assertIn(b'Mark as Complete', response.data)


if __name__ == '__main__':
    unittest.main()
