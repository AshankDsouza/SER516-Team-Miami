from main import app
import unittest
from flask import Flask, request, session
from unittest.mock import patch
import json

class testLogin(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()
        app.secret_key = "fake_key"

    @patch('main.get_one_closed_task')
    @patch('main.get_task_history')
    def test_cycle_time_graph(self, fake_get_task_history, fake_get_one_closed_task):
        #mock data
        fake_get_one_closed_task.return_value = [
            {
                "id": 1,
                "subject": "fake_task",
                "created_date": "2021-01-01",
                "finished_date": "2021-01-10"
            }
        ]
        fake_get_task_history.return_value = (9, 1)
        with app.test_request_context('/cycle-time-graph'):
            with self.app as client:
                session['auth_token'] = "fake_auth_token"
                session['project_id'] = 'fake_project_id'
                response = client.post('/cycle-time-graph', json={'closed_task_id': [1] })
                self.assertEqual(response.status_code, 200)

                expected_result = [ {
                    "task_id": 1,
                    "cycle_time": 9,
                }]
                self.assertEqual(json.loads(response.data), expected_result)

