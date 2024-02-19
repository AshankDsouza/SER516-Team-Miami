import unittest
from main import app

class TestMetricSelection(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_get_request_without_auth_token(self):
        response = self.app.get('/metric-selection')
        self.assertEqual(response.status_code, 302) 

    def test_post_request_with_burndown_selected(self):
        response = self.app.post('/metric-selection', data={'selectionOption': 'burndown'})
        self.assertEqual(response.status_code, 302)  
        self.assertTrue(response.location.endswith('/burndown-metric-parameter'))

    def test_post_request_with_cycle_time_selected(self):
        response = self.app.post('/metric-selection', data={'selectionOption': 'cycle_time'})
        self.assertEqual(response.status_code, 302)  
        self.assertTrue(response.location.endswith('/cycle-time-graph'))

    def test_post_request_with_lead_time_selected(self):
        response = self.app.post('/metric-selection', data={'selectionOption': 'lead_time'})
        self.assertEqual(response.status_code, 302)  
        self.assertTrue(response.location.endswith('/lead-time-graph'))

    def test_post_request_with_invalid_option_selected(self):
        response = self.app.post('/metric-selection', data={'selectionOption': 'invalid_option'})
        self.assertEqual(response.status_code, 200)  

if __name__ == '__main__':
    unittest.main()
