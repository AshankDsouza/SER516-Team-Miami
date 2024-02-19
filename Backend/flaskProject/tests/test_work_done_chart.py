from Backend.flaskProject.main import app
import unittest
from flask import session
from unittest.mock import patch
import json

class TestWorkDoneChart(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()
        app.secret_key = "fake_key"

    @patch('main.requests.get')  
    def test_work_done_chart(self, mock_get):
        
        mock_get.side_effect = [
            
            unittest.mock.Mock(status_code=200, json=lambda: {
                "user_stories": [
                    {"total_points": 5},
                    {"total_points": None},
                    {"total_points": 10}
                ]
            }),
            
            unittest.mock.Mock(status_code=200, json=lambda: [
                {"id": 1, "subject": "Task 1", "status": 1},
                {"id": 2, "subject": "Task 2", "status": 2},
                {"id": 3, "subject": "Task 3", "status": 3}
            ])
        ]

        
        with app.test_request_context('/work-done-chart?projectid=1&sprintid=1'):
            session['auth_token'] = "fake_auth_token"
            session['project_id'] = 'fake_project_id'

            
            response = self.app.get('/work-done-chart')

            
            self.assertEqual(response.status_code, 200)

            
            expected_result = {
                "user_stories": [{"total_points": 5}, {"total_points": 10}],
                "tasks": [
                    {"id": 1, "subject": "Task 1", "status": 1},
                    {"id": 2, "subject": "Task 2", "status": 2},
                    {"id": 3, "subject": "Task 3", "status": 3}
                ]
            }
            self.assertEqual(json.loads(response.data), expected_result)

if __name__ == '__main__':
    unittest.main()
