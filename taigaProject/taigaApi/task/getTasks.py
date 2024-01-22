import os
import requests
from dotenv import load_dotenv

load_dotenv()


def get_tasks(project_id, auth_token):
    taiga_url = os.getenv('TAIGA_URL')
    task_api_url = f"{taiga_url}/tasks?project={project_id}"

    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json',
    }

    try:
        response = requests.get(task_api_url, headers=headers)
        response.raise_for_status()
        project_info = response.json()
        return project_info

    except requests.exceptions.RequestException as e:
        print(f"Error fetching tasks: {e}")
        return None


def get_closed_tasks(project_id, auth_token):
    tasks = get_tasks(project_id, auth_token)
    if tasks:
        closed_tasks = [
            {
                "subject": task["subject"],
                "created_date": task["created_date"],
                "finished_date": task["finished_date"]

            }
            for task in tasks if task.get("is_closed")
        ]

        return closed_tasks
    else:
        return None


def get_all_tasks(project_id, auth_token):
    tasks = get_tasks(project_id, auth_token)
    if tasks:
        all_tasks = [
            {
                "id": task["id"],
                "created_date": task["created_date"],
                "finished_date": task["finished_date"]
            }
            for task in tasks
        ]

        return all_tasks
    else:
        return None

