# project/test_main.py

import os
import unittest

from project import app, db
from project._config import basedir
from project.models import User

TEST_DB = 'test.db'


class MainTests(unittest.TestCase):
    # set up and tear down
    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQL_ALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
                                                 os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # helper functions
    def login(self, name, password):
        return self.app.post('/', data=dict(
            name=name, password=password
        ), follow_redirects=True)

    # tests

    def test_404_error(self):
        response = self.app.get('/this-route-does-not-exist/')
        self.assertEquals(response.status_code, 404)
        self.assertIn(b'Sorry. There\'s nothing here.', response.data)

    def test_500_error(self):
        bas_user = User(
            name='Jeremy',
            email='Jeremy@example.com',
            password='Jeremy123'
        )
        db.session.add(bas_user)
        db.session.commit()
        self.assertRaises(ValueError, self.login, 'Jeremy', 'Jeremy123')
        try:
            response = self.login(name='Jeremy', password='Jeremy123')
            self.assertEquals(response.status_code, 500)
        except ValueError as e:
            pass


if __name__ == '__main__':
    unittest.main()
