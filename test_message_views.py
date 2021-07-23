"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


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



class MessageViewTestCase(TestCase):
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

        db.session.commit()

        self.testmessage = Message( text= "Hello",
                                    user_id = self.testuser.id)
        

        db.session.add(self.testmessage)
        db.session.commit()

        self.testmessage_id = self.testmessage.id
        
    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()
    

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test
          
            resp = c.post("/messages/new", data={"text": "Hello", "user_id": self.testuser.id })
            
            
            messages = Message.query.all()
            message = Message.query.filter( Message.id == self.testmessage_id).one()

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)
            self.assertEqual( len(messages), 2 )
            self.assertEqual( message.text , "Hello")

            with c.session_transaction() as sess:
                del sess[CURR_USER_KEY]
                
            resp = c.post("/messages/new", data={"text": "Not Allowed", "user_id": self.testuser.id })
            
            messages = Message.query.all()

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)
            self.assertEqual( len(messages), 2 )
            self.assertIs( bool(Message.query.filter( Message.text == "Not Allowed").all() ), False)
      
    def test_delete_message(self):
        """Can a user delete a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post( f'/messages/{self.testmessage.id}/delete' , follow_redirects = True)
            html = resp.get_data( as_text=True)

            messages = Message.query.all()

            self.assertEqual(len(messages), 0)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'{self.testuser.username}', html)
        
            self.tearDown()
            self.setUp()

            with c.session_transaction() as sess:
                del sess[CURR_USER_KEY]
                
            resp = c.post( f'/messages/{self.testmessage.id}/delete' , follow_redirects = True)
            html = resp.get_data( as_text=True)

            messages = Message.query.all()

            self.assertEqual(len(messages), 1)
 
            self.assertIn('<a href="/signup">Sign up</a>', html)
    
