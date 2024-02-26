import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Function to retrieve user stories for a specific project from the Taiga API
def get_user_story(project_id, auth_token):

    # Get Taiga API URL from environment variables
    taiga_url = os.getenv('TAIGA_URL')

    # Construct the URL for the user stories API endpoint for the specified project
    user_story_api_url = f"{taiga_url}/userstories?project={project_id}"

    # Define headers including the authorization token and content type
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json',
    }

    try:

        # Make a GET request to Taiga API to retrieve user stories
        response = requests.get(user_story_api_url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

        # Extract and return the user stories information from the response
        project_info = response.json()
        return project_info

    except requests.exceptions.RequestException as e:

        # Handle errors during the API request and print an error message
        print(f"Error fetching project by slug: {e}")
        return None

# Filter out the user stories that are in progress
def get_in_progress_user_stories(project_id, auth_token):
    user_stories = get_user_story(project_id, auth_token)
    in_progress_stories = []
    for story in user_stories:
        if story["status_extra_info"]["name"] == "In progress":
            in_progress_stories.append(story)
    return in_progress_stories

# get business value custom field id
    
# get business value for each user story: user story id, BV id#