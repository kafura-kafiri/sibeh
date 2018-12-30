from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly
import numpy as np
from sanic import Blueprint
from sanic.response import json
from datetime import datetime, timedelta
from tools.pqdict import pqdict
import config


blu = Blueprint('spy', url_prefix='/v0.1/!')
q = pqdict(key=lambda x: x[1])
zoom = 2
key = lambda _lat, _lng: '{},{}'.format("%.{}f".format(zoom) % _lat, "%.{}f".format(zoom) % _lng)


@blu.route('/@<lat>,<lng>')
async def height(request, lat, lng):
    return json({'altitude': int(h(float(lat), float(lng)))})


@blu.route('/<hang>/<user>/<back_head:int>:<back_tail:int>')
@blu.route('/<hang>/<user>/<back_head:int>')
async def alt_spy(request, user, hang, back_head, back_tail=0):
    now = datetime.now()
    back_head = now - timedelta(hours=back_head)
    back_tail = now - timedelta(hours=back_tail)
    _locations = await config.locations.find({
        'hang': hang,
        'user': user,
        '_date': {
            '$lte': back_head,
            '$gt': back_tail
        },
        'altitude': {'$exists': True}
    })
    n = 0
    s = 0
    for location in _locations:
        s += (h(*location['location']) - location['altitude']) ** 2
        n += 1
    deviation = 0 if n == 0 else (s / n) ** .5
    return json({'deviation': deviation})


def _2csv(file, z=0):
    """
    url: http://dwtkns.com/srtm30m/
    :param file:
    :param z:
    :return:
    """
    def _zoom(arr, zz, _lat, _lng):
        if z == zz:
            return np.save(directory + '/{}.npy'.format(key(_lat, _lng)), arr)
        arr = np.split(arr, 2, axis=0)
        arr = [*np.split(arr[0], 2, axis=1), *np.split(arr[1], 2, axis=1)]
        zz += 1
        for i, a in enumerate(arr):
            _zoom(a, zz, _lat + int(i / 2) * 2 ** -zz, _lng + (i % 2) * 2 ** -zz)
    lat, lng = file.split('E')
    lat, lng = int(lat[1:]), int(lng)
    directory = 'static/tiles/'
    raster = gdal.Open(directory + file + '.hgt', GA_ReadOnly)
    heights = raster.GetRasterBand(1).ReadAsArray()[:-1, :-1]
    _zoom(heights, 0, lat, lng)


def h(lat, lng):
    lat = 2 * int(lat) + 1 - lat - .00000001
    f_lat, f_lng = lat % 2 ** -zoom, lng % 2 ** -zoom
    lat -= f_lat - .000000001
    lng -= f_lng - .000000001
    _key = key(lat, lng)
    if _key not in q:
        q[_key] = np.load('static/tiles/{}.npy'.format(_key)), datetime.now()
        if len(q) > 128:
            q.pop()

    return q[_key][0][int(f_lat * 3600), int(f_lng * 3600)]

