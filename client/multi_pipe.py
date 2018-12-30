from contextlib import closing
from multiprocessing import Process
import asyncio
from aiopipe import aiopipe
import uvloop
import time
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def main():
    star = [(aiopipe(), aiopipe()) for _ in range(16)]
    core_args = []

    def nested(arr):
        if arr:
            forward, backward = arr[0]
            with forward[1].send() as tx:
                core_args.append((backward[0], tx))
                return nested(arr[1:])
        else:
            p = Process(target=server, args=(tuple(core_args), ))
            p.start()
            return p

    _server = nested(star)
    _clients = []
    n = time.time()
    for (rx, _), (_, ty) in star:
        _clients.append(Process(target=client, args=(rx, ty)))
        _clients[-1].start()
    for _client in _clients:
        _client.join()
    _server.join()
    print(time.time() - n)


def client(rx, ty):
    loop = asyncio.new_event_loop()

    async def node():
        r = await rx.open(loop)
        with ty.send() as t:
            t = await t.open()
            for msg in [*('lol' for _ in range(100000)), 'bye']:
                t.write('{}\n'.format(msg).encode())
                msg = await r.readline()
                msg = msg[:-1].decode()
                # print(msg)

    loop.run_until_complete(node())


def server(rts):
    loop = asyncio.new_event_loop()

    async def handler(r, t):
        r = await r.open(loop)
        with closing(t):
            msg = 'hi'
            while msg != 'bye':
                msg = await r.readline()
                msg = msg[:-1].decode()
                t.write('{}\n'.format(msg).encode())

    tasks = []
    for ry, tx in rts:
        tasks.append(handler(ry, loop.run_until_complete(tx.open(loop))))
    loop.run_until_complete(asyncio.wait(tasks))


if __name__ == '__main__':
    main()
