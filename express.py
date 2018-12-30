from config import app, wrk
from ego import blu as ego
from motion import blu as motion
from scenario import blu as scenario
from tools.ql import blu as ql
from spy import blu as spy
from client import blu as client
from sanic.response import redirect

app.blueprint(ego)
app.blueprint(scenario)
app.blueprint(ql)
app.blueprint(motion)
app.blueprint(spy)
app.blueprint(client)
app.static('/static', './static')
app.add_route(lambda _: redirect('/static/favicon.png'), '/favicon.ico')

if __name__ == '__main__':
    app.run(host="0.0.0.0", workers=wrk, port=5000)  # , access_log=None, backlog=False)
