from main import app
import unittest
from unittest.mock import patch

class TestSlugInput(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()
        app.secret_key = "fake_key"

    @patch('flaskProject.main.get_project_by_slug')
    @patch('flaskProject.main.request')
    @patch('flaskProject.main.session', {'auth_token': 'fake_auth_token'})
    def test_slug_input_post_success(self, mock_session, mock_request, mock_get_project_by_slug):
        mock_request.method = 'POST'
        mock_request.form = {'slugInput': 'test_slug'}
        mock_get_project_by_slug.return_value = {'id': 'fake_project_id'}

        with app.test_request_context('/'):
            with self.app as client:
                response = client.post('/')
                self.assertEqual(response.status_code, 302) 
                self.assertEqual(mock_session['project_id'], 'fake_project_id')

    @patch('flaskProject.main.get_project_by_slug')
    @patch('flaskProject.main.request')
    @patch('flaskProject.main.session', {'auth_token': 'fake_auth_token'})
    def test_slug_input_post_failure(self, mock_session, mock_request, mock_get_project_by_slug):
        mock_request.method = 'POST'
        mock_request.form = {'slugInput': 'invalid_slug'}
        mock_get_project_by_slug.return_value = None

        with app.test_request_context('/'):
            with self.app as client:
                response = client.post('/')
                self.assertEqual(response.status_code, 200)  
                self.assertTrue(mock_get_project_by_slug.called)  
                self.assertIn('error', response.get_data(as_text=True))  

    @patch('flaskProject.main.session', {})
    def test_slug_input_no_auth_token(self, mock_session):
        with app.test_request_context('/'):
            with self.app as client:
                response = client.post('/')
                self.assertEqual(response.status_code, 302)  
                self.assertEqual(response.location, 'http://localhost/') 

if __name__ == '__main__':
    unittest.main()
