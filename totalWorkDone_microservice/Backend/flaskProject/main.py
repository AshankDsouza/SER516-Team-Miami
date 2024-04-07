from flask import Flask
import json

from utility.totalWorkDone import totalWorkDone

from threading import Thread

app = Flask(__name__)

@app.route("/<project_id>/<sprint_id>/<auth_token>/total-work-done-chart", methods=["GET"])
def totalWrokDone(project_id, sprint_id, auth_token):
    try:
        data_to_plot = totalWorkDone(project_id, sprint_id, auth_token)

        return json.dumps({"data_to_plot": data_to_plot }), 200
    except Exception as e:
        # Handle errors during the API request and print an error message
        print(e)
        return json.dumps({ "msg": "Failed plot sprint data" }), 500
    