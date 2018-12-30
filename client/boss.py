import requests
from client import host, admin_key, fastness, tehran
import time
from random import randint
from tools.maths import rnd
from threading import Thread
from datetime import datetime
order_rate = 4  # 1.37
paths = []

requests.delete(host + '/food/!!/shifts', data={'key': admin_key, 'q': '{}'}, verify=False)
requests.delete(host + '/food/!!/paths', data={'key': admin_key, 'q': '{}'}, verify=False)
requests.delete(host + '/food/!!/credits', data={'key': admin_key, 'q': '{}'}, verify=False)

# get a B key
requests.put(host + '/food/mehrad', data={'key': admin_key}, verify=False)
response = requests.post(host + '/food/mehrad/@privilege=b', data={'key': admin_key}, verify=False)
requests.post(host + '/food/mehrad/@credit=1000000', data={'key': admin_key}, verify=False)
b_key = response.text

# print(b_key)


def insertion_loop(key):
    while True:
        # insert orders randomly
        response = requests.post(host + '/food/~{},{};{},{}'.format(*rnd(tehran), *rnd(tehran)), data={
            'key': key,
            'volume': 2,
            'priority': 1,
            'delay': 400
        }, verify=False)
        paths.append(response.json()['_id'])
        time.sleep(randint(1000, 3000) / fastness / order_rate)


Thread(target=insertion_loop, args=(b_key, )).start()


def rebook():
    while True:
        # active porters to porters
        requests.patch(host + '/food', data={'key': b_key}, verify=False)
        # requests.post(host + '/food/@frees', data={'key': b_key})
        requests.post(host + '/food/!!!/hng', data={'key': b_key}, verify=False)
        time.sleep(420 / fastness)


Thread(target=rebook).start()


def grant():
    while True:
        clock = datetime.now()
        clock = clock.hour * 3600 + clock.minute * 60 + clock.second
        # in a while see all requests grant all add a complete shift to each of them.
        users = requests.get(host + "/food/!requests", params={'key': b_key}, verify=False).json()
        print(users)
        for user in users:
            requests.post(host + '/food/{}/@shifts'.format(user), data={'key': b_key}, verify=False)
            requests.post(host + '/food/{}/@shifts={}:{}:{};{}:{}:{}'.format(
                user,
                int((clock + 4) / 3600), int((clock + 4) / 60) % 60, (clock + 4) % 60,
                int((24 * 3600 - 1) / 3600), int((24 * 3600 - 1) / 60) % 60, (24 * 3600 - 1) % 60,
            ), data={'key': b_key, 'fcm': user, 'capacity': 20}, verify=False)
        time.sleep(10)


Thread(target=grant).start()


def beg():
    while True:
        for path in paths:
            location = requests.get(host + '/food/~{}@'.format(path), params={'key': b_key}, verify=False).json()
        time.sleep(5)


# Thread(target=beg).start()
