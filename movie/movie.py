from flask import Flask, render_template, request, jsonify, make_response, send_from_directory
import json
import sys
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3200
HOST = '0.0.0.0'

# Reading and writing to the json database
with open('{}/databases/movies.json'.format("."), 'r') as jsf:
   movies = json.load(jsf)["movies"]

def write(movies):
    with open('{}/databases/movies.json'.format("."), 'w') as f:
        json.dump({'movies':movies}, f, indent=4)

# Swagger documentation
@app.route("/docs", methods=['GET'])
def docs():
	return render_template('swagger_template.html')

@app.route('/spec', methods=['GET'])
def get_spec():
	return send_from_directory('.', 'UE-archi-distribuees-Movie-1.0.0-resolved.yaml')

# Routes
@app.route("/", methods=['GET'])
def home():
    return make_response("<h1 style='color:blue'>Welcome to the Movie service!</h1>",200)

@app.route("/json", methods=['GET'])
def get_json():
    res = make_response(jsonify(movies), 200)
    return res

@app.route("/movies/<movieid>", methods=['GET'])
def get_movie_by_id(movieid):
    for m in movies:
        if str(m['id']) == str(movieid):
            res = make_response(jsonify(m), 200)
            return res
    return make_response(jsonify({'error': 'Movie ID not found'}), 400)

@app.route('/movies/<movieid>', methods=['POST'])
def add_movie(movieid):
    if any([k not in request.get_json() for k in ['id', 'title', 'rating', 'director']]):
        return make_response(jsonify({'error': 'bad input parameter'}), 400)
    req = request.get_json()
    for m in movies:
        if str(m['id']) == str(movieid):
            return make_response(jsonify({'error': 'Movie ID already exists'}), 409)
    movies.append(req)
    write(movies)
    res = make_response(jsonify({"message":"movie added"}),200)
    return res

@app.route('/movies/<movieid>/<rating>', methods=['PUT'])
def update_rating(movieid, rating):
    try:
        rating = float(rating)
    except ValueError:
        return make_response(jsonify({'error': 'Rating must be a number'}), 400)
    for m in movies:
        if str(m['id']) == str(movieid):
            m['rating'] = rating
            write(movies)
            return make_response(jsonify(m), 200)
    return make_response(jsonify({'error': 'Movie ID not found'}), 404)

@app.route('/movies/<movieid>', methods=['DELETE'])
def delete_movie(movieid):
    for m in movies:
        if str(m['id']) == str(movieid):
            movies.remove(m)
            write(movies)
            return make_response(jsonify(m), 200)
    return make_response(jsonify({'error': 'Movie not found'}), 404)

if __name__ == "__main__":
    print("Server running in port %s"%(PORT))
    app.run(host=HOST, port=PORT)
