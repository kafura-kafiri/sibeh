from sanic import Blueprint
from sanic.response import text, json
import ujson
from tools import parse_location, parse_path
from datetime import datetime
import config
from ego import privileges
from geopy.distance import vincenty
from client import fastness
import config
from tools import points
import ujson
import numpy as np
from bson import ObjectId

c = .01

# from oracle import observe
blu = Blueprint('motion', url_prefix='/v0.1')


@blu.route('/~<path>/@', methods=['GET'])
@blu.route('/<hang>/~<path>/@', methods=['GET'])
@privileges({'a', 'b', 'o', 'p'})
async def path_location(request, payload, path, hang=None):
    location = await config.locations.find({
        'hang': hang,
        'points._id': ObjectId(path)
    }).sort([('_date', -1)]).to_list(1)
    if location:
        location = location[0]
        del location['points']
        del location['_id']
    else:
        location = {}
    return json(location, 200)


@blu.route("/<hang>/<user>/@", methods=['GET'])
@privileges({'a', 'b', 'o', 'p'})
async def user_location(request, payload, hang, user):
    location = await config.locations.find({'hang': hang, 'porter': user}).sort([('_date', -1)]).to_list(1)
    if location:
        location = location[0]
        if 'points' in location:
            del location['points']
        del location['_id']
    else:
        location = {}
    return json(location, 200)


async def __location(hang, user, _location_, points):
    now = datetime.now()
    config.mu.observe(
        {
            'type': 2,
            '_id': user,
            'hang': hang,
            'location': _location_[:2],
            'value': 1,
            '_date': now
        })
    velocity = None
    # lat, lng, date =
    # ts = now.timestamp() - date
    # if ts < 100:
    #     d = vincenty(location, (lat, lng)).m
    #     d /= ts * fastness
    #     if d > 2:
    #         velocity = [d, location[0] - lat, location[1] - lng]

    # print('---', user)
    location = {
        '_date': now,
        'porter': user,
        'hang': hang,
        'location': _location_[:2],
    }
    if len(_location_) > 2:
        location['altitude'] = _location_[2],
    if velocity:
        location['velocity'] = velocity
    if points:
        location['points'] = [{'_id': ObjectId(_id)} for _id in set(points)]
    insert = await config.locations.insert_one(location)
    return {"inserted_id": str(insert.inserted_id)}


@blu.websocket('/<hang>/<user>/@@')
@privileges({'a', 'b', 'o', 'p'})
async def _location_loop(request, payload, ws, hang, user):
    while True:
        data = await ws.recv()
        data = ujson.loads(data)
        location = data['location']
        points = data['points']
        await ws.send(ujson.dumps(await __location(hang, user, location, points)))


@blu.route("/<hang>/<user>/@<location>", methods=['GET', 'POST', 'PUT'])
@blu.route("/<hang>/<user>/@<location>/~<points>", methods=['GET', 'POST', 'PUT'])
@privileges({'a', 'b', 'o', 'p'})
async def _location(request, payload, hang, user, location, points=''):
    location = parse_location(location)
    return json(await __location(hang, user, location, points.split(';') if points else []))


async def _sum_star(porters, transmitter, receiver):
    porters.append(transmitter)
    porters.append(receiver)
    async with config.session.get(config.osrm_host + '/table/v1/driving/' + points(porters), params={
        'sources': ';'.join([str(i) for i in range(len(porters) - 1)]),
        'destinations': ';'.join([str(i) for i in range(len(porters) - 2, len(porters))])
    }) as response:
        m = np.array(json.loads(await response.text())['durations'])
        return sum(m[:-1, 0]) / (m.shape[0] - 1) + m[-1, 1]


@blu.route('/<hang>/~<path>/*')
async def _sum_star(request, porters, transmitter, receiver):
    return text(await _sum_star())


@blu.route('/<hang>/~<path>/$')
async def cost(request, path, hang, porters=None, entropy=True, priority=0):
    if not porters:
        from oracle.oracle import hangs
        porters = hangs[hang][2].knn(path[0])
        print(porters)
        # reassign porters to have [ point ]
    s = await _sum_star(porters, *porters) + priority * 100
    # += entropy() -> *= k
    if entropy:
        from oracle.oracle import hangs
        s += (hangs[hang][2](path[0]) - hangs[hang](path[1])) * c
    # get K from flash
    return text(s * config.flash.get_khang(hang.encode()))
