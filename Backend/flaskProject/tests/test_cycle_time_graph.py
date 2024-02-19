import unittest
from unittest.mock import patch, MagicMock
from flask import session
from main import app

class TestCycleTimeGraph(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    @patch('main.get_closed_tasks_for_a_sprint')
    @patch('main.get_one_closed_task')
    @patch('main.request')
    def test_cycle_time_graph_success(self, mock_request, mock_get_one_closed_task, mock_get_closed_tasks_for_a_sprint):
        mock_request.method = 'POST'
        mock_request.json = MagicMock(return_value={'closed_tasks_ids': ['1', '2']})
        session['auth_token'] = 'fake_auth_token'
        session['project_id'] = 'fake_project_id'
        session['sprint_selected'] = '1'

        mock_get_closed_tasks_for_a_sprint.return_value = [{'id': '1'}, {'id': '2'}]
        mock_get_one_closed_task.side_effect = [({'task_id': '1', 'cycle_time': 10}, 'closed_task_number1'), ({'task_id': '2', 'cycle_time': 20}, 'closed_task_number2')]

        response = self.app.post('/cycle-time-graph')

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['task_id'], '1')
        self.assertEqual(data[0]['cycle_time'], 10)
        self.assertEqual(data[1]['task_id'], '2')
        self.assertEqual(data[1]['cycle_time'], 20)

    @patch('main.request')
    def test_cycle_time_graph_no_auth_token(self, mock_request):
        mock_request.method = 'POST'
        session.pop('auth_token', None)

        response = self.app.post('/cycle-time-graph')

        self.assertEqual(response.status_code, 302) 
        self.assertEqual(response.location, 'http://localhost/') 

if __name__ == '__main__':
    unittest.main()
