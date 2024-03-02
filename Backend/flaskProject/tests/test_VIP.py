from flaskProject.main import app
import unittest
from flask import Flask, request, session
from unittest.mock import patch

class test_calculate_VIP(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()
        app.secret_key = "fake key"

    @patch("flaskProject.main.get_userstories_for_milestones")
    @patch("flaskProject.main.get_business_value_id")
    @patch("flaskProject.main.get_custom_attribute_values")
    @patch("flaskProject.main.get_user_story_business_value_map")
    @patch("flaskProject.main.get_milestones_by_sprint")

    def test(self, fake_get_milestones_by_sprint, fake_get_user_story_business_value_map, fake_get_custom_attribute_values, fake_get_business_value_id, fake_get_userstories_for_milestones):
        fake_get_milestones_by_sprint.return_value = []
        fake_get_user_story_business_value_map.return_value = {}
        fake_get_custom_attribute_values.return_value = {}
        fake_get_business_value_id.return_value = 1
        fake_get_userstories_for_milestones.return_value = []
        with app.test_request_context('/VIPC'):
            with self.app as client:
                response = client.get('/VIPC')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data, [])
                
            

