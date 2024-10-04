from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3203
HOST = '0.0.0.0'
BOOKING_HOST = 'http://localhost:3201/bookings/'
MOVIES_HOST = 'http://localhost:3200/'

with open('{}/databases/users.json'.format("."), "r") as jsf:
	users = json.load(jsf)["users"]

@app.route("/", methods=['GET'])
def home():
	return "<h1 style='color:blue'>Welcome to the User service!</h1>"

@app.route("/users", methods=['GET'])
def user():
	return make_response(jsonify(users), 200)

@app.route('/users/<userid>', methods=['GET'])
def user_id(userid):
	for u in users:
		if str(u['id']) == str(userid):
			return make_response(jsonify(u), 200)
	return make_response(jsonify({'error': 'bad input parameter'}), 400)

@app.route('/bookings/<userid>', methods=['GET'])
def bookings_user(userid):
	r = requests.get(BOOKING_HOST + str(userid))
	if r.status_code != 200:
		return make_response(jsonify({'error': 'bad input parameter'}), 400)
	return make_response(jsonify(r.json()), 200)

@app.route('/movieinfos/<userid>', methods=['GET'])
def movieinfos_user(userid):
	bookings_request = requests.get(BOOKING_HOST + str(userid))
	movies_request = requests.get(MOVIES_HOST + 'json')
	if bookings_request.status_code != 200:
		return make_response(jsonify({'error': 'bad input parameter'}), 400)
	if movies_request.status_code != 200:
		return make_response(jsonify({'error': 'bad input parameter'}), 400)
	bookings = bookings_request.json()
	movies = movies_request.json()
	ids_in_bookings = [m for b in bookings["dates"] for m in b['movies']]
	res = {"movies": [m for m in movies if m['id'] in ids_in_bookings]}
	return make_response(jsonify(res), 200)



if __name__ == "__main__":
	print("Server running in port %s"%(PORT))
	app.run(host=HOST, port=PORT)
