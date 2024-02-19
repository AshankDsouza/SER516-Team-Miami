from flask import Flask, render_template, request, redirect, url_for, session
import os
import json
from datetime import datetime, timedelta
from taigaApi.authenticate import authenticate
from taigaApi.project.getProjectBySlug import get_project_by_slug
from taigaApi.project.getProjectTaskStatusName import get_project_task_status_name
from taigaApi.userStory.getUserStory import get_user_story
from taigaApi.task.getTaskHistory import get_task_history
from taigaApi.task.getTasks import get_closed_tasks, get_all_tasks, get_tasks
from taigaApi.milestones.getMilestonesForSprint import get_milestones_by_sprint
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

@app.route('/', methods=['GET', 'POST'])
def loginPage():    
    if 'auth_token' in session: 
        return redirect('/slug-input')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        auth_token = authenticate(username, password)
        if auth_token:
            session['auth_token'] = auth_token
            return redirect('/slug-input')
        else:
            session['auth_token'] = None
            return render_template('login2.html', error = True)
        
    return render_template('login2.html', error = False)

@app.route('/logout', methods=['GET'])
def log_out():
    if 'auth_token' in session:
        del session['auth_token']

    return redirect('/')

@app.route('/slug-input', methods=['GET', 'POST'])
def slug_input():
    if 'auth_token' not in session: 
        return redirect('/')

    if request.method == 'POST':
        print('Take slug input')

    return render_template('slug-input.html')

@app.route('/<project_id>/<sprint_id>/partial-work-done-chart', methods=['GET'])
def partial_work_done_chart(project_id, sprint_id):
    # If user is not log`ged in redirect to login page
    if 'auth_token' not in session: 
        return redirect('/')
    
    # Fetching the auth token from session
    auth_token = session['auth_token']

    # Throwing error if the user has submitted project_id or sprint_id
    if((not project_id) or (not sprint_id)):
        return 'Invalid request!'

    try:
        # Fetching milestones / usertories from taiga endpoint
        milestone = get_milestones_by_sprint(project_id, sprint_id, auth_token)

        # Fetching tasks from taiga endpoint
        tasks = get_tasks(project_id, auth_token)

        # Data required to plot is stored here
        processing_user_stories = {}

        data_to_plot = { 
            "total_story_points": 0,
            "x_axis": [],
            "y_axis": [],
            "ideal_projection": [],
            "actual_projection": [],
            "sprint_start_date": milestone["estimated_start"],
            "sprint_end_date": milestone["estimated_finish"],
        }

        for user_story in milestone["user_stories"]:
            if user_story["total_points"] == None: 
                continue

            processing_user_stories[user_story["id"]] = {
                "points": int(user_story["total_points"]),
                "created_date": user_story["created_date"],
                "finish_date": user_story["finish_date"],
                "tasks": []
            }
            data_to_plot["total_story_points"] += int(user_story["total_points"])
            
        start_date  = datetime.strptime(data_to_plot["sprint_start_date"], '%Y-%m-%d')
        end_date    = datetime.strptime(data_to_plot["sprint_end_date"], '%Y-%m-%d')

        data_to_plot["x_axis"] = [(start_date + timedelta(days=day)).strftime("%d %b %Y") for day in range((end_date - start_date).days + 1)]
        data_to_plot["y_axis"] = [i for i in range(0, data_to_plot["total_story_points"] + 20, 10)]

        ideal_graph_points = data_to_plot["total_story_points"]
        avg_comp_story_point = data_to_plot["total_story_points"]/(len(data_to_plot["x_axis"]) - 1)

        while ideal_graph_points > 0:
            temp = round(ideal_graph_points - avg_comp_story_point, 1)
            
            if(len(data_to_plot["ideal_projection"]) <= 0):
                data_to_plot["ideal_projection"].append(data_to_plot["total_story_points"])

            if(temp > 0):
                data_to_plot["ideal_projection"].append(temp)
            else:
                data_to_plot["ideal_projection"].append(0)

            ideal_graph_points = temp

        for task in tasks:
            if(task["user_story"] not in processing_user_stories):
                continue

            task_finished_date = None
            if(task["status_extra_info"]["is_closed"]): 
                task_finished_date = datetime.fromisoformat(task["finished_date"]).strftime("%d %b %Y")

            processing_user_stories[task["user_story"]]["tasks"].append({
                "closed": task["status_extra_info"]["is_closed"],
                "finished_date": task_finished_date 
            })

        for index in range(0, len(data_to_plot["x_axis"])):
            current_processing_date = data_to_plot["x_axis"][index]
            current_processing_date_points = 0

            if index <= 0:
                current_processing_date_points = data_to_plot["total_story_points"]
            else:
                current_processing_date_points = data_to_plot["actual_projection"][index - 1]

            for user_story_id in processing_user_stories:
                user_story = processing_user_stories[user_story_id]
                task_count = len(user_story["tasks"])

                if(task_count <= 0):
                    continue

                task_points = user_story["points"]/task_count

                for task in user_story["tasks"]:
                    if(not task["closed"] or task["finished_date"] != current_processing_date):
                        continue
                    
                    current_processing_date_points = current_processing_date_points - task_points

            data_to_plot["actual_projection"].append(round(current_processing_date_points, 1))

        return json.dumps(data_to_plot)
    except Exception as e:
        # Handle errors during the API request and print an error message
        print(e)
        return 'None'
    
@app.route('/<project_id>/<sprint_id>/total-work-done-chart', methods=['GET'])
def total_work_done_chart(project_id, sprint_id):
    # If user is not log`ged in redirect to login page
    if 'auth_token' not in session: 
        return redirect('/')
    
    # Fetching the auth token from session
    auth_token = session['auth_token']

    # Throwing error if the user has submitted project_id or sprint_id
    if((not project_id) or (not sprint_id)):
        return 'Invalid request!'

    try:
        # Fetching milestones / usertories from taiga endpoint
        milestone = get_milestones_by_sprint(project_id, sprint_id, auth_token)

        # Data required to plot is stored here
        data_to_plot = { 
            "total_story_points": 0,
            "x_axis": [],
            "y_axis": [],
            "ideal_projection": [],
            "actual_projection": [],
            "sprint_start_date": milestone["estimated_start"],
            "sprint_end_date": milestone["estimated_finish"],
        }

        for user_story in milestone["user_stories"]:
            if user_story["total_points"] == None: 
                continue

            data_to_plot["total_story_points"] += int(user_story["total_points"])
            
        start_date  = datetime.strptime(data_to_plot["sprint_start_date"], '%Y-%m-%d')
        end_date    = datetime.strptime(data_to_plot["sprint_end_date"], '%Y-%m-%d')

        data_to_plot["x_axis"] = [(start_date + timedelta(days=day)).strftime("%d %b %Y") for day in range((end_date - start_date).days + 1)]
        data_to_plot["y_axis"] = [i for i in range(0, data_to_plot["total_story_points"] + 20, 20)]

        ideal_graph_points = data_to_plot["total_story_points"]
        avg_comp_story_point = data_to_plot["total_story_points"]/(len(data_to_plot["x_axis"]) - 1)

        while ideal_graph_points > 0:
            temp = round(ideal_graph_points - avg_comp_story_point, 1)
            
            if(len(data_to_plot["ideal_projection"]) <= 0):
                data_to_plot["ideal_projection"].append(data_to_plot["total_story_points"])

            if(temp > 0):
                data_to_plot["ideal_projection"].append(temp)
            else:
                data_to_plot["ideal_projection"].append(0)

            ideal_graph_points = temp

        for index in range(0, len(data_to_plot["x_axis"])):
            current_processing_date = data_to_plot["x_axis"][index]
            current_processing_date_points = 0

            if index <= 0:
                current_processing_date_points = data_to_plot["total_story_points"]
            else:
                current_processing_date_points = data_to_plot["actual_projection"][index - 1]

            total_points_completed = 0
            for user_story in milestone["user_stories"]:
                if(user_story["finish_date"] == None or user_story["total_points"] == None):
                    continue

                finish_date = datetime.fromisoformat(user_story["finish_date"]).strftime("%d %b %Y")
                    
                if(finish_date != current_processing_date):
                    continue

                total_points_completed = user_story["total_points"] + total_points_completed

            data_to_plot["actual_projection"].append(round(current_processing_date_points - total_points_completed, 1))

        return json.dumps(data_to_plot)
    except Exception as e:
        # Handle errors during the API request and print an error message
        print(e)
        return 'None'
    