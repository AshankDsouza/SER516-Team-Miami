from flask import Flask, jsonify, request 
from taiga import TaigaAPI
import re 
from app import get_project_slug, get_auth_token


# api = TaigaAPI()

# api.auth(
#     username='username',
#     password='pswd'
# )


# new_project = api.projects.get_by_slug('ser516asu-ser516-team-miami')


app = Flask(__name__) 


@app.route('/heartbeat', methods=['GET']) 
def helloworld(): 
	if(request.method == 'GET'): 
		data = {"data": "The app is alive!"} 
		return jsonify(data) 

def get_slug_from_url(url):
    # Assuming the URL format is like: /project/ser516asu-ser516-team-miami/
    match = re.search(r'/project/(.*?)/', url)
    if match:
        return match.group(1)
    else:
        return None

@app.route('/project/<project_id>', methods=['GET'])  
def get_project_details(project_id):
      print("Project id: ", project_id)

      auth = get_auth_token()
      proj = get_project_slug(auth, project_id)

      return jsonify(proj)


# @app.route('/project/<project_id>', methods=['GET']) 
# def get_project_data(project_id): 
#     if request.method == 'GET':
#         project_slug = None
#         #get_slug_from_url(request.url)
#         if project_slug:
#             try:
#                 project = api.projects.get_by_slug(project_slug)
#                 return jsonify(project)
#             except Exception as e:
#                 return jsonify({"error": str(e)})
#         else:
#             return jsonify({"error": "Project slug not found in URL"})


if __name__ == '__main__': 
	app.run(debug=True) 
