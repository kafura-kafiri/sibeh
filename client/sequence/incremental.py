import requests
from sanic import Sanic
from sanic.response import text
from client import host, tehran, admin_key
from tools.maths import rnd
import time
from multiprocessing import Process, Manager
from ast import literal_eval
app = Sanic(__name__)
matches = Manager().list()
version = '/v0.1'
host += version


@app.route('/<motor>', methods=['POST'])
def msg(request, motor):
    matches.append((motor, literal_eval(request.form['path'][0])))
    return text('Hello, World!')


client_server = Process(target=app.run, kwargs={'port': 5002}).start()

requests.delete(host + '/!!/food/locations', data={'key': admin_key, 'q': '{}'})
requests.delete(host + '/!!/food/paths', data={'key': admin_key, 'q': '{}'})
requests.delete(host + '/!!/food/users', data={'key': admin_key, 'q': '{}'})

# get a B key
response = requests.post(host + '/food/@credit=2,@password=123', data={'key': admin_key})
b_key = response.json()['key']
print(b_key)

# get two O key
requests.post(host + '/food/adam/@password=123', data={'key': b_key})
requests.post(host + '/food/eve/@password=123', data={'key': b_key})

response = requests.put(host + '/food/adam/@privilege=o', data={'key': b_key})
adam = response.json()['key']
response = requests.put(host + '/food/eve/@privilege=o', data={'key': b_key})
eve = response.json()['key']

# get 3 P key ->

response = requests.post(host + '/food/abel/@password=123', data={'key': adam})
abel = response.json()['key']
response = requests.post(host + '/food/cain/@password=123', data={'key': eve})
cain = response.json()['key']
response = requests.post(host + '/food/seth/@password=123', data={'key': eve})
seth = response.json()['key']

# insert paths randomly
response = requests.post(host + '/food/~{},{};{},{}'.format(*rnd(tehran), *rnd(tehran)), data={
    'key': adam,
    'volume': 2,
    'priority': 1,
    'delay': 400
})
print(response.json()['_id'])

response = requests.post(host + '/food/~{},{};{},{}'.format(*rnd(tehran), *rnd(tehran)), data={
    'key': eve,
    'volume': 5,
    'priority': 6,
    'delay': 1300
})
print(response.json()['_id'])

response = requests.post(host + '/food/~{},{};{},{}'.format(*rnd(tehran), *rnd(tehran)), data={
    'key': adam,
    'volume': 17,
    'priority': 2,
})
print(response.json()['_id'])

requests.post(host + '/food/abel/@{},{}'.format(*rnd(tehran)), data={'key': abel}, verify=False)

requests.post(host + '/food/!!!/grd', data={'key': b_key})

response = requests.get(host + '/food/abel/@', params={'key': adam})
print(response.text)
response = requests.get(host + '/food/~{}/@'.format(matches[0][1]['_id']), params={'key': adam})
print(response.text)

time.sleep(.1)
print(matches)
response = requests.post(host + '/food/~{}/@ack'.format(';'.join(p['_id'] for p in matches[0][1]['points'])), data={'key': abel})

response = requests.get(host + '/food/abel/@', params={'key': adam})
print(response.text)
response = requests.get(host + '/food/~{}/@'.format(matches[0][1]['_id']), params={'key': adam})
print(response.text)

print(host + '/food/abel/@{},{}/~{}'.format(*rnd(tehran), matches[0][1]['_id']))
print(abel)
requests.post(host + '/food/abel/@{},{}/~{}'.format(*rnd(tehran), matches[0][1]['_id']), data={'key': abel}, verify=False)
response = requests.get(host + '/food/abel/@', params={'key': adam})
print(response.text)
response = requests.get(host + '/food/~{}/@'.format(matches[0][1]['_id']), params={'key': adam})
print(response.text)

response = requests.post(host + '/food/~{}/@at'.format(matches[0][1]['_id']), data={'key': abel})
print(response.text)

requests.post(host + '/food/abel/@{},{}/~{}'.format(*rnd(tehran), matches[0][1]['_id']), data={'key': abel}, verify=False)
response = requests.get(host + '/food/abel/@', params={'key': adam})
print(response.text)
response = requests.get(host + '/food/~{}/@'.format(matches[0][1]['_id']), params={'key': adam})
print(response.text)

response = requests.post(host + '/food/~{}/@done'.format(matches[0][1]['_id']), data={'key': abel})
print(response.text)

requests.post(host + '/food/abel/@{},{}'.format(*rnd(tehran)), data={'key': abel}, verify=False)
response = requests.get(host + '/food/abel/@', params={'key': adam})
print(response.text)
response = requests.get(host + '/food/~{}/@'.format(matches[0][1]['_id']), params={'key': adam})
print(response.text)
