import unittest
from flask import Flask, request, session
from your_app_module import app  # Replace 'your_app_module' with the actual module name
from unittest.mock import patch

class TestLoginPage(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()
        app.secret_key = "test_secret_key"  # Set a known secret key for testing

    @patch('your_app_module.authenticate')
    def test_login_successful(self, mock_authenticate):
        # Mock the authenticate function to return a token for successful login
        mock_authenticate.return_value = "fake_auth_token"

        with app.test_request_context('/'):
            with self.app as client:
                # Send a POST request to the '/' route with valid credentials
                response = client.post('/', data={'username': 'test_user', 'password': 'test_password'})

                # Assert that the response status code is as expected for a successful login
                self.assertEqual(response.status_code, 200)

                # Assert that the session contains the expected auth token
                self.assertEqual(session['auth_token'], "fake_auth_token")

    @patch('your_app_module.authenticate')
    def test_login_failed(self, mock_authenticate):
        # Mock the authenticate function to return None for failed login
        mock_authenticate.return_value = None

        with app.test_request_context('/'):
            with self.app as client:
                # Send a POST request to the '/' route with invalid credentials
                response = client.post('/', data={'username': 'invalid_user', 'password': 'invalid_password'})

                # Assert that the response status code is as expected for a failed login
                self.assertEqual(response.status_code, 200)  # Adjust if your app returns a different status code

                # Assert that the session does not contain an auth token
                self.assertIsNone(session.get('auth_token'))

if __name__ == '__main__':
    unittest.main()
