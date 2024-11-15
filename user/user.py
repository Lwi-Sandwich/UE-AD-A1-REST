from flask import Flask, render_template, request, jsonify, make_response, send_from_directory
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3203
HOST = '0.0.0.0'
BOOKING_HOST = 'http://localhost:3201/bookings/'
MOVIES_HOST = 'http://localhost:3200/'

# Reading and writing to the json database
with open('{}/databases/users.json'.format("."), "r") as jsf:
	users = json.load(jsf)["users"]

def write(users):
    with open('{}/databases/users.json'.format("."), 'w') as f:
        json.dump({'users':users}, f, indent=4)
@app.route('/users/<userid>', methods=['GET'])

# Swagger documentation
@app.route("/docs", methods=['GET'])
def docs():
	return render_template('swagger_template.html')

@app.route('/spec', methods=['GET'])
def get_spec():
	return send_from_directory('.', 'UE-archi-distribuees-User-1.0.0-resolved.yaml')

# Routes
@app.route("/", methods=['GET'])
def home():
	return "<h1 style='color:blue'>Welcome to the User service!</h1>"

@app.route("/users", methods=['GET'])
def user():
	return make_response(jsonify(users), 200)

@app.route("/users/<userid>", methods=['POST'])
def add_user(userid):
	req = request.get_json()
	if any([k not in req for k in ['id', 'name', 'last_active']]):
		return make_response(jsonify({'error': 'bad input parameter'}), 400)
	for u in users:
		if str(u['id']) == str(userid):
			return make_response(jsonify({'error': 'User ID already exists'}), 409)
	users.append(req)
	write(users)
	res = make_response(jsonify({"message":"user added"}),200)
	return res

@app.route('/users/<userid>', methods=['DELETE'])
def delete_user(userid):
    for u in users:
        if str(u['id']) == str(userid):
            users.remove(u)
            write(users)
            return make_response(jsonify(u), 200)
    return make_response(jsonify({'error': 'User not found'}), 404)

@app.route('/users/<userid>', methods=['GET'])
def user_id(userid):
	for u in users:
		if str(u['id']) == str(userid):
			return make_response(jsonify(u), 200)
	return make_response(jsonify({'error': 'not found'}), 404)

@app.route('/bookings/<userid>', methods=['GET'])
def bookings_user(userid):
	r = requests.get(BOOKING_HOST + str(userid))
	if r.status_code != 200:
		return make_response(jsonify({'error': f'booking failed with status code {r.status_code}'}), r.status_code)
	return make_response(jsonify(r.json()), 200)

@app.route('/movieinfos/<userid>', methods=['GET'])
def movieinfos_user(userid):
	bookings_request = requests.get(BOOKING_HOST + str(userid))
	movies_request = requests.get(MOVIES_HOST + 'json')
	if bookings_request.status_code != 200:
		return make_response(jsonify({'error': f'booking failed with status code {bookings_request.status_code}'}), bookings_request.status_code)
	if movies_request.status_code != 200:
		return make_response(jsonify({'error': f'movies failed with status code {movies_request.status_code}'}), movies_request.status_code)
	bookings = bookings_request.json()
	movies = movies_request.json()
	# All the movie ids in the user's bookings
	ids_in_bookings = [m for b in bookings["dates"] for m in b['movies']]
	# Filtering the movies to only include the ones in the user
	res = {"movies": [m for m in movies if m['id'] in ids_in_bookings]}
	return make_response(jsonify(res), 200)

@app.route("/bookings/<userid>", methods=['POST'])
def add_booking(userid):
	# the booking service will do all of the job
	req = request.get_json()
	r = requests.post(BOOKING_HOST + str(userid), json=req)
	if r.status_code != 200:
		return make_response(jsonify({"error": f"booking failed with status code {r.status_code}"}), r.status_code)
	return make_response(jsonify(r.json()), 200)


if __name__ == "__main__":
	print("Server running in port %s"%(PORT))
	app.run(host=HOST, port=PORT)
