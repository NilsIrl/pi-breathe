#!/usr/bin/env python3

from flask import Flask
from flask_restful import Resource, Api, reqparse
import urllib.request
import urllib.parse
import sqlite3
import json
import math

app = Flask(__name__)
api = Api(app)

directionparser = reqparse.RequestParser()
directionparser.add_argument('src', type=str, required=True)
directionparser.add_argument('origin', type=str, required=True)
directionparser.add_argument('destination', type=str, required=True)
directionparser.add_argument('rank_preference', type=str, required=True)

pollutionparse = reqparse.RequestParser()
pollutionparse.add_argument('src', type=str, required=True)
pollutionparse.add_argument('lng', type=float, required=True)
pollutionparse.add_argument('lat', type=float, required=True)
pollutionparse.add_argument('time')
pollutionparse.add_argument('pollution', type=float, required=True)


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
                pollution_level += abs((step['start_location']['lat'] -
                                        step['end_location']['lat']) *
                                       pollution_location[1] -
                                       (step['start_location']['lng'] -
                                        step['end_location']['lng']) *
                                       pollution_location[0] +
                                       step['start_location']['lng'] *
                                       step['end_location']['lat'] -
                                       step['start_location']['lat'] *
                                       step['end_location']['lng']) / \
                                       math.sqrt(
                                           (step['start_location']['lat'] -
                                            step['end_location']['lat']) ** 2 +
                                           (step['start_location']['lng'] -
                                            step['end_location']['lng']) ** 2)
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
        networked = False
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
            return {k: apirequest[k] for k in ('status', 'error_message')}
        bestroute = apirequest['routes'][0]
        bestlevel = Direction.pollutionlevel(apirequest['routes'][0])
        for route in apirequest['routes'][1:]:
            level = self.pollutionlevel(route)
            if level > bestlevel:
                bestroute = route
            elif level == bestlevel:
                if route['legs'][0][rank_preference]['value'] < \
                   bestroute['legs'][0][rank_preference]['value']:
                    bestroute = route
        return bestroute


class Pollution(Resource):
    def get(self):
        pass

    def post(self):
        args = pollutionparse.parse_args()
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


api.add_resource(Direction, '/direction')
api.add_resource(Pollution, '/pollution')

if __name__ == '__main__':
    app.run(debug=True)
