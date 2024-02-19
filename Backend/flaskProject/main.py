from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import json
from datetime import datetime, timedelta

from taigaApi.authenticate import authenticate
from taigaApi.project.getProjectBySlug import get_project_by_slug
from taigaApi.project.getProjectTaskStatusName import get_project_task_status_name
from taigaApi.userStory.getUserStory import get_user_story
from taigaApi.task.getTaskHistory import get_task_history
from taigaApi.task.getTasks import get_closed_tasks, get_all_tasks, get_one_closed_task, get_tasks, get_closed_tasks_for_a_sprint
from taigaApi.project.getProjectMilestones import get_number_of_milestones, get_milestone_id
from taigaApi.milestones.getMilestonesForSprint import get_milestones_by_sprint
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
        parameter = request.form.get('workOption')
        if parameter == 'businessValues':
            return redirect('/burndown-bv')
        return redirect('/burndown-metric_configuration')  #just a placeholder

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
        if "40198" not in business_value_res['attributes_values']:
            business_value_res["attributes_values"]["40198"] = 0
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
    lead_times_for_sprint = get_lead_times_for_tasks(project_id, sprint_id, auth_token)
    return render_template('lead-time-sprint-graph.html', lead_times_for_sprint=lead_times_for_sprint)


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
                task_finished_date = datetime.strptime(task["finished_date"], '%Y-%m-%dT%H:%M:%S.%fZ').strftime("%d %b %Y")

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
                if(user_story["finish_date"] == None):
                    continue

                finish_date = datetime.strptime(user_story["finish_date"], '%Y-%m-%dT%H:%M:%S.%fZ').strftime("%d %b %Y")
                    
                if(finish_date != current_processing_date):
                    continue

                print("US completed: ", round(current_processing_date_points - user_story["total_points"], 1))
                total_points_completed = user_story["total_points"] + total_points_completed

            data_to_plot["actual_projection"].append(round(current_processing_date_points - total_points_completed, 1))

        return json.dumps(data_to_plot)
    except Exception as e:
        # Handle errors during the API request and print an error message
        print(e)
        return 'None'
    
@app.route("/burndown-bv")
def render_burndown_bv():
    if "auth_token" not in session:
        return redirect("/")
    return render_template("burndown-bv.html")

@app.route("/burndown-bv-data", methods=["GET", "POST"])
def get_burndown_bv_data():
    if request.method == "GET":
        # get all user stories data
        user_stories = get_user_story(session["project_id"], session["auth_token"])
        # use each user stories id to get bv and check if done
        bv_per_date = [0] * 21
        for idx, val in enumerate(user_stories):
            ## Sprint1 filter
            if val["milestone_name"] == "Sprint1":
                bv = int(get_business_value_by_user_story(val["id"]))
                if val["status_extra_info"]["name"] == "Done":
                    ## Jan filter
                    if val["finish_date"][5:7] == "01":
                        ## convert date to index
                        bv_per_date[int(val["finish_date"][8:10]) - 29] += bv
                    ## Feb filter
                    if val["finish_date"][5:7] == "02":
                        bv_per_date[int(val["finish_date"][8:10]) + 2] += bv
        # calc bv accumulation
        bv_accumulation = 0
        is_accumulation = False
        for idx, val in enumerate(bv_per_date):
            if val != 0:
                bv_accumulation += val
                is_accumulation = True
            if val == 0 and is_accumulation == True:
                bv_per_date[idx] = bv_accumulation
        return bv_per_date