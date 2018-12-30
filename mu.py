import asyncio
from contextlib import closing
from multiprocessing import Process
from tools.mu.v02 import Mu
import ujson as json

core_args = []
hangs = {}


def observe(_type, _id, hang, location, value, _date):
    if hang not in hangs:
        hangs[hang] = (Mu(), Mu(), Mu())
    hangs[hang][_type].observe(_id, *location, value)


def server(rts):
    loop = asyncio.new_event_loop()

    async def handler(r, t):
        r = await r.open(loop)
        with closing(t):
            msg = 'hi'
            while msg != 'bye :(':
                msg = await r.readline()
                msg = msg[:-1].decode()
                msg = json.loads(msg)
                if 'observe' in msg:
                    observe(msg['type'], msg['_id'], msg['hang'], msg['location'], msg['value'], msg['_date'])
                else:
                    hang = msg['hang']
                    if hang not in hangs:
                        hangs[hang] = (Mu(), Mu(), Mu())
                    msg = hangs[hang][msg['type']](*msg['location'])
                    t.write('{}\n'.format(str(msg)).encode())

    tasks = []
    for ry, tx in rts:
        tasks.append(handler(ry, loop.run_until_complete(tx.open(loop))))
    try:
        loop.run_until_complete(asyncio.wait(tasks))
    except KeyboardInterrupt:
        pass


def nested(arr):
    if arr:
        forward, backward = arr[0]
        with forward[1].send() as tx:
            core_args.append((backward[0], tx))
            return nested(arr[1:])
    else:
        p = Process(target=server, args=(tuple(core_args),))
        p.daemon = True
        p.start()
        return p


class Client:
    def __init__(self, r, t):
        self.r = r
        self.t = t

    def send(self, msg):
        self.t.write('{}\n'.format(msg).encode())

    def observe(self, query):
        query['observe'] = True
        self.send(json.dumps(query))

    async def __call__(self, _type, hang, location):
        self.send(json.dumps({
            'type': _type,
            'hang': hang,
            'location': location
        }))
        return await self.recv()

    async def bye(self):
        self.send('bye')
        await self.recv()
        # self.ty.__exit__(None, None, None)

    async def recv(self):
        msg = await self.r.readline()
        return msg[:-1].decode()
