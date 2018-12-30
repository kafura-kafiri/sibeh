import logging
from datetime import datetime
from sanic import Sanic
from sanic.response import json
import requests
from sanic_cors import CORS
from ast import literal_eval
from client import host


class MyFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s,%03d" % (t, record.msecs)
        return s
    converter = datetime.fromtimestamp


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console = logging.FileHandler('simulation.log')
console.setLevel(logging.DEBUG)
logger.addHandler(console)

formatter = MyFormatter(fmt='%(asctime)s %(message)s', datefmt='%Y-%m-%d,%H:%M:%S.%f')
console.setFormatter(formatter)

logger.debug('/*******************************\\')
logger.debug('   {}'.format(datetime.now()))
logger.debug('\\*******************************/')


app = Sanic(__name__)
CORS(app)
motors = {}
paths = []
os = []


@app.route('/key')
async def key(request):
    return json({'key': os[0]})


@app.route('/<motor>', methods=['POST'])
async def msg(request, motor):
    path = literal_eval(request.form['path'][0])
    paths.append(path['_id'])
    requests.post(host + '/food/~{}/@ack'.format(path['_id']), data={'key': motors[motor].key})
    path['points'] = list(reversed(path['points']))
    motors[motor].msg_box.append(path)
    logger.critical("porter: {}, path: {}".format(motor, request.form['path'][0]))
    return json({
        'SUCCESS': True
    })
