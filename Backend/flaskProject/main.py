from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import json
from datetime import datetime, timedelta

from taigaApi.authenticate import authenticate
from taigaApi.project.getProjectBySlug import get_project_by_slug
from taigaApi.project.getProjectTaskStatusName import get_project_task_status_name
from taigaApi.userStory.getUserStory import get_user_story
from taigaApi.task.getTaskHistory import calculate_cycle_times_for_tasks
from taigaApi.task.getTasks import get_closed_tasks, get_all_tasks, get_one_closed_task, get_tasks, get_closed_tasks_for_a_sprint
from taigaApi.project.getProjectMilestones import get_number_of_milestones, get_milestone_id
from taigaApi.milestones.getMilestonesForSprint import get_milestones_by_sprint
from taigaApi.task.getTasks import get_lead_times_for_tasks
from taigaApi.customAttributes.getCustomAttributes import get_business_value_data_for_sprint
import secrets
import requests
from threading import Thread

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
        project_slug = request.form['slugInput']
        project_info = get_project_by_slug(project_slug, session['auth_token'])

        if project_info == None:
            return render_template('slug-input.html', error = True)
        session["project_id"] = project_info["id"]
        
        return redirect('/sprint-selection')

    return render_template('slug-input.html')


@app.route('/sprint-selection', methods=['GET', 'POST'])
def sprint_selection():
    if 'auth_token' not in session:
        return redirect('/')

    if 'project_id' not in session:
        return redirect('/slug-input')

    sprintMapping, total_sprints = get_number_of_milestones(session["project_id"], session['auth_token'])

    if request.method == 'POST':
        session['sprint_selected'] = request.form.get('selectionOption')
        # TODO: Bug fix (sprint mapping)
        session['sprint_id'] = sprintMapping[str(len(sprintMapping) - int(request.form.get('selectionOption')) + 1)]
        print("\n\n")
        print(json.dumps(sprintMapping, indent=2))
        print("\n\n")
        return redirect('/metric-selection')

    return render_template('sprint-selection.html', total_sprints = total_sprints)
    
@app.route('/metric-selection', methods=['GET', 'POST'])
def metric_selection():
    if 'auth_token' not in session: 
        return redirect('/')

    if request.method == 'POST':
        session['metric_selected'] = request.form.get('selectionOption')
        if session['metric_selected'] == "burndown":
            return redirect('/burndown-graph')

        elif session['metric_selected'] == 'cycle_time':
            return redirect('/cycle-time-graph')

        elif session['metric_selected'] == "lead_time":
            return redirect('/lead-time-graph')

    return render_template('metric-selection.html')

@app.route('/burndown-graph', methods=['GET'])
def burndown_graph():
    if 'auth_token' not in session: 
        return redirect('/')
    
    if 'sprint_selected' not in session:
        return redirect('/sprint-selection')
    
    if 'metric_selected' not in session:
        return redirect('/metric-selection')
    
    return render_template('burndown-graph.html')


# TODO: Depricated (Endpoint not in use)
@app.route('/burndown-metric-parameter', methods=['GET', 'POST'])
def burndown_metric_parameter():
    if 'auth_token' not in session: 
        return redirect('/')
    
    if request.method == 'POST':
        parameter = request.form.get('workOption')
        if parameter == 'businessValues':
            return redirect('/burndown-bv')
        return redirect('/burndown-metric_configuration')  #just a placeholder

    return render_template('burndown-metric_configuration.html')

# TODO: Depricated (Endpoint not in use)
@app.route('/work-done-chart', methods=['GET'])
def work_done_chart():
    if 'auth_token' not in session: 
        return redirect('/')
    
    auth_token  = session['auth_token']
    taiga_url   = os.getenv('TAIGA_URL')

    print(request.args)

    project_id  = request.args.get('projectid')
    sprint_id   = request.args.get('sprintid')

    if((not project_id) or (not sprint_id)):
        return 'Invalid request!'

    milestones_api_url  = f"{taiga_url}/milestones/{sprint_id}?project={project_id}"
    taks_api_url        = f"{taiga_url}/tasks?project={project_id}"

    # Define headers including the authorization token and content type
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json',
    }

    try:
        # Make a GET request to Taiga API to retrieve user stories
        mailstones_res = requests.get(milestones_api_url, headers=headers)
        mailstones_res.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

        # Extracting information from the mailstones_res
        milestone = mailstones_res.json()

        # Make a GET request to Taiga API to retrieve tasks
        tasks_res = requests.get(taks_api_url, headers=headers)
        tasks_res.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

        # Extracting information from the tasks_res
        tasks = tasks_res.json()

        for user_story in milestone["user_stories"]:
            if user_story["total_points"] == None: 
                continue

        print(json.dumps({ "milestone": milestone, "tasks": tasks }, indent=2))

        return json.dumps(milestone)
    except requests.exceptions.RequestException as e:
        # Handle errors during the API request and print an error message
        print(f"Error fetching project by slug: {e}")
        return redirect('/error')

@app.route('/<user_story>/get-business-value', methods=['GET'])
def get_business_value_by_user_story(user_story):
    if 'auth_token' not in session:
        return redirect('/')
    auth_token  = session['auth_token']
    project_id = session['project_id']
    taiga_url   = os.getenv('TAIGA_URL')
    business_value_id = get_business_value_id(project_id, auth_token)
    business_value_api_url  = f"{taiga_url}/userstories/custom-attributes-values/{user_story}"
    # Define headers including the authorization token and content type
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json',
    }
    try:
        # Make a GET request to Taiga API to retrieve user stories
        response = requests.get(business_value_api_url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        # Extracting information from the response
        business_value_res = response.json()
        if str(business_value_id) not in business_value_res['attributes_values']:
            business_value_res["attributes_values"][str(business_value_id)] = 0
        return business_value_res["attributes_values"][str(business_value_id)]
    except requests.exceptions.RequestException as e:
        # Handle errors during the API request and print an error message
        print(f"Error fetching project by slug: {e}")
        return redirect('/error')
      
@app.route('/lead-time-graph', methods=['GET'])      
def lead_time_graph():
    if 'auth_token' not in session:
        return redirect('/')
    auth_token = session['auth_token']
    project_id = session['project_id']
    sprint_id = session['sprint_id']
    lead_times_for_sprint = get_lead_times_for_tasks(project_id, sprint_id, auth_token)
    return render_template('lead-time-sprint-graph.html', lead_times_for_sprint=lead_times_for_sprint)


#fetch data and calculate cycle time of tasks or user stories selected and display graph.
#This is not average cycle time.
@app.route('/cycle-time-graph', methods=['GET'])
def cycle_time_graph_get():
    if 'auth_token' not in session: 
        return redirect('/')
    #show users all the closed tasks in the selected sprint

    closed_tasks_in_a_spirnt = get_closed_tasks_for_a_sprint(session["project_id"], session["sprint_id"], session["auth_token"])
    session["closed_tasks_in_a_sprint"] = closed_tasks_in_a_spirnt

    in_sprint_ids = [task["ref"] for task in closed_tasks_in_a_spirnt]
    return render_template('CycleTimeGraph.html', closed_tasks = in_sprint_ids)


@app.route('/cycle-time-graph', methods=['POST'])
def cycle_time_graph():
    if 'auth_token' not in session: 
        return redirect('/')
    if request.method == 'POST':
        #The data should be sent by fetch and POST method in JSON format
        closed_tasks_ids = request.json['closed_tasks_ids']

        closed_tasks_selected = []
        if closed_tasks_ids == [0]:
            closed_tasks_selected = session["closed_tasks_in_a_sprint"]
        else:
            closed_tasks_selected = [task for task in session["closed_tasks_in_a_sprint"] if task["ref"] in closed_tasks_ids]

        #fetch data from taiga api
        if (closed_tasks_selected != None):
            return jsonify(calculate_cycle_times_for_tasks(closed_tasks_selected, session['auth_token']))


@app.route('/partial-work-done-chart', methods=['GET'])
def partial_work_done_chart():
    # If user is not log`ged in redirect to login page
    if 'auth_token' not in session: 
        return redirect('/')
    
    # Fetching the auth token from session
    auth_token = session['auth_token']

    if 'project_id' in session:
        project_id = session['project_id']

    if 'sprint_id' in session:
        sprint_id = session['sprint_id']

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
        return redirect('/error')
    
@app.route('/total-work-done-chart', methods=['GET'])
def total_work_done_chart():
    # If user is not log`ged in redirect to login page
    if 'auth_token' not in session: 
        return redirect('/')
    
    # Fetching the auth token from session
    auth_token = session['auth_token']

    # TODO: Bug fix (redirect)
    if 'project_id' in session:
        project_id = session['project_id']

    if 'sprint_id' in session:
        sprint_id = session['sprint_id']

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
        return redirect('/error')
    
@app.route("/burndown-bv")
def render_burndown_bv():
    if "auth_token" not in session:
        return redirect("/")
    return render_template("burndown-bv.html")

@app.route("/burndown-bv-data", methods=["GET", "POST"])
def get_burndown_bv_data():
    if request.method == "GET":
        running_bv_data, ideal_bv_data = get_business_value_data_for_sprint(session['project_id'], session['sprint_id'],
                                                                            session['auth_token'])
        return list((list(running_bv_data.items()), list(ideal_bv_data.items())))

@app.route("/error", methods=["GET"])
def render_error():
    return render_template("error.html")
