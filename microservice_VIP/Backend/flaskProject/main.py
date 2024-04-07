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

@app.route("/VIPC", methods=["POST"])
def calculate_VIP():
    if "auth_token" not in session:
        return redirect("/")
    # get all the user stories from the sprint
    user_stories = get_userstories_for_milestones(
        [session["sprint_id"]], session["auth_token"]
    )[
        0
    ]  # it has complete infromation

    # get business value of each user story, and calculate total business value
    get_userstory_ids = lambda: [userstory["id"] for userstory in user_stories]
    userstory_ids = get_userstory_ids()
    business_value_id = get_business_value_id(
        session["project_id"], session["auth_token"]
    )
    custom_attribute_values = get_custom_attribute_values(
        userstory_ids, session["auth_token"]
    )
    ###
    user_story_business_value_map = get_user_story_business_value_map(
        business_value_id, custom_attribute_values
    )
    total_business_value = sum(user_story_business_value_map.values())
    ###

    # get total user stories points

    ####
    total_points = 0
    story_points_map = {}
    story_finish_date_map = {}
    ####

    for story in user_stories:
        if story["total_points"] != None:
            total_points += story["total_points"]
            story_points_map[story["id"]] = story["total_points"]
            story_finish_date_map[story["id"]] = story["finish_date"]

    # get story start dates
    ###
    story_start_date_map = get_user_story_start_date(
        user_stories, session["auth_token"]
    )
    ###

    # get starting date of a sprint
    # get ending date of a sprint "finish_date"
    sprint_data = get_milestones_by_sprint(
        session["project_id"], session["sprint_id"], session["auth_token"]
    )
    sprint_start_date = sprint_data["estimated_start"]
    sprint_start_date = datetime.fromisoformat(sprint_start_date)
    sprint_finish_date = sprint_data["estimated_finish"]
    sprint_finish_date = datetime.fromisoformat(sprint_finish_date)
    # check which user stories is in progress at a given date
    date_list = [
        (sprint_start_date + timedelta(days=day))
        for day in range((sprint_finish_date - sprint_start_date).days + 1)
    ]
    data_points = []
    one_day_points = 0
    one_day_BV = 0
    for date in date_list:
        date = date.replace(tzinfo=None)
        for user_story in user_stories:
            if story_start_date_map[user_story["id"]] == None:
                continue
            start_date = story_start_date_map[user_story["id"]].replace(tzinfo=None)
            if story_finish_date_map[user_story["id"]] != None:
                finish_date = datetime.fromisoformat(
                    story_finish_date_map[user_story["id"]]
                ).replace(tzinfo=None)
            else:
                finish_date = None


            if start_date.date() <= date.date() and (finish_date == None or finish_date.date() > date.date()):

                one_day_points += story_points_map[user_story["id"]]
                one_day_BV += user_story_business_value_map[user_story["id"]]

        data_points.append(
            {
                "date": date.strftime("%d %b %Y"),
                "user_story_points": one_day_points / total_points,
                "BV": one_day_BV / total_business_value,
            }
        )
        one_day_points = 0
        one_day_BV = 0

    return jsonify(data_points)



