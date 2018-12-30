import numpy as np
import json
from bson import ObjectId
from datetime import datetime

parse_location = lambda location: [float(word.replace('%20', " ").strip()) for word in location.split(',')]
parse_path = lambda path: np.ravel([parse_location(word) for word in path.split(';')])
points = lambda ps: ';'.join(['{},{}'.format(*reversed(p['points'][-1]['location'])) for p in ps])


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId) or isinstance(o, datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)
