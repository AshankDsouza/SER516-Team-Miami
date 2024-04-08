import unittest
from unittest.mock import patch, MagicMock
from Backend.flaskProject.main import app

class PartialWorkDoneTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('Backend.flaskProject.main.requests.get')
    def test_bd(self, fake_post):
        with self.app.session_transaction() as fake_session:
            fake_session['auth_token'] = 'fake_auth_token'
        fake_response = MagicMock()
        fake_response.status_code = 200
        fake_response.json.return_value = {'data_to_plot': 'fake_data_to_plot'}
        fake_post.return_value = fake_response
        response = self.app.get('/multi-sprint-bd')
        self.assertEqual(response.status_code, 200)