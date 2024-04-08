from flask import Flask, request, jsonify
from taigaApi.task.getTasks import (
    get_lead_times_for_tasks,
    get_userstories_for_milestones,
)

app = Flask(__name__)

@app.route("/lead-time-graph", methods=["GET"])
def lead_time_graph():
    project_id = request.form["project_id"]
    sprint_id = request.form["sprint_id"]
    auth_token = request.form["auth_token"]
    lead_times_for_sprint = get_lead_times_for_tasks(project_id, sprint_id, auth_token)
    if auth_token:
        return jsonify({"lead_times_for_sprint": lead_times_for_sprint}), 200


