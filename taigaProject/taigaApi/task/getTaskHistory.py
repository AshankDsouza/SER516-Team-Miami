import os
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()


def get_task_history(tasks, auth_token):
    taiga_url = os.getenv('TAIGA_URL')
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json',
    }

    cycle_time = 0
    closed_tasks = 0
    for task in tasks:
        task_history_url = f"{taiga_url}/history/task/{task['id']}"
        finished_date = task["finished_date"]
        try:
            response = requests.get(task_history_url, headers=headers)
            response.raise_for_status()
            history_data = response.json()
            in_progress_date = extract_new_to_in_progress_date(history_data)
            finished_date = datetime.fromisoformat(finished_date[:-1])
            if in_progress_date:
                in_progress_date = datetime.fromisoformat(str(in_progress_date)[:-6])
                cycle_time += (finished_date - in_progress_date).days
                closed_tasks += 1

        except requests.exceptions.RequestException as e:
            print(f"Error fetching project by slug: {e}")

    return [cycle_time, closed_tasks]


def extract_new_to_in_progress_date(history_data):
    for event in history_data:
        values_diff = event.get("values_diff", {})
        if "status" in values_diff and values_diff["status"] == ["New", "In progress"]:
            created_at = datetime.fromisoformat(event["created_at"])
            return created_at
    return None
