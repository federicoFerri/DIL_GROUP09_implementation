from bson.json_util import dumps
from flask import Flask, request, jsonify
from collections import defaultdict
import calendar
import datetime
import pymongo
import copy

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


@app.route('/getBuildings')
def available_buildings():
    num_seats = request.args.get('num_seats', 1, type=int)
    start_day, end_day = calendar.monthrange(datetime.date.today().year, datetime.date.today().month)
    start_date = datetime.datetime.combine(datetime.date.today().replace(day=start_day), datetime.datetime.min.time())
    end_date = datetime.datetime.combine(datetime.date.today().replace(day=end_day), datetime.datetime.max.time())
    reservations = main_db.reservation.find({'startDate': {'$gt': start_date, '$lt': end_date}})
    buildings = {
        hour: {building['name']: {classroom['name']: classroom['seats'] for classroom in building['classrooms']} for
               building in main_db.building.find({})} for hour in range(8, 23)}
    for day in range(start_day, end_day + 1):
        today_reservations = [reservation for reservation in reservations if reservation['startDate'].day == day]
        used = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        available = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        for reservation in today_reservations:
            for seat in reservation['seats']:
                hours = list(range(reservation['startDate'].hour, reservation['endDate'].hour))
                for hour in hours:
                    used[hour][seat['buildingName']][seat['classroomName']].append(seat['number'])
        for building, classrooms in buildings.items():
            for classroom, hours in classrooms.items():
                for hour, seats in hours.items():
                    available_seats = set(seats) - set(used[hour][building][classroom])
                    if len(available_seats) >= num_seats:
                        available[hour][building][classroom].extend(available_seats)
        print(available)

    return 'ok'


@app.route('/reserveSeats', methods=['POST'])
def reserve_seats():
    reservation = request.json
    seats = reservation['seats']
    if not reservation:
        return 'bad request', 400
    main_db.reservation.insert(
        {'userId': reservation['userId'], 'startDate': reservation['startDate'], 'endDate': reservation['endDate'],
         'seats': seats})
    return 'ok', 200


@app.route('/getByDate')
def seats_by_date():
    date = request.args.get('date')
    start_date = datetime.datetime.strptime(date, '%Y-%m-%d')
    end_date = start_date.replace(day=start_date.day + 1)
    today_reservations = main_db.reservation.find({'startDate': {'$gt': start_date, '$lt': end_date}})
    occupied_seats = []
    available_seats = []
    for reservation in today_reservations:
        for seat in reservation['seats']:
            occupied_seats.insert(seat)
    buildings = main_db.building.find({})
    for building in buildings:
        for classroom in building['classrooms']:
            for seat in classroom['seats']:
                if seat not in occupied_seats:
                    available_seats.insert(
                        {"seat": seat,
                         "building": building,
                         "classroom": classroom})
    return jsonify(available_seats), 200


if __name__ == '__main__':
    app.run()
