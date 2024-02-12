from flask import Flask, render_template, request, redirect, url_for, session
import getpass
import json
from datetime import datetime, timedelta
from taigaApi.authenticate import authenticate
from taigaApi.project.getProjectBySlug import get_project_by_slug
from taigaApi.project.getProjectTaskStatusName import get_project_task_status_name
from taigaApi.userStory.getUserStory import get_user_story
from taigaApi.task.getTaskHistory import get_task_history
from taigaApi.task.getTasks import get_closed_tasks, get_all_tasks
from taigaApi.project.getProjectMilestones import get_number_of_milestones
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
        project_slug = request.form['slugInput']
        project_info = get_project_by_slug(project_slug, session['auth_token'])
        session["project_id"] = project_info["id"]
        if session["project_id"] == None:
            return "Wrong slug input. Please try again."
        return redirect('/sprint-selection')

    return render_template('slug-input.html')


@app.route('/sprint-selection', methods=['GET', 'POST'])
def sprint_selection():
    if 'auth_token' not in session: 
        return redirect('/')

    total_sprints = get_number_of_milestones(session["project_id"], session['auth_token'])

    if request.method == 'POST':
        session['sprint_selected'] = request.form.get('selectionOption')
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

    return render_template('metric-selection.html')

@app.route('/burndown-metric-parameter', methods=['GET', 'POST'])
def burndown_metric_parameter():
    if 'auth_token' not in session: 
        return redirect('/')
    
    if request.method == 'POST':
        parameter = request.form.get('parameter')
        return redirect('/burndown-metric_configuration') #just a placeholder

    return render_template('burndown-metric_configuration.html')

