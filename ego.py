from twofish import Twofish
from sanic import Blueprint
from sanic.exceptions import abort
from sanic.response import json
from functools import wraps
from datetime import datetime, timedelta
import config

T = Twofish(b'*secret*')
blu = Blueprint('ego', url_prefix='/v0.1')


def encrypt(privilege, user, hang, time):
    key = '{}.{}.{}.{}'.format(privilege, user, hang, int(time.timestamp() / 60)).ljust(32)
    return (T.encrypt(key[:16].encode()) + T.encrypt(key[16:].encode())).hex()


print(encrypt('a', 'admin', '', datetime.now()))


def decrypt(key):
    key = bytes.fromhex(key)
    l = (T.decrypt(key[:16]) + T.decrypt(key[16:])).decode().rstrip().split('.')
    if len(l) != 4:
        raise Exception
    return tuple(l)


def privileges(roles):
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            try:
                payload = decrypt(request.form['key'][0] if 'key' in request.form else request.args['key'][0])
            except:
                abort(403, 'not authorized')
            if payload[0] in roles:
                if 'hang' in kwargs and 'user' in kwargs:
                    ban(payload, kwargs['user'], kwargs['hang'])
                if int(payload[3]) > datetime.now().timestamp() / 60 - 8 * 60:
                    return await f(request, payload, *args, **kwargs)
                abort(403, 'your account expired prepare for some credits.')
            abort(403, ' or '.join(roles) + ' required')
        return decorated_function
    return decorator


def ban(payload, user, hang):
    if payload[2] != hang and payload[0] != 'a':
        abort(403, 'you are not in this hang')
    if payload[0] == 'p' and user != payload[1]:
        abort(403, 'access to another porter')


@blu.route('/<hang>/@credit=<credit:int>,@password=<password>', methods=['POST', 'PUT'])
@blu.route('/<hang>/@password=<password>,@credit=<credit:int>', methods=['POST', 'PUT'])
# @blu.route('/<hang>/<user>/@credit=<credit:int>', methods=['POST', 'PUT'])
@privileges({'a'})
async def credit(request, payload, hang, credit, password):
    now = datetime.now()
    await config.users.update_one({
        'user': hang
    }, {
        '$set': {
            '_date': now,
            'hang': hang,
            'user': hang,
            'password': password,
            'privilege': 'b',
            # 'credit': credit,
        },
        '$inc': {'credit': credit}
    }, True, True)
    return json({'SUCCESS': True, 'key': encrypt('b', hang, hang, now), 'password': password}, 201)  # must generate password


@blu.route('/<hang>/<user>/@password=<password>', methods=['GET'])
async def login(request, user, hang, password):
    user = await config.users.aggregate([
        {'$match': {'hang': hang, 'user': user}},
        {'$lookup': {
            'from': "users",
            'localField': "hang",
            'foreignField': "user",
            'as': "boss"
        }},
    ])
    if user and user['boss']['credit'] > 0 and user['password'] == password:
        return json({'SUCCESS': True, 'key': encrypt(user['privilege'], user, hang, datetime.now())}, 200)


@blu.route('/<hang>/<user>/@password=<password>', methods=['POST'])
@privileges({'a', 'b', 'o'})
async def signup(request, payload, user, hang, password):
    # ban(payload, user, hang)
    now = datetime.now()
    await config.users.insert_one({
        '_date': now,
        'hang': hang,
        'user': user,
        'password': password,
        'privilege': 'p'
    })
    return json({'SUCCESS': True, 'key': encrypt('p', user, hang, now)}, 201)


@blu.route('/<hang>/<user>/@password=<password>', methods=['PUT'])
@privileges({'a', 'b', 'o', 'p'})
async def change_password(request, payload, user, hang, password):
    # ban(payload, user, hang)
    result = await config.users.update_one({'hang': hang, 'user': user}, {
        '$set': {
            'password': password
        }
    })
    #### if
    return json({'SUCCESS': True, 'key': encrypt('p', user, hang, datetime.now())}, 202)


@blu.route('/<hang>/<user>/@privilege=<privilege>', methods=['PUT'])
@privileges({'a', 'b', 'o'})
async def _privilege(request, payload, user, hang, privilege):
    # ban(payload, user, hang)
    if ord(payload[0]) >= ord(privilege):
        abort(403)
    result = await config.users.update_one({'hang': hang, 'user': user}, {
        '$set': {
            'privilege': privilege
        }
    })
    if result.modified_count == 0:
        abort(403)
    return json({'SUCCESS': True, 'key': encrypt(privilege, user, hang, datetime.now())}, 202)