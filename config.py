from motor.motor_asyncio import AsyncIOMotorClient
from sanic import Sanic
import asyncio
import aiohttp
from multiprocessing import Value
from ctypes import c_bool, c_int
from aiopipe import aiopipe
from mu import Client, nested
wrk = 3
app = Sanic(__name__)


lock, cnt, cnt_lock = Value(c_bool, False), Value(c_int, 0), Value(c_bool, False)
session, locations, paths, users = None, None, None, None
mu = None
star = [(aiopipe(), aiopipe()) for _ in range(wrk)]
_server = nested(star)


@app.listener('before_server_start')
async def init(sanic, loop):
    global session, locations, users, paths
    session = await aiohttp.ClientSession().__aenter__()
    db = AsyncIOMotorClient().express
    locations = AsyncIOMotorClient('mongodb://localhost:27020').express.locations
    locations.create_index([('location', '2d')])
    locations.create_index([('location', '2dsphere')])
    users = db.users
    paths = db.paths

    while True:
        if not cnt_lock.value:
            global mu
            cnt_lock.value = True
            rx, ty = star[cnt.value][0][0], star[cnt.value][1][1]
            ty = ty.send()
            mu = Client(await rx.open(loop), await ty.__enter__().open())
            cnt.value += 1
            cnt_lock.value = False
            break


@app.listener('before_server_start')
async def init_ones(sanic, loop):
    if not lock.value:
        lock.value = True
        _paths = await paths.find({
            'porters.ack': True
        }).sort([('_date', -1)]).to_list(10000)
        ps = {}
        for path in _paths:
            ps.clear()
            hang = path['hang']
            now = path['porters'][-1]['_date']
            for p in reversed(path['points']):
                _id = str(p['_id'])
                if '_date' in p:
                    delay = (now - p['_date']).total_seconds()
                    ps[_id] = delay
                    mu.observe({
                        'type': 0,
                        '_id': _id,
                        'hang': hang,
                        'location': p['location'],
                        'value': delay,
                        '_date': now
                    })
                else:
                    mu.observe({
                        'type': 1,
                        '_id': _id,
                        'hang': hang,
                        'location': p['location'],
                        'value': ps[_id],
                        '_date': now
                    })
        # print(await mu(0, 'food', [35.747181515, 51.237893783]))


@app.listener('after_server_stop')
async def after_server_stop(sanic, loop):
    await session.__aexit__(None, None, None)
    # await client.bye()
    await asyncio.sleep(0)
