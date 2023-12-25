import unittest
from config import TestConfig
from app import create_app, db
from app.models import User, BlogPost


class BlogTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self) -> None:
        db.session.romove()
        db.drop_all()
        self.app_context.pop()

    def test_user_register(self):
        response = self.client.post('/register', data={
            'email': 'newuser@example.com',
            'password': 'newpassword',
            'name': 'New User'
        }, follow_redirects=True)
        self.assertIn(b'Registration Successful', response.data)  # Adjust based on actual flash message
        new_user = User.query.filter_by(email='newuser@example.com').first()
        self.assertIsNotNone(new_user)

    def test_user_login(self):
        # Create a user
        user = User(email='test@example.com', password='test')
        db.session.add(user)
        db.session.commit()

        # Try to login
        response = self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'test'
        }, follow_redirects=True)
        self.assertIn(b'Welcome', response.data)  # or a similar success message

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_blog_post_creation(self):
        # Assuming you have a user logged in for creating posts
        self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'test',
            'is_admin': True,
        }, follow_redirects=True)

        response = self.client.post('/new-post', data={
            'title': 'Test Post',
            'subtitle': 'Test Subtitle',
            'body': 'This is a test post.',
            'img_url': 'http://example.com/image.png'
        }, follow_redirects=True)
        self.assertIn(b'Post created successfully', response.data)
        post = BlogPost.query.filter_by(title='Test Post').first()
        self.assertIsNotNone(post)

    def test_blog_post_deletion(self):
        # Create a post
        post = BlogPost(title='Delete Me', content='Delete this post.')
        db.session.add(post)
        db.session.commit()

        # Delete the post
        response = self.client.post(f'/delete-post/{post.id}', follow_redirects=True)
        self.assertIn(b'Post deleted successfully', response.data)
        deleted_post = BlogPost.query.get(post.id)
        self.assertIsNone(deleted_post)


if __name__ == '__main__':
    unittest.main()
