from flask import Flask, jsonify, request 

app = Flask(__name__) 


@app.route('/heartbeat', methods=['GET']) 
def helloworld(): 
	if(request.method == 'GET'): 
		data = {"data": "The app is alive!"} 
		return jsonify(data) 


if __name__ == '__main__': 
	app.run(debug=True) 
