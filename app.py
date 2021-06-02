import jsonschema
from flask import Flask, request, jsonify
from jsonschema import validate
from collections import defaultdict
import datetime
import pymongo
import pytz

app = Flask(__name__, static_url_path='')

mongodb_uri = 'mongodb+srv://app:Fq0gY35jenP1Dn4s@main.3jwk1.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
client = pymongo.MongoClient(mongodb_uri, connect=False)
main_db = client.main_db


@app.route('/')
def index():
    return app.send_static_file('index.html')


def compute_availabilities(default, reservations, tz):
    not_available = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for reservation in reservations:
        start_date = pytz.utc.localize(reservation['startDate']).astimezone(tz)
        end_date = pytz.utc.localize(reservation['endDate']).astimezone(tz)
        for seat in reservation['seats']:
            hours = list(range(start_date.hour, end_date.hour))
            for hour in hours:
                not_available[hour][seat['buildingName']][seat['classroomName']].append(seat['number'])
    available = []
    for hour, buildings in default.items():
        for building, classrooms in buildings.items():
            for classroom, seats in classrooms.items():
                available_seats = set(seats) - set(not_available[hour][building][classroom])
                if len(available_seats) > 0:
                    available.append({'hour': hour, 'buildingName': building, 'classroomName': classroom,
                                      'seatsNumber': list(available_seats)})
    return available


@app.route('/api/get_dates')
def get_dates():
    tz = pytz.timezone('Europe/Rome')
    now = datetime.datetime.now(tz)
    reservations = list(main_db.reservation.find({'$or': [{'startDate': {'$gt': now}}, {'endDate': {'$gt': now}}]}))

    dates = []
    for date in [now] + [now.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=i) for i in
                         range(1, 6)]:
        date_after = date.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
        filtered_reservations = [reservation for reservation in reservations if
                                 date < pytz.utc.localize(reservation['startDate']) < date_after or
                                 date < pytz.utc.localize(reservation['endDate']) < date_after]
        default = {hour: {building['name']: {classroom['name']: classroom['seats']
                                             for classroom in building['classrooms']}
                          for building in main_db.building.find({})} for hour in range(max(date.hour, 8), 23)}
        if len(compute_availabilities(default, filtered_reservations, tz)) > 0:
            dates.append(date.strftime('%Y-%m-%d'))
    return jsonify(dates)


@app.route('/api/get_availabilities')
def get_availabilities():
    date_string = request.args.get('date')
    tz = pytz.timezone('Europe/Rome')
    if date_string is not None:
        try:
            date = tz.localize(datetime.datetime.strptime(date_string, '%Y-%m-%d'))
        except ValueError as e:
            return str(e), 422
        now = datetime.datetime.now(tz)
        if date.date() == now.date():
            date = now
    else:
        date = datetime.datetime.now(tz)
    date_after = date.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
    reservations = list(main_db.reservation.find({
        '$or': [{'startDate': {'$gt': date, '$lt': date_after}}, {'endDate': {'$gt': date, '$lt': date_after}}]}))
    default = {hour: {building['name']: {classroom['name']: classroom['seats'] for classroom in building['classrooms']}
                      for building in main_db.building.find({})} for hour in range(max(date.hour, 8), 23)}
    available = compute_availabilities(default, reservations, tz)
    return jsonify(available)


def validate_schema(instance):
    schema = {
        "type": "object",
        "properties": {
            "userId": {"type": "string"},
            "date": {"type": "string"},
            "hour": {"type": "integer"},
            "duration": {"type": "integer"},
            "building": {"type": "string"},
            "classroom": {"type": "string"},
            "seats": {"type": "array", "items": {"type": "string"}}
        },
        "additionalProperties": False
    }

    try:
        validate(instance=instance, schema=schema)
        return True
    except jsonschema.exceptions.ValidationError as err:
        print(err)
        return False


@app.route('/api/book_seats', methods=['POST'])
def book_seats():
    reservation = request.json
    if not reservation or not validate_schema(reservation):
        return 'bad request', 400
    tz = pytz.timezone('Europe/Rome')
    date = tz.localize(datetime.datetime.strptime(reservation['date'], '%Y-%m-%d'))
    start_date = date.replace(hour=reservation['hour'])
    end_date = start_date + datetime.timedelta(hours=reservation['duration'])
    mongo_data = {'user_id': reservation['userId'], 'startDate': start_date, 'endDate': end_date, 'seats': [
        {'buildingName': reservation['building'], 'classroomName': reservation['classroom'], 'number': seat}
        for seat in reservation['seats']
    ]}
    main_db.reservation.insert_one(mongo_data)
    return 'ok', 200


if __name__ == '__main__':
    app.run()
