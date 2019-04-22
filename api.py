#!/usr/bin/env python3

from flask import Flask
from flask_restful import Resource, Api, reqparse
import urllib.request
import urllib.parse
import sqlite3
import json
import time

app = Flask(__name__)
api = Api(app)

directionparser = reqparse.RequestParser()
directionparser.add_argument('src', type=str, required=True)
directionparser.add_argument('origin', type=str, required=True)
directionparser.add_argument('destination', type=str, required=True)
# distance or duration if pollution is equal
directionparser.add_argument('rank_preference', type=str, required=True)

pollutionparser = reqparse.RequestParser()
pollutionparser.add_argument('src', type=str, required=True)
pollutionparser.add_argument('lng', type=float, required=True)
pollutionparser.add_argument('lat', type=float, required=True)
pollutionparser.add_argument('time')
pollutionparser.add_argument('pollution', type=float, required=True)

postlocationparser = reqparse.RequestParser()
postlocationparser.add_argument('src', type=str, required=True)
postlocationparser.add_argument('lat', type=float, required=True)
postlocationparser.add_argument('lng', type=float, required=True)
postlocationparser.add_argument('time', type=int, required=False)

getlocationparser = reqparse.RequestParser()
getlocationparser.add_argument('src', type=str, required=True)
getlocationparser.add_argument('n', type=int, required=False)
getlocationparser.add_argument('maxtime', type=int, required=False)
getlocationparser.add_argument('mintime', type=int, required=False)
getlocationparser.add_argument('later', type=bool, required=False)


class Direction(Resource):
    @staticmethod
    def loadPollution(route):
        with sqlite3.connect('database/pi-breathe.db') as conn:
            c = conn.cursor()
            c.execute("SELECT lat, lng, pollution FROM pollution WHERE "
                      "lat < :northeastlat AND lat > :southwestlat AND "
                      "lng < :northeastlng AND lng > :southwestlng",
                      {"northeastlat": route['bounds']['northeast']['lat'],
                       "southwestlat": route['bounds']['southwest']['lat'],
                       "northeastlng": route['bounds']['northeast']['lng'],
                       "southwestlng": route['bounds']['southwest']['lng']})
            return c.fetchall()

    @staticmethod
    def pollutionlevel(route):
        pollution_locations = Direction.loadPollution(route)
        pollution_level = 0
        for step in route['legs'][0]['steps']:
            for pollution_location in pollution_locations:
                # https://wikimedia.org/api/rest_v1/media/math/render/svg/be2ab4a9d9d77f1623a2723891f652028a7a328d
                x0 = pollution_location[1]
                y0 = pollution_location[0]
                x1 = step['start_location']['lng']
                y1 = step['start_location']['lat']
                x2 = step['end_location']['lng']
                y2 = step['end_location']['lat']
                m_line = (x1 - x2) / (y1 - y2)
                c_line = y1 - m_line * x1
                m_new = -1 / m_line
                c_new = y0 - m_new * x0
                lng = (c_line-c_new)/(m_line-m_new)
                lat = lng * m_new + c_new
        return pollution_level

    def get(self):
        args = directionparser.parse_args()
        data = {}
        with open("secret/api.key") as keyfile:
            data['key'] = keyfile.read()
        data['mode'] = "walking"
        data['alternatives'] = "true"
        data['origin'] = args['origin']
        data['destination'] = args['destination']
        networked = True
        rank_preference = 'duration' if args['rank_preference'] != 'distance' \
                          else 'distance'
        if networked:
            url = "https://maps.googleapis.com/maps/api/directions/json?" + \
                  urllib.parse.urlencode(data)
            response = urllib.request.urlopen(url)
        else:
            response = open("test.json")
        apirequest = json.load(response)

        if apirequest['status'] != 'OK':
            return {k: apirequest[k] for k in ['status']}
        bestroute = apirequest['routes'][0]
        bestlevel = Direction.pollutionlevel(apirequest['routes'][0])
        for route in apirequest['routes'][1:]:
            level = Direction.pollutionlevel(route)
            if level > bestlevel:
                bestroute = route
            elif level == bestlevel:
                if route['legs'][0][rank_preference]['value'] < \
                   bestroute['legs'][0][rank_preference]['value']:
                    bestroute = route
        return bestroute, 200, {'Access-Control-Allow-Origin': '*'}


class Pollution(Resource):
    def get(self):
        pass

    def post(self):
        args = pollutionparser.parse_args()
        with sqlite3.connect('database/pi-breathe.db') as conn:
            c = conn.cursor()
            if 'time' in args:
                c.execute("INSERT INTO pollution (src, lng, lat, time,"
                          "pollution) VALUES (:src, :lng, :lat, :time,"
                          ":pollution)", {"src": args['src'],
                                          "lng": args['lng'],
                                          "lat": args['lat'],
                                          "time": args['time'],
                                          "pollution": args['pollution']})
            else:
                c.execute("INSERT INTO pollution (src, lng, lat, pollution)"
                          " VALUES (:src, :lng, :lat, :pollution)",
                          {"src": args['src'],
                           "lng": args['lng'],
                           "lat": args['lat'],
                           "time": args['time'],
                           "pollution": args['pollution']})
            conn.commit()
        return {"message": "Success"}


class Location(Resource):
    def get(self):
        args = getlocationparser.parse_args()
        with sqlite3.connect("database/pi-breathe.db") as conn:
            c = conn.cursor()
            request = "SELECT lng, lat, time FROM location WHERE "
            request += "src = :src"
            if args['maxtime'] is not None or args['mintime'] is not None:
                if args['maxtime'] is not None:
                    request += " AND time < :maxtime"
                if args['mintime'] is not None:
                    request += " AND time > :mintime"
            request += " ORDER BY time "
            request += "DESC" if args["later"] else "ASC"
            if args['n'] is not None:
                request += " LIMIT :n"
            print(request)
            c.execute(request, args)
            result = c.fetchall()
        return {"locations": result}

    def post(self):
        args = postlocationparser.parse_args()
        with sqlite3.connect("database/pi-breathe.db") as conn:
            c = conn.cursor()
            args["time"] = args['time'] if 'time' in args else int(time.time())
            c.execute("INSERT INTO location (src, lng, lat, time) VALUES"
                      " (:src, :lng, :lat, :time)", args)
            conn.commit()
        return {"message": "Success"}, 200, {'Access-Control-Allow-Origin': '*'
                                             }


api.add_resource(Direction, '/direction')
api.add_resource(Pollution, '/pollution')
api.add_resource(Location, '/location')

if __name__ == '__main__':
    app.run(debug=True)
