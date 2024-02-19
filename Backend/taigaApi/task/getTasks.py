import os
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from a .env file
load_dotenv()


# Function to retrieve tasks for a specific project from the Taiga API
def get_tasks(project_id, auth_token):

    # Get Taiga API URL from environment variables
    taiga_url = os.getenv('TAIGA_URL')

    # Construct the URL for the tasks API endpoint for the specified project
    task_api_url = f"{taiga_url}/tasks?project={project_id}"

    # Define headers including the authorization token and content type
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json',
    }

    try:

        # Make a GET request to Taiga API to retrieve tasks
        response = requests.get(task_api_url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

        # Extract and return the tasks information from the response
        project_info = response.json()
        return project_info

    except requests.exceptions.RequestException as e:

        # Handle errors during the API request and print an error message
        print(f"Error fetching tasks: {e}")
        return None


# Function to retrieve closed tasks for a specific project from the Taiga API
def get_closed_tasks(project_id, auth_token):

    # Call the get_tasks function to retrieve all tasks for the project
    tasks = get_tasks(project_id, auth_token)
    if tasks:

        # Filter tasks to include only closed tasks and format the result
        closed_tasks = [
            {
                "id": task["id"],
                "subject": task["subject"],
                "created_date": task["created_date"],
                "finished_date": task["finished_date"],
                "ref": task["ref"]
            }
            for task in tasks if task.get("is_closed")
        ]

        return closed_tasks
    else:
        return None

def get_closed_tasks_for_a_sprint(project_id, sprint_id, auth_token):

    # Call the get_tasks function to retrieve all tasks for the project
    tasks = get_tasks(project_id, auth_token)
    if tasks:

        # Filter tasks to include only closed tasks and format the result
        closed_tasks = [
            {
                "id": task["id"],
                "subject": task["subject"],
                "created_date": task["created_date"],
                "finished_date": task["finished_date"]
            }
            for task in tasks if task.get("is_closed") and task['milestone'] == sprint_id
        ]

        return closed_tasks
    else:
        return None


# Function to retrieve all tasks for a specific project from the Taiga API
def get_all_tasks(project_id, auth_token):

    # Call the get_tasks function to retrieve all tasks for the project
    tasks = get_tasks(project_id, auth_token)
    if tasks:

        # Format all tasks and return the result
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
    
# Function to retrieve a closed task by ID
def get_one_closed_task(task_id, project_id, auth_token):
    # to get all the tasks
    closed_tasks = get_closed_tasks(project_id, auth_token)
    if closed_tasks:
        #Find the task with the given ID in closed tasks
        for task in closed_tasks:
           
            if task["ref"] == task_id:
                result = [task] #get_task_history(taks, auth_token) require a list of tasks
                return result
    return None


def get_closed_tasks_for_a_sprint(project_id, sprint_id, auth_token):

    # Call the get_tasks function to retrieve all tasks for the project
    tasks = get_tasks(project_id, auth_token)
    if tasks:

        # Filter tasks to include only closed tasks and format the result
        closed_tasks = [
            {
                "id": task["id"],
                "subject": task["subject"],
                "created_date": task["created_date"],
                "finished_date": task["finished_date"],
                "ref": task["ref"]
            }
            for task in tasks if task.get("is_closed") and task['milestone'] == sprint_id
        ]

        return closed_tasks
    else:
        return None         



    


def get_lead_times_for_tasks(project_id, sprint_id, auth_token):
    tasks = get_closed_tasks_for_a_sprint(project_id, sprint_id, auth_token)
    taskList = []
    for task in tasks:
        created_date = datetime.fromisoformat(task["created_date"])
        finished_date = datetime.fromisoformat(task['finished_date'])
        temp = dict(task)
        temp['lead_time'] = round((finished_date - created_date).days + (finished_date - created_date).seconds/86400, 2)
        taskList.append(temp)
    taskList.sort(key = lambda x : datetime.fromisoformat(x['finished_date']))
    for task in taskList:
        task['created_date'] = datetime.strftime(datetime.fromisoformat(task['created_date']), '%d %b %y')
        task['finished_date'] = datetime.strftime(datetime.fromisoformat(task['finished_date']), '%d %b %y')
    return taskList


