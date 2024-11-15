from flask import Flask, render_template, request, jsonify, make_response, send_from_directory
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3201
HOST = '0.0.0.0'
TIMES_HOST = 'http://localhost:3202/showmovies/'

# Reading and writing to the json database
with open('{}/databases/bookings.json'.format("."), "r") as jsf:
	bookings = json.load(jsf)["bookings"]

def write(bookings):
	with open('{}/databases/bookings.json'.format("."), 'w') as f:
		json.dump({'bookings':bookings}, f, indent=4)

# Swagger documentation
@app.route("/docs", methods=['GET'])
def docs():
	return render_template('swagger_template.html')

@app.route('/spec', methods=['GET'])
def get_spec():
	return send_from_directory('.', 'UE-archi-distribuees-Booking-1.0.0-resolved.yaml')

# Routes
@app.route("/", methods=['GET'])
def home():
	return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"

@app.route("/bookings", methods=['GET'])
def get_all():
	return make_response(jsonify(bookings), 200)

@app.route('/bookings/<userid>', methods=['GET'])
def bookings_user(userid):
	for b in bookings:
		if str(b['userid']) == str(userid):
			return make_response(jsonify(b), 200)
	return make_response(jsonify({'error': 'user not found'}), 404)

@app.route('/bookings/<userid>', methods=['POST'])
def add_booking(userid):
	req = request.get_json()
	# Check if the date is available
	g = requests.get(TIMES_HOST + str(req['date']))
	if g.status_code != 200:
		return make_response({'error': f'showtime failed with status code {g.status_code}'}, g.status_code)
	get = json.loads(g.content)
	if req['movieid'] not in get['movies']:
		return make_response(jsonify({'error': 'This movie isn\'t planned for this date'}), 409)
	# We need to check if the user already has a booking list
	booking = None
	for b in bookings:
		if str(b['userid']) == str(userid):
			booking = b
	if booking == None:
		booking = {"userid": str(userid), "dates": []}
		bookings.append(booking)
	need_new = True
	# Check if the date already exists in the booking list
	for d in booking["dates"]:
		if d["date"] == req["date"]:
			if any([m == req["movieid"] for m in d["movies"]]):
				return make_response(jsonify({'error': 'booking already exists'}), 409)
			d["movies"].append(req["movieid"])
			need_new = False
	if need_new:
		booking["dates"].append({"date": req["date"], "movies": [req["movieid"]]})
	write(bookings)
	return make_response(jsonify(booking), 200)

if __name__ == "__main__":
	print("Server running in port %s"%(PORT))
	app.run(host=HOST, port=PORT)
