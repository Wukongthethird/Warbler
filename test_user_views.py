  # with self.client as c:
            # resp = c.post('/signup', data={"username":"testuser",
            #                 "email":"test2@test.com",
            #                 "password":"testuser2"
            #                 })

            # html = resp.get_data(as_text=True)
            
            # users = User.query.all()
            # self.assertEqual(len(users),1)
            # self.assertIn('<li><a href="/signup">Sign up</a></li>', html)

"""User View tests."""

import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

        self.testuser_id = self.testuser.id
        self.testuser2_id = self.testuser2.id

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

    def test_view_user_page(self):
        """Can logged in user view another user's page?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            user2 = User.query.get(self.testuser2_id)

            resp = c.get(f"/users/{self.testuser2_id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"{user2.username}", html)

            # Test that user cannot view another user's profile if not logged in
            with c.session_transaction() as sess:
                del sess[CURR_USER_KEY]
            
            resp = c.get(f"/users/{self.testuser2_id}", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<a href="/signup">Sign up</a>', html)
      
    def test_profile(self):
      """Can logged in user view and edit profile?"""

      with self.client as c:
          with c.session_transaction() as sess:
              sess[CURR_USER_KEY] = self.testuser.id
          
          # GET route
          resp = c.get('/users/profile')
          html = resp.get_data(as_text=True)

          self.assertEqual(resp.status_code, 200)
          self.assertIn(f'{self.testuser.username}', html)

          # POST route
          resp = c.post('/users/profile', data={"username":"helloworld",
                            "email":"test@test.com",
                            "password":"testuser",
                            "image_url": None,
                            "bio": "",
                            "header_image_url": None
                            },
                            follow_redirects=True)
          
          html = resp.get_data(as_text=True)
          
          self.assertEqual(resp.status_code, 200)
          self.assertIn('<h4 id="sidebar-username">@helloworld</h4>', html)