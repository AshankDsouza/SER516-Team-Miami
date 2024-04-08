from flask import Flask, request

from taigaApi.customAttributes.getCustomAttributes import (
    get_business_value_data_for_sprint,
)

app = Flask(__name__)


@app.route("/burndown-bv-data", methods=["GET"])
def get_burndown_bv_data():
    try:
        running_bv_data, ideal_bv_data = get_business_value_data_for_sprint(
            request.form["project_id"],
            request.form["sprint_id"],
            request.form["auth_token"],
        )
        return list((list(running_bv_data.items()), list(ideal_bv_data.items())))

    except Exception as e:
        print(e)
        return "Error"
