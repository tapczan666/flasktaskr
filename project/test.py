import os
import unittest

from views import app, db
from _config import basedir
from models import User

TEST_DB = 'test.db'


class AllTests(unittest.TestCase):

    ##########################
    ### setup and teardown ###
    ##########################

    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQALCHEMY_DATABASE_URI'] = 'sqlite:///' +\
            os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.create_all()

    # executed after each test
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    ######################
    ### helper methods ###
    ######################
    def login(self, name, password):
        return self.app.post('/', data=dict(name=name, password=password),
                             follow_redirects=True)

    def register(self, name, email, password, confirm):
        return self.app.post(
            'register/',
            data=dict(name=name, email=email,
                      password=password, confirm=confirm),
            follow_redirects=True
        )

    #############
    ### tests ###
    #############

    # each test should start with 'test'
    def test_user_can_register(self):
        new_user = User('michael', 'miachael@mherman.org', 'michaelherman')
        db.session.add(new_user)
        db.session.commit()
        test = db.session.query(User).all()
        for t in test:
            t.name
        assert t.name == 'michael'

    def test_form_is_present(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please log in to access your task list', response.data)

    def test_users_cannot_log_in_unless_registered(self):
        response = self.login('foo', 'bar')
        self.assertIn(b'Invalid username or password.', response.data)

    def test_registered_users_can_login(self):
        self.register('Michael', 'michael@realpython.pl', 'python', 'python')
        response = self.login('Michael', 'python')
        self.assertIn(b'Welcome!', response.data)

    def test_invalid_form_data(self):
        self.register('Michael', 'michael@realpython.pl', 'python', 'python')
        response = self.login('alert("alert box!");', 'foo')
        self.assertIn(b'Invalid username or password.', response.data)

    def test_form_is_present_on_register_page(self):
        response = self.app.get('register/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please register to access the task list.',
                      response.data)

    def test_user_registration(self):
        self.app.get('register/', follow_redirects=True)
        self.register('Michael', 'michael@realpython.pl', 'python', 'python')
        self.app.get('register/', follow_redirects=True)
        response = self.register(
            'Michael', 'michael@realpython.pl', 'python', 'python'
        )
        self.assertIn(
            b'That username and/or email already exists.',
            response.data
        )


if __name__ == '__main__':
    unittest.main()
