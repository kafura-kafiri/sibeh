from sanic import Blueprint
from sanic.response import json
from ego import privileges
from ast import literal_eval
import config
from datetime import datetime, timedelta
blu = Blueprint('ql', url_prefix='/v0.1/!!')
'''
    graph ql - free users.
    graph ql - unassigned orders
    add hang to ql so can separate hangs /<hang>/!!/<collection>
'''


@blu.route("/<hang>/<collection>", methods=['DELETE'])
@privileges({'a', 'b', 'o'})
async def delete_all(request, payload, hang, collection):
    return json(await getattr(config, collection).delete_many(literal_eval(
        request.form['q'][0] if 'q' in request.form else request.args['q'][0]
    )))


@blu.route("/<hang>/<collection>", methods=['GET'])
@privileges({'a', 'b', 'o'})
async def delete_all(request, payload, hang, collection):
    return json(await getattr(config, collection).find(literal_eval(
        request.form['q'][0] if 'q' in request.form else request.args['q'][0]
    )).to_list(None))


@blu.route("/<hang>/<collection>", methods=['POST'])
@privileges({'a', 'b', 'o'})
async def delete_all(request, payload, hang, collection):
    return json(await getattr(config, collection).aggregate(literal_eval(
        request.form['q'][0] if 'q' in request.form else request.args['q'][0]
    )).to_list(None))


async def _hot_paths(hang):
    head = datetime.now() + timedelta(minutes=10)
    return await config.paths.find({
        'hang': hang,
        'points.head': {
            '$lte': head
        },
        '$or': [
            {
                'porters.ack': {'$in': [None, False]}
            }, {
                'porters': []
            }
        ],
    }).to_list(None)


@blu.route("/<hang>/paths/@hots")
@privileges({'a', 'b', 'o'})
async def hot_paths(request, payload, hang):
    paths = await _hot_paths(hang)
    for path in paths:
        path['_id'] = str(path['_id'])
        for p in path['points']:
            p['_id'] = str(p['_id'])
    return json(paths)


@blu.route("/<hang>/paths/@undone", methods=['GET', 'POST'])  # undone
@privileges({'a', 'b', 'o'})
async def undone(request, payload, hang):
    paths = await config.paths.find({
        'hang': hang,
        'points': {
            '$not': {
                '$elemMatch': {
                    'volume': {'$exists': False},
                    'at': {'$exists': True}
                }
            }
        }
    }).to_list(None)
    for path in paths:
        path['_id'] = str(path['_id'])
        for p in path['points']:
            p['_id'] = str(p['_id'])
    return json(paths)


async def frees(hang):
    locations = await config.locations.aggregate([
        {
            '$match': {
                'hang': hang,
                # 'points': {'$exists': False},
                '_date': {'$gt': datetime.now() - timedelta(minutes=5)}
            }
        }, {
            '$sort': {'porter': 1, '_date': 1}
        }, {
            '$group': {
                '_id': "$porter",
                '_date': {'$last': "$_date"},
                'doc': {'$last': '$$ROOT'},
            }
        }, {
            '$match': {
                'doc.points': {'$exists': False}
            }
        }
    ]).to_list(None)
    return [last['doc'] for last in locations]


@blu.route('/<hang>/porters/@frees', methods=['POST'])
@privileges({'a', 'b', 'o'})
async def _frees(request, payload, hang):
    free_porters = await frees(hang)
    for porter in free_porters:
        del porter['_id']
    return json({'data': free_porters})


@blu.route('/<hang>/porters/@all', methods=['POST'])
@privileges({'a', 'b', 'o'})
async def _total(request, payload, hang):
    locations = await config.locations.aggregate([
        {
            '$match': {
                'hang': hang,
                # 'points': {'$exists': False},
                '_date': {'$gt': datetime.now() - timedelta(minutes=5)}
            }
        }, {
            '$sort': {'porter': 1, '_date': 1}
        }, {
            '$group': {
                '_id': "$porter",
                '_date': {'$last': "$_date"},
                'doc': {'$last': '$$ROOT'},
            }
        }
    ]).to_list(None)
    locations = [last['doc'] for last in locations]
    for doc in locations:
        del doc['_id']
        del doc['_date']
        if 'points' in doc:
            for p in doc['points']:
                p['_id'] = str(p['_id'])
    return json(locations)
