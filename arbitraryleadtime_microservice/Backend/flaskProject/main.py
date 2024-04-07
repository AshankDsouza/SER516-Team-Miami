from flask import Flask, request, jsonify
from taigaApi.task.getTasks import (
    get_lead_times_for_arbitrary_timeframe
)

app = Flask(__name__)

@app.route("/arbitrary-lead-time-data", methods=["GET"])
def arbitrary_lead_time():
    project_id = request.form["project_id"]
    auth_token = request.form["auth_token"]
    start_date = request.form["start_date"]
    end_date = request.form["end_date"]
    lead_times_for_timeframe = get_lead_times_for_arbitrary_timeframe(project_id=project_id, start_time=start_date, end_time=end_date, auth_token=auth_token)
    if auth_token:
        return jsonify({"lead_times_for_timeframe": lead_times_for_timeframe}), 200


