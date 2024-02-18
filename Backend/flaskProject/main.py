from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import json
from datetime import datetime, timedelta

from taigaApi.authenticate import authenticate
from taigaApi.project.getProjectBySlug import get_project_by_slug
from taigaApi.project.getProjectTaskStatusName import get_project_task_status_name
from taigaApi.userStory.getUserStory import get_user_story
from taigaApi.task.getTaskHistory import get_task_history
from taigaApi.task.getTasks import get_closed_tasks, get_all_tasks, get_one_closed_task, get_closed_tasks_for_a_sprint
from taigaApi.project.getProjectMilestones import get_number_of_milestones, get_milestone_id
from Backend.taigaApi.task.getTasks import get_lead_times_for_tasks

import secrets
import requests


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

    sprintMapping, total_sprints = get_number_of_milestones(session["project_id"], session['auth_token'])

    if request.method == 'POST':
        session['sprint_selected'] = request.form.get('selectionOption')
        session['sprint_id'] = sprintMapping[request.form.get('selectionOption')]
        return redirect('/metric-selection')
    
    return render_template('sprint-selection.html', total_sprints = total_sprints)
    
@app.route('/metric-selection', methods=['GET', 'POST'])
def metric_selection():
    if 'auth_token' not in session: 
        return redirect('/')

    if request.method == 'POST':
        session['metric_selected'] = request.form.get('selectionOption')
        if session['metric_selected'] == "burndown":
            return redirect('/burndown-metric-parameter')

        elif session['metric_selected'] == 'cycle_time':
            return redirect('/cycle-time-graph')

        elif session['metric_selected'] == "lead_time":
            return redirect('/lead-time-graph')


    return render_template('metric-selection.html')

@app.route('/burndown-metric-parameter', methods=['GET', 'POST'])
def burndown_metric_parameter():
    if 'auth_token' not in session: 
        return redirect('/')
    
    if request.method == 'POST':
        parameter = request.form.get('parameter')
        return redirect('/burndown-metric_configuration') #just a placeholder

    return render_template('burndown-metric_configuration.html')



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
        return 'None'

@app.route('/<user_story>/get-business-value', methods=['GET'])
def get_business_value_by_user_story(user_story):
    if 'auth_token' not in session:
        return redirect('/')
    auth_token  = session['auth_token']
    taiga_url   = os.getenv('TAIGA_URL')
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
        return business_value_res["attributes_values"]["40198"]
    except requests.exceptions.RequestException as e:
        # Handle errors during the API request and print an error message
        print(f"Error fetching project by slug: {e}")
        return 'None'
      
@app.route('/lead-time-graph', methods=['GET'])      
def lead_time_graph():
    if 'auth_token' not in session:
        return redirect('/')
    auth_token = session['auth_token']
    project_id = session['project_id']
    sprint_id = session['sprint_id']
    return get_lead_times_for_tasks(project_id, sprint_id, auth_token)


#fetch data and calculate cycle time of tasks or user stories selected and display graph.
#This is not average cycle time.
@app.route('/cycle-time-graph', methods=['GET'])
def cycle_time_graph_get():
    if 'auth_token' not in session: 
        return redirect('/')
    #show users all the closed tasks in the selected sprint
    sprint_name = "Sprint" + session["sprint_selected"]
    sprint_id = get_milestone_id(session["project_id"], session["auth_token"], sprint_name)
    closed_tasks_in_a_spirnt = get_closed_tasks_for_a_sprint(session["project_id"], sprint_id, session["auth_token"])
    in_sprint_ids = [task["ref"] for task in closed_tasks_in_a_spirnt]
    print("closed_tasks_in_a_spirnt: ")
    print(in_sprint_ids)
    return render_template('CycleTimeGraph.html', closed_tasks = in_sprint_ids)

@app.route('/cycle-time-graph', methods=['POST'])
def cycle_time_graph():
    if 'auth_token' not in session: 
        return redirect('/')
    if request.method == 'POST':
        
        #The data should be sent by fetch and POST method in JSON format
        closed_tasks_ids = request.json['closed_tasks_ids']
        sprint_name = "Sprint" + session["sprint_selected"]
        closed_tasks_in_a_spirnt = get_closed_tasks_for_a_sprint(session["project_id"], sprint_name, session["auth_token"])
        #in_sprint_ids = [task["id"] for task in closed_tasks_in_a_spirnt]
        #closed_tasks_ids = [id for id in closed_tasks_ids if id in in_sprint_ids]
        #fetch data from taiga api
        task_id_cycle_time = []
        for task_id in closed_tasks_ids:
            selected_task = get_one_closed_task(task_id, session["project_id"], session['auth_token'])
            if selected_task != None:
                cycle_time, closed_task_number = get_task_history(selected_task, session['auth_token'])
                task_id_cycle_time.append(
                    {
                        "task_id": task_id,
                        "cycle_time": cycle_time,
                    }
                )
        #task_id_cycle_time = json.dumps(task_id_cycle_time)
        #return render_template('CycleTimeGraph.html', task_id_cycle_time = task_id_cycle_time, task = in_sprint_ids)
        return jsonify(task_id_cycle_time)


