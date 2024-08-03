import unittest
from flask import Flask
from batter.batter_routes import batter_bp
from pitcher.pitcher_routes import pitcher_bp
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
        self.assertIn(b'<title>Baseball Higher or Lower</title>', response.data)

    def test_batter_blueprint(self):
        """
        Test that the batter blueprint is registered and responds correctly.
        """
        response = self.client.get('/batter/')
        # Verify that the route exists and returns a 200 OK status
        self.assertIn(response.status_code, [200])

    def test_pitcher_blueprint(self):
        """
        Test that the pitcher blueprint is registered and responds correctly.
        """
        response = self.client.get('/pitcher/')
        # Verify that the route exists and returns a 200 OK status
        self.assertIn(response.status_code, [200])

    def test_hitter_blueprint(self):
        """
        Test that the hitter blueprint is registered and responds correctly.
        """
        response = self.client.get('/hitter/')
        # Verify that the route exists and returns a 200 OK status
        self.assertIn(response.status_code, [200])

    def test_homer_blueprint(self):
        """
        Test that the homer blueprint is registered and responds correctly.
        """
        response = self.client.get('/homer/')
        # Verify that the route exists and returns a 200 OK status
        self.assertIn(response.status_code, [200])

    def test_strikeout_blueprint(self):
        """
        Test that the strikeout blueprint is registered and responds correctly.
        """
        response = self.client.get('/strikeout/')
        # Verify that the route exists and returns a 200 OK status
        self.assertIn(response.status_code, [200])

    def test_winner_blueprint(self):
        """
        Test that the winner blueprint is registered and responds correctly.
        """
        response = self.client.get('/winner/')
        # Verify that the route exists and returns a 200 OK status
        self.assertIn(response.status_code, [200])
    

if __name__ == '__main__':
    unittest.main()