import unittest

from app import create_app
from extensions import db
from models import Enquiry, User


def build_app():
    app = create_app(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SECRET_KEY": "test-key",
        }
    )
    with app.app_context():
        db.create_all()
        admin = User(full_name="Test Admin", email="admin@example.com", role="admin")
        admin.set_password("test-password")
        db.session.add(admin)
        db.session.commit()
    return app


class ApplicationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = build_app()
        self.client = self.app.test_client()

    def test_public_pages_load(self):
        paths = [
            "/",
            "/about",
            "/services",
            "/services/transport-logistics",
            "/capabilities",
            "/partners",
            "/contact",
            "/health",
            "/robots.txt",
            "/sitemap.xml",
        ]
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)

    def test_enquiry_submission_and_admin_login(self):
        response = self.client.post(
            "/contact",
            data={
                "full_name": "Project Client",
                "company": "Example Limited",
                "email": "client@example.com",
                "phone": "+254700000000",
                "service": "Transport & Project Logistics",
                "project_location": "Nairobi",
                "message": "We need coordinated delivery of reinforcement steel to our project site.",
                "consent": "y",
            },
        )
        self.assertEqual(response.status_code, 302)
        with self.app.app_context():
            self.assertEqual(Enquiry.query.count(), 1)

        response = self.client.post(
            "/login",
            data={"email": "admin@example.com", "password": "test-password"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Enquiry workspace", response.data)


if __name__ == "__main__":
    unittest.main()
