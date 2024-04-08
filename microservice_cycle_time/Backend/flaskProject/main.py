import sqlite3
import time
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import json
from datetime import datetime, timedelta

from taigaApi.authenticate import authenticate
from taigaApi.project.getProjectBySlug import get_project_by_slug
from taigaApi.project.getProjectTaskStatusName import get_project_task_status_name
from taigaApi.userStory.getUserStory import get_user_story
from taigaApi.task.getTaskHistory import calculate_cycle_times_for_tasks
from taigaApi.task.getTasks import (
    get_closed_tasks,
    get_all_tasks,
    get_one_closed_task,
    get_tasks,
    get_closed_tasks_for_a_sprint,
    get_lead_times_for_arbitrary_timeframe
)
from taigaApi.project.getProjectMilestones import (
    get_number_of_milestones,
    get_milestone_id,
)

from taigaApi.milestones.getMilestonesForSprint import (
    get_milestones_by_sprint,
    get_milestone_stats_by_sprint,
)
from taigaApi.task.getTasks import (
    get_lead_times_for_tasks,
    get_userstories_for_milestones,
)
from taigaApi.customAttributes.getCustomAttributes import (
    get_business_value_data_for_sprint,
    get_business_value_id,
    get_user_story_business_value_map,
    get_custom_attribute_values,
)
from taigaApi.userStory.getUserStory import get_user_story_start_date

from utility.partialWorkDone import partialWorkDone
from utility.totalWorkDone import totalWorkDone

import secrets
import requests
from threading import Thread

app = Flask(__name__)

@app.route("/cycle_time_calculation", methods=["POST"])
def cycle_time_graph():
        data = request.get_json()
        main_session = data["session"]
        closed_tasks_ids = data["closed_tasks_ids"]

        closed_tasks_selected = []
        if closed_tasks_ids == [0]:
            closed_tasks_selected = main_session["closed_tasks_in_a_sprint"]
        else:
            closed_tasks_selected = [
                task
                for task in main_session["closed_tasks_in_a_sprint"]
                if task["ref"] in closed_tasks_ids
            ]
        if len(closed_tasks_selected) == 0:
            return []


        #Check if the database exists and if the database still valid
        database_name = 'sprint_{}_project_{}.db'.format(main_session["sprint_id"], main_session["project_id"])
        database_path = os.path.join(app.root_path, database_name)

        if os.path.exists(database_path):
            current_time = time.time()
            creation_time = os.path.getctime(database_path)
            difference = (current_time - creation_time) / 60
            if difference <= 30:
                #retrieve data from
                valid_closed_tasks_ids = [task['ref'] for task in closed_tasks_selected]
                valid_ids = ', '.join(map(str, valid_closed_tasks_ids))
                result = []
                conn = sqlite3.connect(database_path)
                c = conn.cursor()
                c.execute('SELECT * FROM cycle_times WHERE id IN ({})'.format(valid_ids))
                entries = c.fetchall()
                result = [{'task_id': entry[0], 'cycle_time': entry[1]} for entry in entries]
                return result

        else:
            #create database
            conn = sqlite3.connect(database_path)
            c = conn.cursor()
            closed_tasks_ids = request.json["closed_tasks_ids"]

            # fetch data from taiga api
            if closed_tasks_selected != None:

                result = calculate_cycle_times_for_tasks(
                    closed_tasks_selected, main_session["auth_token"]
                )
                c.execute('''
                    CREATE TABLE IF NOT EXISTS cycle_times (
                        id TEXT PRIMARY KEY,
                        cycle_time REAL NOT NULL
                        )
                    ''')
                for entry in result:
                    c.execute('INSERT INTO cycle_times (id, cycle_time) VALUES (?, ?)', (entry['task_id'], entry['cycle_time']))
                conn.commit()
                conn.close()
                return result
            conn.commit()
            conn.close()

