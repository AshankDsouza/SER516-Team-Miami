import unittest
from unittest.mock import patch, MagicMock
from Backend.flaskProject.main import app

class test_work_auc(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('Backend.flaskProject.main.requests.get')
    def test_work_auc(self, fake_post):
        with self.app.session_transaction() as fake_session:
            fake_session['project_id'] = 'fake_project_id'
            fake_session['auth_token'] = 'fake_auth_token'
        fake_response = MagicMock()
        fake_response.status_code = 200
        fake_response.json.return_value = {'data_point': 'fake_data_point'}
        fake_post.return_value = fake_response
        response = self.app.get('/work-auc-data')
        self.assertEqual(response.status_code, 200)
