from flaskProject.main import app
import unittest
from flask import Flask, request, session
from unittest.mock import patch

class testLogin(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()
        app.secret_key = "fake_key"

    @patch('flaskProject.main.authenticate')
    def testLoginSuccessful(self, fake_authenticate):
        fake_authenticate.return_value = "fake_auth_token"
        with app.test_request_context('/'):
            with self.app as client:
                response = client.post('/', data={'username': 'test_user', 'password': 'test_password'})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(session['auth_token'], "fake_auth_token")

    @patch('flaskProject.main.authenticate')
    def testLoginFailed(self, fake_authenticate):
        fake_authenticate.return_value = None
        with app.test_request_context('/'):
            with self.app as client:
                response = client.post('/', data={'username': 'invalid_user', 'password': 'invalid_password'})
                self.assertEqual(response.status_code, 200)
                self.assertIsNone(session.get('auth_token'))



        
