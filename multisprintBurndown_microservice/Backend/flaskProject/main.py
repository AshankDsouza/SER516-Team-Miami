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


@app.route("/<project_id>/<auth_token>/multi-sprint-bd", methods=["post"])
def calclateBDConsistency(project_id, auth_token):
    try:
        data_to_plot = {}
        threads = []
        session = request.json

        for key in session["sprint_mapping"].keys():
            sprintId = session["sprint_mapping"][key]
            sprint_key = len(session["sprint_mapping"]) - int(key) + 1
            data_to_plot[sprint_key] = {}

            # partial work done
            thread1 = Thread(target=partialWorkDone, args=(project_id, sprintId, auth_token, data_to_plot, sprint_key))

            # total work done
            thread2 = Thread(target=totalWorkDone, args=(project_id, sprintId, auth_token, data_to_plot, sprint_key))

            # business value
            thread3 = Thread(target=get_business_value_data_for_sprint, args=(project_id, sprintId, auth_token, data_to_plot, sprint_key))

            thread1.start()
            thread2.start()
            thread3.start()
            threads.append(thread1)
            threads.append(thread2)
            threads.append(thread3)

        for thread in threads:
            thread.join()

        return render_template("multi-sprint-bd.html", data_to_plot=data_to_plot)
    except Exception as e:
        # Handle errors during the API request and print an error message
        print(e)
        return json.dumps({ "msg": "Failed plot bd consistency data", "e": e }), 500
    