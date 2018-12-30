from datetime import datetime
from sanic.response import json, text
from sanic import Blueprint

# from neurals import bbox_limit, neuron, feed
from traffic import route, match
from geopy.distance import vincenty
from config import app, common
from tools import parse_path, parse_location
from client import fastness
import os
from asyncio import sleep

blu = Blueprint('nostradamus', url_prefix='/0.1')

'''
/hang/~path [GET]  >>> path meta, customer pay, porter earn - nostradamus
/hang/user~path [GET]  >>> nostradamus
'''


async def biker_predict(_id, s_lat, s_lng, t_lat, t_lng, delay):
    _locations = await common.locations.find({'porter': _id}).sort([('_date', -1)]).limit(1).to_list()
    if not _locations:
        #  bad so bad very bad
        return json({'bad': 'bad'})
    location = _locations[0]
    if _id in dst:
        _dst = dst[_id]
        if len(_dst) == 2:
            _dst.append(route(location, _dst[1])['t'])
    else:
        _dst = [None, location, 0]
    return max(_dst[2] + route(_dst[1], [s_lat, s_lng]), delay) + route([s_lat, s_lng], [t_lat, t_lng])


@app.route("/<_id>/predict/@<path>")
@app.route("/<_id>/predict/@<path>/+<delay:int>")
async def biker_predict_endpoint(request, _id, path, delay=0):
    s_lat, s_lng, t_lat, t_lng = parse_path(path)
    t = biker_predict(_id, s_lat, s_lng, t_lat, t_lng)
    return json({'t': t})


@app.route("/predict/@<path>")
@app.route("/predict/@<path>/+<delay:int>")
async def predict(request, path, delay=0):
    s_lat, s_lng, t_lat, t_lng = parse_path(path)
    bbox = []
    bbox_size = .001
    while len(bbox) < bbox_limit and bbox_size < 1:
        l_lat, l_lng, r_lat, r_lng = s_lat - bbox_size, s_lng - bbox_size, s_lat + bbox_size, s_lng + bbox_size
        bbox = locations.find({
            'location': {
                '$geoWithin': {
                    '$box': [
                        [s_lat, s_lng],
                        [r_lat, r_lng]
                    ]
                }
            }
        }).limit().to_list()
        bbox_size *= 2
    times = [await biker_predict(location['porter'], s_lat, s_lng, t_lat, t_lng, delay) for location in bbox]
    return text('fe')  # neuron(times)
# in _location you have to feed neural.


import traffic.weather
import traffic
