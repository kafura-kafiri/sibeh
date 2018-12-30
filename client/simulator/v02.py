import logging
import threading
import time
from ast import literal_eval
from random import randint
from threading import Thread

import requests

from tools.maths import rnd
from client.motors.v04 import Motor
from datetime import datetime
from client import host, tehran, admin_key, fastness
from static.names import names


class MyFormatter(logging.Formatter):
    converter = datetime.fromtimestamp

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s,%03d" % (t, record.msecs)
        return s


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# console = logging.StreamHandler()
# logger.addHandler(console)

console = logging.FileHandler('simulation.log')
console.setLevel(logging.DEBUG)
logger.addHandler(console)

formatter = MyFormatter(fmt='%(asctime)s %(message)s', datefmt='%Y-%m-%d,%H:%M:%S.%f')
console.setFormatter(formatter)

logger.debug('/*******************************\\')
logger.debug('   {}'.format(datetime.now()))
logger.debug('\\*******************************/')
# 2011-06-09,07:12:36.553554 Jackdaws love my big sphinx of quartz.

app = Flask(__name__, template_folder='../client')
motors = {}
order_rate = 1.37
paths = []


@app.route('/<motor>', methods=['POST'])
def msg(motor):
    path = literal_eval(request.values['path'])
    paths.append(path['_id'])
    requests.post(host + '/food/~{}@ack'.format(path['_id']), data={'key': motors[motor].key})
    motors[motor].msg_box.append(path)
    logger.critical("porter: {}, path: {}".format(motor, request.values['path']))
    return jsonify({
        'SUCCESS': True
    })


@app.route('/')
def _map():
    return render_template('simulation.html', key=b_key, host=host, hang='food')


client_server = threading.Thread(target=app.run, kwargs={'port': 5002})
client_server.start()

while True:
    try:
        requests.delete(host + '/food/!!/shifts', data={'key': admin_key, 'q': '{}'})
        requests.delete(host + '/food/!!/paths', data={'key': admin_key, 'q': '{}'})
        requests.delete(host + '/food/!!/credits', data={'key': admin_key, 'q': '{}'})

        # get a B key
        requests.put(host + '/food/mehrad', data={'key': admin_key})
        response = requests.post(host + '/food/mehrad@privilege=b', data={'key': admin_key})
        requests.post(host + '/food/mehrad@credit=1000000', data={'key': admin_key})
        b_key = response.text
        break

    except:
        time.sleep(2)
        print('next try about 2secs later')

# some operators -> start inserting randomly


def insertion_loop(operator, key):
    while True:
        # insert orders randomly
        requests.post(host + '/food/~{},{};{},{}'.format(*rnd(tehran), *rnd(tehran)), data={
            'key': key,
            'volume': 2,
            'priority': 1,
            'delay': 400
        }, timeout=2)
        time.sleep(randint(1000, 3000) / fastness / order_rate)


for o in [[name, None] for name in ]:
    while True:
        try:
            requests.put(host + '/food/{}'.format(o[0]), data={'key': b_key})
            response = requests.post(host + '/food/{}@privilege=o'.format(o[0]), data={'key': b_key})
            o[1] = response.text
            thread = Thread(target=insertion_loop, args=tuple(o))
            thread.start()
            break
        except:
            time.sleep(1)


clock = datetime.now()
clock = clock.hour * 3600 + clock.minute * 60 + clock.second
for name in :
    while True:
        try:
            motors[name] = Motor(name, requests.put(host + '/food/{}'.format(name), data={'key': b_key}).text,
                                 *rnd(tehran), hang='food', fastness=fastness)
            motors[name].shift(clock + 6, 24 * 3600 - 1)
            # motors[name].shift(clock + 20, clock + 40)
            motors[name].thread.start()
            break
        except:
            time.sleep(1)

# fastness = 24 () -> periods in ego -> hour = 1

def rebook():
    while True:
        try:
            # active porters to porters
            requests.patch(host + '/food', data={'key': b_key})

            response = requests.post(host + '/food/@frees', data={'key': b_key})
            if response.json():
                logger.info(response.text)
            # # solve
            requests.post(host + '/food/!!!/hng', data={'key': b_key})
        except: pass
        time.sleep(420 / fastness)

rebook_thread = Thread(target=rebook)
rebook_thread.start()

# 1. each 10sec / fastness each operator will ask location of all porters and orders.


def beg():
    while True:
        try:
            for path in set(paths):
                location = requests.get(host + '/food/~{}@'.format(path), params={'key': b_key}).json()
                if location['date'] and location['lat'] and location['lng']:
                    logger.info("path: {} -> {}".format(path, str(location)))
                else:
                    logger.info("-- path removed --")
                    paths.remove(path)
        except: pass
        time.sleep(5)


begging_thread = Thread(target=beg)
begging_thread.start()


def report():
    while True:
        n = 0
        s = 0
        for name, motor in motors.items():
            n += motor.n
            s += motor.s
        print('-- {}m have gone for {} finished paths --'.format(s, n))
        time.sleep(60)


report_thread = Thread(target=report)
report_thread.start()
