from app import app, db
import os
import unittest
from config import basedir
from app.api import \
    register_librarian, add_member_db,\
    update_member_db, add_book_db
from app.api import update_book_db
from app.models import Librarian, Member, Book


TEST_DB = 'test.db'


class BasicTests(unittest.TestCase):

    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'\
            + os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

    # executed after each test
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # Helper methods:
    def register(self, email, name, password, confirm):
        return self.app.post(
            '/register',
            data=dict(
                email=email, name=name, password=password,
                confirm=confirm), follow_redirects=True)

    def login(self, email, password):
        return self.app.post(
            '/login',
            data=dict(
                email=email,
                password=password), follow_redirects=True)

    def logout(self):
        return self.app.get(
            '/logout', follow_redirects=True)

    # tests:
    def test_index_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome To LbMS', response.data)

    def test_registeration_page(self):
        response = self.register(
            'admin@gmail.com', 'admin',
            '1234', '1234')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You are now registered and can log in', response.data)

    def test_invalid_registeration(self):
        response = self.register(
            'admin@gmail.com', 'admin',
            '1234', '123')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Passwords do not match', response.data)

    def test_register(self):
        register_librarian('admin', 'admin@gmail.com', '123')
        self.assertEqual(Librarian.query.get('1').name, 'admin')

    def test_login(self):
        register_librarian('admin', 'admin@gmail.com', '123')
        response = self.login('admin@gmail.com', '123')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have been logged in!', response.data)

    def test_add_member(self):
        add_member_db('m_01', 'm_01@gmail.com', '999')
        self.assertEqual(Member.query.get('1').name, 'm_01')

    def test_update_member(self):
        member = Member(name='m_01', email='m_01@gmail.com', phone='999')
        db.session.add(member)
        db.session.commit()
        update_member_db('1', 'm_updated', 'm_01@gmail.com', '888')
        self.assertEqual(member.name, 'm_updated')
        self.assertEqual(member.phone, '888')

    def test_add_book(self):
        add_book_db('b_01', '12345', '5', ['a1', 'a2'])
        self.assertEqual(Book.query.get('1').title, 'b_01')

    def test_update_book(self):
        add_book_db('b_01', '12345', '5', ['a1', 'a2'])
        update_book_db('1', 'b_updated', '1245', '5', ['a1', 'a2'])
        book = Book.query.get('1')
        self.assertEqual(book.isbn, '1245')


if __name__ == "__main__":
    unittest.main()
