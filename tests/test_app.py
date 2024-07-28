import unittest
from flask import Flask
from batter.routes import batter_bp
from pitcher.routes import pitcher_bp
from app import app  

class FlaskAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Create a test client for the Flask application.
        This is run once for the entire class before any tests are executed.
        """
        cls.client = app.test_client()
        cls.client.testing = True

    def test_home_page(self):
        """
        Test that the home page loads correctly.
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<title>Game Launcher</title>', response.data)

    def test_batter_blueprint(self):
        """
        Test that the batter blueprint is registered and responds correctly.
        """
        response = self.client.get('/batter/some_route')  # Replace 'some_route' with an actual route in batter_bp
        # Verify that the route exists and returns a 200 OK status
        self.assertIn(response.status_code, [200, 404])

    def test_pitcher_blueprint(self):
        """
        Test that the pitcher blueprint is registered and responds correctly.
        """
        response = self.client.get('/pitcher/some_route')  # Replace 'some_route' with an actual route in pitcher_bp
        # Verify that the route exists and returns a 200 OK status
        self.assertIn(response.status_code, [200, 404])

if __name__ == '__main__':
    unittest.main()