from client import host, tehran, admin_key
import requests
# from tools.ego import decrypt
from tools.maths import rnd
from datetime import datetime, timedelta
import time
from flask import Flask, request
import threading
from ast import literal_eval

app = Flask(__name__)
matches = []


@app.route('/<motor>', methods=['POST'])
def msg(motor):
    matches.append((motor, literal_eval(request.values['path'])))
    return 'Hello, World!'


client_server = threading.Thread(target=app.run, kwargs={'port': 5002})
client_server.start()

'''
        solve() -> notification list -> (two extra end point for test (retrieve msg for this porter))
            for each P: retrieve msgs -> ack path ->
                with google map| osrm: make route -> move -> send location -> at -> done

        request for each path location
'''

requests.post(host + '/!flush', data={'key': admin_key}, verify=False)
requests.delete(host + '/food/!!/shifts', data={'key': admin_key, 'q': '{}'}, verify=False)
requests.delete(host + '/food/!!/paths', data={'key': admin_key, 'q': '{}'}, verify=False)
requests.delete(host + '/food/!!/credits', data={'key': admin_key, 'q': '{}'}, verify=False)
# get a B key
requests.put(host + '/food/mehrad', data={'key': admin_key}, verify=False)
response = requests.post(host + '/food/mehrad/@privilege=b', data={'key': admin_key}, verify=False)
requests.post(host + '/food/mehrad/@credit=10', data={'key': admin_key}, verify=False)
b_key = response.text
time.sleep(.3)

# get 3 P key ->

p_key = requests.put(host + '/food/mohsen', data={'key': b_key}, verify=False).text

clock = datetime.now()
clock = clock.hour * 3600 + clock.minute * 60 + clock.second

requests.post(host + '/food/mohsen/@shifts={}:{}:{};{}:{}:{}'.format(
    int((clock) / 3600), int((clock) / 60) % 60, (clock) % 60,
    int((24 * 3600 - 1) / 3600), int((24 * 3600 - 1) / 60) % 60, (24 * 3600 - 1) % 60,
), data={'key': b_key, 'fcm': 'mohsen', 'capacity': 20}, verify=False)

# insert orders randomly
requests.post(host + '/food/~{},{};{},{}'.format(*rnd(tehran), *rnd(tehran)), data={
    'key': b_key,
    'volume': 2,
    'priority': 1,
    'delay': 400
}, verify=False)

requests.post(host + '/food/~{},{};{},{}'.format(*rnd(tehran), *rnd(tehran)), data={
    'key': b_key,
    'volume': 5,
    'priority': 6,
    'delay': 1300
}, verify=False)

time.sleep(.5)
requests.patch(host + '/food', data={'key': b_key}, verify=False)

# send some random location. for mohsen.
requests.post(host + '/food/mohsen/@{},{}'.format(*rnd(tehran)), data={'key': p_key}, verify=False)

# solve
requests.post(host + '/food/!!!/test_batch/simulator', data={'key': b_key}, verify=False)
#
# wait for ack
time.sleep(.5)
points = matches[0][1]['points']
ps = {}
for p in reversed(points):
    if 'volume' in p:
        ps[p['_id']] = len(ps)
points = [p['_id'] if 'volume' in p else '${}'.format(ps[p['_id']]) for p in reversed(points)]
response = requests.post(host + '/food/~{}/@ack'.format(';'.join(points)), data={'key': p_key}, verify=False)
# get path location
response = requests.get(host + '/food/~{}/@'.format(points[0]), params={'key': b_key}, verify=False)
print(points[0])
print(response.text)

response = requests.get(host + '/food/mohsen/@', params={'key': b_key}, verify=False)
print(response.text)

response = requests.post(host + '/food/~{}/@done'.format(matches[0][1]['_id']), data={'key': p_key}, verify=False)

