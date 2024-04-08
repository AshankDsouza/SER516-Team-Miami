from flask import Flask, request, jsonify

from datetime import datetime, timedelta

from taigaApi.project.getProjectMilestones import (
    get_number_of_milestones,
)

from taigaApi.milestones.getMilestonesForSprint import (
    get_milestones_by_sprint,
)

app = Flask(__name__)


@app.route("/work-auc-data", methods=["GET"])
def get_work_auc_data():
    try:
        sprintMapping, sprints = get_number_of_milestones(
            request.form["project_id"], request.form["auth_token"]
        )

        work_auc_by_sprint_id = {}
        for sprint_id in list(sprintMapping.values()):
            milestone = get_milestones_by_sprint(
                request.form["project_id"], sprint_id, request.form["auth_token"]
            )

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

            start_date = datetime.strptime(
                data_to_plot["sprint_start_date"], "%Y-%m-%d"
            )
            end_date = datetime.strptime(data_to_plot["sprint_end_date"], "%Y-%m-%d")

            data_to_plot["x_axis"] = [
                (start_date + timedelta(days=day)).strftime("%d %b %Y")
                for day in range((end_date - start_date).days + 1)
            ]
            data_to_plot["y_axis"] = [
                i for i in range(0, data_to_plot["total_story_points"] + 20, 20)
            ]

            ideal_graph_points = data_to_plot["total_story_points"]
            avg_comp_story_point = data_to_plot["total_story_points"] / (
                len(data_to_plot["x_axis"]) - 1
            )
            while ideal_graph_points > 0:
                temp = round(ideal_graph_points - avg_comp_story_point, 1)
                if len(data_to_plot["ideal_projection"]) <= 0:
                    data_to_plot["ideal_projection"].append(
                        data_to_plot["total_story_points"]
                    )
                if temp > 0:
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
                    current_processing_date_points = data_to_plot["actual_projection"][
                        index - 1
                    ]
                total_points_completed = 0
                for user_story in milestone["user_stories"]:
                    if (
                        user_story["finish_date"] == None
                        or user_story["total_points"] == None
                    ):
                        continue
                    finish_date = datetime.fromisoformat(
                        user_story["finish_date"]
                    ).strftime("%d %b %Y")

                    if finish_date != current_processing_date:
                        continue
                    total_points_completed = (
                        user_story["total_points"] + total_points_completed
                    )
                data_to_plot["actual_projection"].append(
                    round(current_processing_date_points - total_points_completed, 1)
                )

            actual_value = data_to_plot["actual_projection"]
            ideal_value = data_to_plot["ideal_projection"]
            total_points = data_to_plot["total_story_points"]
            work_auc_delta = []
            for idx in range(len(actual_value)):
                if total_points != 0:
                    work_auc_delta.append(
                        round(
                            abs(
                                (total_points - actual_value[idx]) / total_points
                                - (total_points - ideal_value[idx]) / total_points
                            ),
                            2,
                        )
                    )
                else:
                    work_auc_delta.append(0)

            work_auc_by_sprint_id[sprint_id] = sum(work_auc_delta) * 100

        work_auc_by_sprint_order = []
        for sprint_id in list(sprintMapping.values()):
            work_auc_by_sprint_order.insert(0, work_auc_by_sprint_id[sprint_id])

        sprint_label = []
        for i in range(sprints):
            sprint_label.append("Sprint " + str(i + 1))

        return jsonify(
            {
                "x_axis": sprint_label,
                "work_auc_by_sprint_order": work_auc_by_sprint_order,
            }
        )

    except Exception as e:
        print(e)
        return "Error"
