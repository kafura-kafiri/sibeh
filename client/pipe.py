from contextlib import closing
from multiprocessing import Process
import asyncio
import time
from aiopipe import aiopipe
import uvloop


async def main(loop):
    rx, tx = aiopipe()
    ry, ty = aiopipe()

    with tx.send() as tx:
        proc = Process(target=child, args=(tx, ry))
        proc.start()

    rx = await rx.open(loop)
    n = time.time()
    with ty.send() as ty:
        ty = await ty.open()
        for msg in [*('why benz why porsche why lens' for i in range(100000)), 'bye']:
            ty.write('{}\n'.format(msg).encode())
            msg = await rx.readline()
            msg = msg[:-1].decode()
            # print('main', msg)
    print(time.time() - n)
    proc.join()


def child(tx, ry):
    loop = asyncio.new_event_loop()
    tx = loop.run_until_complete(tx.open(loop))

    async def handler():
        r = await ry.open(loop)
        with closing(tx):
            msg = 'hi'
            while msg != 'bye':
                msg = await r.readline()
                msg = msg[:-1].decode()
                # print('child:', msg)
                tx.write('{}\n'.format(msg).encode())

    loop.run_until_complete(handler())


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
main_loop = asyncio.get_event_loop()
main_loop.run_until_complete(main(main_loop))
