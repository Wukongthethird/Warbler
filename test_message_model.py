"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from app import app,  CURR_USER_KEY
import os
from unittest import TestCase
# from sqlalchemy.exc import IntegrityError

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
PASSWORD = "HASHED_PASSWORD"

# Now we can import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

class MessageModelTestCase(TestCase):
    """Test Message Model"""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url=None
        )

        db.session.add(u)
        db.session.commit()

        self.client = app.test_client()
        self.test_user = u

    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.rollback()

    def test_message_create(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user.id
            
            new_message = Message(  
                text = "Test Message",
                user_id = self.test_user.id
            )

            db.session.add(new_message)
            db.session.commit()

            user2 = User(username="testuser2",
                         email="test2@test.com",
                         password="testuser2"
                         )

            db.session.add(user2)
            db.session.commit()

            messages = Message.query.all()

        self.assertEqual(len(messages),1)
        self.assertEqual( self.test_user.id, new_message.user_id)
        self.assertNotEqual( user2.id, new_message.user_id)


    
