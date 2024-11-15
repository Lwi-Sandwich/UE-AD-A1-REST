from flask import Flask, render_template, request, jsonify, make_response, send_from_directory
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3202
HOST = '0.0.0.0'

with open('{}/databases/times.json'.format("."), "r") as jsf:
   schedule = json.load(jsf)["schedule"]

# Swagger documentation
@app.route("/docs", methods=['GET'])
def docs():
	return render_template('swagger_template.html')

@app.route('/spec', methods=['GET'])
def get_spec():
	return send_from_directory('.', 'UE-archi-distribuees-Showtime-1.0.0-resolved.yaml')

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Showtime service!</h1>"

@app.route("/showtimes", methods=['GET'])
def showtimes():
   res = make_response(jsonify(schedule), 200)
   return res

@app.route("/showmovies/<date>", methods=['GET'])
def showmovies(date):
   for s in schedule:
      if str(s['date']) == str(date):
         res = make_response(jsonify(s), 200)
         return res
   return make_response(jsonify({'error': 'showtime date not found'}), 404)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
