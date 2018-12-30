from sanic import Blueprint
from sanic.response import text, json
from ego import privileges, ban
from datetime import datetime, timedelta
from static import client_host
import config
from config import mu
from tools import parse_location, parse_path, JSONEncoder
from tools.ql import _hot_paths, frees
from bson import ObjectId
import json as _json
import solver
from pymongo import ReturnDocument
blu = Blueprint('scenario', url_prefix='/v0.1')


# @blu.route('/~<path>/@priority=<priority>', methods=['POST'])
@blu.route('/<hang>/~<path>/@priority=<priority>', methods=['POST'])
@privileges({'a', 'b', 'o'})
async def set_priority(request, payload, hang, path, volume=0, priority=0):
    print(path)
    pass


# @blu.route('/~<path>/@delay=<delay>', methods=['POST'])
@blu.route('/<hang>/~<path>/@delay=<delay>', methods=['POST'])
@privileges({'a', 'b', 'o'})
async def alter_delay(request, payload, path):
    pass


@blu.route('/<hang>/~<path>/@ack', methods=['POST'])
@privileges({'a', 'b', 'o', 'p'})
async def at(request, payload, hang, path):
    location = (await config.locations.find({'hang': hang, 'porter': payload[1]}).sort([('_date', -1)]).to_list(1))[0]
    path = path.split(';')  # bunch of ids
    now = datetime.now()
    if len(path) <= 2:
        returned_id = path[0]
        path = await config.paths.find_one_and_update({
            '_id': ObjectId(returned_id),
            'hang': hang,
        }, {
            '$push': {
                'porters': {
                    'porter': payload[1],
                    '_date': now,
                    'ack': True,
                    'location': location['location']
                }
            }
        }, return_document=ReturnDocument.AFTER)
    else:
        paths = await config.paths.find({
            '_id': {'$in': [ObjectId(point) for point in path]},  # fixme maybe it check them two
        }).to_list(None)
        await config.paths.delete_many({
            '_id': {'$in': [p['_id'] for p in paths]},
        })
        paths = {str(p['_id']): p for p in paths}
        flags = set()
        ids = []
        for p in path:
            if p in flags:
                ids.append('$' + p)
            else:
                ids.append(p)
            flags.add(p)
        path = {
            'hang': hang,
            'points': [paths[ids[int(p[1:])]]['points'][0] if '$' in p else paths[p]['points'][1] for p in reversed(path)],
            'porters': [{
                'porter': payload[1],
                '_date': now,
                'ack': True,
                'location': location['location']
            }]
        }
        returned_id = str((await config.paths.insert_one(path)).inserted_id)
    ps = {}
    if path:
        points = path['points']
        config.locations.update_one({'_id': location['_id']}, {
            '$set': {'points': [{'_id': _id} for _id in set(p['_id'] for p in points)]}
        })

        for i, p in enumerate(reversed(points)):
            _id = str(p['_id'])
            if '_date' in p:
                delay = (now - p['_date']).total_seconds()
                ps[_id] = delay
                config.mu.observe({
                    'type': 0,
                    '_id': _id,
                    'hang': hang,
                    'location': p['location'],
                    'value': delay,
                    '_date': now
                })
                # pfs[i].date = p['_date'].timestamp()
            else:
                config.mu.observe({
                    'type': 1,
                    '_id': _id,
                    'hang': hang,
                    'location': p['location'],
                    'value': ps[_id],
                    '_date': now
                })
    return json({"SUCCESS": True, '_id': returned_id})


# @blu.route('/~<path>/@nack', methods=['POST'])
@blu.route('/<hang>/~<path>/@nack', methods=['POST'])
@privileges({'a', 'b', 'o', 'p'})
async def at(request, payload, path, hang):
    # unwrap all to atomic paths ->
    pass


# @blu.route('/~<path>/@at', methods=['POST'])
@blu.route('/<hang>/~<path>/@at', methods=['POST'])
@privileges({'a', 'b', 'o', 'p'})
async def at(request, payload, path, hang):
    await config.paths.update_one({
        'points': {
            '$elemMatch': {
                '_id': ObjectId(path),
                'volume': {'$exists': True}
            }
        }
    }, {
        '$set': {
            'points.$.at': datetime.now()
        }
    })
    return json({'SUCCESS': True})


# @blu.route('/~<path>/@done', methods=['POST'])
@blu.route('/<hang>/~<path>/@done', methods=['POST'])
@privileges({'a', 'b', 'o', 'p'})
async def at(request, payload, path, hang):
    """
    if it is in dispatch mode if it is the last point then we remove it from flash and
    """
    await config.paths.update_one({
        'points': {
            '$elemMatch': {
                '_id': ObjectId(path),
                'volume': {'$exists': False}
            }
        }
    }, {
        '$set': {
            'points.$.at': datetime.now()
        }
    })
    await config.users.update_one({'user': hang, 'hang': hang}, {'$inc': {'credit': -1}})
    return json({'SUCCESS': True})


@blu.route('/<hang>/~<path>', methods=['POST', 'PUT'])
@privileges({'a', 'b', 'o'})
async def _path(request, payload, hang, path):
    s_lat, s_lng, t_lat, t_lng = parse_path(path)
    _id = ObjectId()
    now = datetime.now()
    priority = int(request.form['priority'][0]) if 'priority' in request.form else 0
    volume = int(request.form['volume'][0]) if 'volume' in request.form else 0
    result = await config.paths.insert_one({
        '_id': _id,
        'hang': hang,
        'priority': priority,
        'points': [  # TWISTED
            {
                '_id': _id,
                # 'window': [],
                'location': [t_lat, t_lng],
                # 'at': datetime.now()
            }, {
                '_id': _id,
                '_date': now,
                '_author': payload[1],
                'volume': volume,
                'head': datetime.now(),
                'tail': 0,
                'location': [s_lat, s_lng],
                # 'at': datetime.now()
            }
        ],
        'porters': [
            # {
            #     '_id': '',
            #     '_date': datetime.now(),
            #     'ack': None
            # }
        ]
    })
    return json({'success': True, '_id': str(result.inserted_id)}, 201)


def fcm(matches):
    pass


@blu.route('/<hang>/!!!/<algorithm>/<protocol>', methods=['POST', 'GET'])
@blu.route('/<hang>/!!!/<algorithm>', methods=['POST', 'GET'])
@privileges({'a', 'b'})
async def solve(request, payload, hang, algorithm, protocol=None):
    _frees = await frees(hang)
    hot_paths = await _hot_paths(hang)
    print('-- matching {} free porters with {} hot paths --'.format(len(_frees), len(hot_paths)))
    matches = await getattr(solver, algorithm)(_frees, hot_paths)
    # print(matches)
    if protocol:
        await globals()[protocol](matches)
    matches = {match[0]['porter']: match[1] for match in matches}
    for key, value in matches.items():
        value['_id'] = str(value['_id'])
        for p in value['points']:
            p['_id'] = str(p['_id'])
            if 'head' in p:
                p['head'] = str(p['head'])
                p['tail'] = str(p['tail'])
                p['_date'] = str(p['_date'])
        await config.session.post(client_host + '/{}'.format(key), data={'path': _json.dumps(value)})
    return json({'SUCCESS': True, 'huli': 'muli'})


@blu.route('/<hang>/<user>/@messages')
@privileges({'a', 'b', 'o', 'p'})
async def know(request, payload, user, hang):
    ban(payload, user, hang)
    msg = config.notifications.get(user, None)
    msg = [msg] if msg else []
    return text(_json.dumps(msg, cls=JSONEncoder))
