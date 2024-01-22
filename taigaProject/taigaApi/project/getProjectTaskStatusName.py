import os
import requests
from dotenv import load_dotenv

load_dotenv()


def get_project_task_status_name(project_id, auth_token):
    taiga_url = os.getenv('TAIGA_URL')
    project_task_api_url = f"{taiga_url}/task-statuses?project={project_id}"

    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json',
    }

    try:
        response = requests.get(project_task_api_url, headers=headers)
        response.raise_for_status()
        project_info = response.json()
        return project_info

    except requests.exceptions.RequestException as e:
        print(f"Error fetching project by slug: {e}")
        return None
