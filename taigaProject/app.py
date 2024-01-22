import getpass
import json
from datetime import datetime, timedelta
from taigaApi.authenticate import authenticate
from taigaApi.project.getProjectBySlug import get_project_by_slug
from taigaApi.project.getProjectTaskStatusName import get_project_task_status_name
from taigaApi.userStory.getUserStory import get_user_story
from taigaApi.task.getTasks import get_closed_tasks, get_all_tasks


def default_encoder(obj):
    if isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%d")


def get_auth_token():
    # taiga_username = input("Enter your Taiga username: ")
    # taiga_password = getpass.getpass("Enter your Taiga password: ")
    taiga_username = "ser515asu"
    taiga_password = "a5uP0l4!"
    auth_token = authenticate(taiga_username, taiga_password)
    return auth_token


def get_project_slug(auth_token):
    # project_slug = input("Enter the Taiga project slug: ")
    project_slug = "amarjeetsingh-test_cassess"
    project_info = get_project_by_slug(project_slug, auth_token)
    task_status_name = get_project_task_status_name(project_info["id"], auth_token)

    project_details = {
        "name": project_info["name"],
        "team_members": [member["full_name"] for member in project_info.get("members", [])],
        "taskboard_column": [status["name"] for status in task_status_name],
    }
    print(json.dumps(project_details, indent=2))
    return project_info["id"]


def get_open_user_stories(project_id, auth_token):
    user_stories = get_user_story(project_id, auth_token)
    open_user_stories = [story for story in user_stories if not story["is_closed"]]

    project_details = {
        "open_user_stories": [
            {
                "name": story["subject"],
                "description": story.get("description", "")
            }
            for story in open_user_stories
        ]
    }
    print(json.dumps(project_details, indent=2))


def get_closed_tasks_per_week(project_id, auth_token):
    closed_tasks = get_closed_tasks(project_id, auth_token)
    task_groups = []

    for task in closed_tasks:
        finished_date = datetime.fromisoformat(task["finished_date"])
        week_start = finished_date - timedelta(days=finished_date.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)

        existing_week = next((week for week in task_groups if week["weekEnding"] == week_end), None)

        if existing_week:
            existing_week["closedTasks"] += 1
        else:
            task_groups.append({"weekEnding": week_end, "closedTasks": 1})

    print(json.dumps(task_groups, indent=2, default=default_encoder))


def get_lead_time(project_id, auth_token):
    user_stories = get_user_story(project_id, auth_token)
    lead_time = 0
    closed_user_story = 0
    for user_story in user_stories:
        if user_story["is_closed"]:
            created_date = datetime.fromisoformat(user_story["created_date"])
            finished_date = datetime.fromisoformat(user_story['finish_date'])
            lead_time += (finished_date - created_date).days
            closed_user_story += 1

    avg_lead_time = lead_time / closed_user_story
    print("Average Lead Time: ", avg_lead_time)


def handle_user_action(project_id, auth_token):
    while True:
        action = input(
            "What do you want to do next?\n"
            "(1) Show open user stories\n"
            "(2) Calculate number of task closed per week metric\n"
            "(3) Calculate average lead time\n"
            "(4) Calculate average cycle time\n"
            "(5) Exit\n"
            "Enter action: "
        )
        if action == "1":
            print("Getting list of all open user stories...")
            get_open_user_stories(project_id, auth_token)

        elif action == "2":
            print("Calculating throughput metric...")
            get_closed_tasks_per_week(project_id, auth_token)

        elif action == "3":
            print("Calculating average lead time...")
            get_lead_time(project_id, auth_token)

        elif action == "4":
            print("Calculating average cycle time...")

        elif action == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter a valid option.")


def main():
    auth_token = get_auth_token()
    if auth_token:
        print("Authentication successful.")
        project_id = get_project_slug(auth_token)

        if project_id:
            handle_user_action(project_id, auth_token)


if __name__ == "__main__":
    main()
