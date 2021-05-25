from bson.json_util import dumps
from flask import Flask, request, jsonify
import pymongo

app = Flask(__name__, static_url_path='')

mongodb_uri = 'mongodb+srv://app:Fq0gY35jenP1Dn4s@main.3jwk1.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
client = pymongo.MongoClient(mongodb_uri, connect=False)
main_db = client.main_db


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/api/')
def api_index():
    main_db.test_collection.find({})
    return 'Hello world api'

@app.route('/getbuildings')
def available_buildings():
   num_seats = request.args.get('num_seats')
   return main_db.building.find({})       # TODO ritornare solo gli edifici che hanno un tot numero di posti disponibili

@app.route('/getclassrooms')
def available_classrooms():
    building = request.args.get('building')
    return dumps(main_db.building.find({"name": building}))

@app.route('/getseats')
def available_seats():
    classroom = request.args.get('classroom')
    return dumps(main_db.classroom.find({"name": classroom}))   # è un'altra collection?

@app.route('/selectseats', methods=['POST'])
def select_seats():
    seats = request.json
    if not seats:
        return 'bad request', 400

    # come inserire valori nel database
    return 'ok', 200

if __name__ == '__main__':
    app.run()