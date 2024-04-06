import unittest
from unittest.mock import patch, MagicMock
from Backend.flaskProject.main import app

class test_login(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('Backend.flaskProject.main.requests.post')
    def test_loginPage(self, mock_post):
        mock_reponse = MagicMock()
        mock_reponse.status_code = 200
        mock_reponse.json.return_value = {'auth_token': 'fake_auth_token'}
        mock_post.return_value = mock_reponse
        response = self.app.post('/', data={'username': 'fake_username', 'password': 'fake_password'})
        self.assertEqual(response.status_code, 302)
