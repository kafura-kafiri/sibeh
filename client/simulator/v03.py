import time
from random import randint
from threading import Thread
import requests
from tools.maths import rnd
from client.motors.v07 import Motor
from client import host, tehran, admin_key, fastness
from static.names import names
from client.simulator import motors, app, logger, paths, os
from sanic.response import json

b_key = None
order_rate = 1.37
name_index = 50


# 2011-06-09,07:12:36.553554 Jackdaws love my big sphinx of quartz.
def insertion_loop(operator, key):
    while True:
        requests.post(host + '/food/~{},{};{},{}'.format(*rnd(tehran), *rnd(tehran)), data={
            'key': key,
            'volume': 2,
            'priority': 1,
            'delay': 400
        }, timeout=2)
        time.sleep(randint(1000, 3000) / fastness / order_rate)


def forge():
    requests.delete(host + '/!!/food/locations', data={'key': admin_key, 'q': '{}'})
    requests.delete(host + '/!!/food/paths', data={'key': admin_key, 'q': '{}'})
    requests.delete(host + '/!!/food/users', data={'key': admin_key, 'q': '{}'})

    response = requests.post(host + '/food/@credit=2,@password=123', data={'key': admin_key})
    b_key = response.json()['key']

    for name in names[:5]:
        requests.post(host + '/food/{}/@password=123'.format(name), data={'key': b_key})
        response = requests.put(host + '/food/{}/@privilege=o'.format(name), data={'key': b_key})
        os.append((name, response.json()['key']))
        Thread(target=insertion_loop, args=os[-1]).start()

    for name in names[40: 48]:
        motors[name] = Motor(name, requests.post(host + '/food/{}/@password=123'.format(name),
                                                 data={'key': os[randint(0, len(os) - 1)][1]}).json()['key']
                             , *rnd(tehran), hang='food', fastness=fastness)
        motors[name].thread.start()

    def rebook():
        while True:
            response = requests.post(host + '/!!/food/porters/@frees', data={'key': b_key})
            if response.json():
                logger.info(response.text)
            requests.post(host + '/food/!!!/hng', data={'key': b_key})
            time.sleep(420 / fastness)

    Thread(target=rebook).start()

    # 1. each 10sec / fastness each operator will ask location of all porters and orders.

    # def beg():
    #     while True:
    #         try:
    #             for path in set(paths):
    #                 location = requests.get(host + '/food/~{}@'.format(path), params={'key': b_key}).json()
    #                 if location['date'] and location['lat'] and location['lng']:
    #                     logger.info("path: {} -> {}".format(path, str(location)))
    #                 else:
    #                     logger.info("-- path removed --")
    #                     paths.remove(path)
    #         except: pass
    #         time.sleep(5)
    # Thread(target=beg).start()


@app.route('/@<lat>,<lng>', methods=['GET'])
async def new_motor(request, lat, lng):
    lat = float(lat)
    lng = float(lng)
    global name_index
    motors[names[name_index]] = Motor(names[name_index], requests.post(host + '/food/{}/@password=123'.format(names[name_index]),
                                             data={'key': os[randint(0, len(os) - 1)][1]}).json()['key']
                         , lat, lng, hang='food', fastness=fastness)
    motors[names[name_index]].thread.start()
    name_index += 1
    return json({'Success': True})

if __name__ == '__main__':
    forge()
    app.run(host='0.0.0.0', port=5002)
