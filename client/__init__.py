from sanic import Blueprint
from sanic.response import html
import jinja2
import os.path
# import googlemaps
#
# gmaps = googlemaps.Client(key='AIzaSyCDlOOdPKWiM3fzXGLyX0kFs49rt4_WPHA')
fastness = 24
host = 'http://localhost:5000'
version = '/v0.1'
host += version
osrm_host = 'http://localhost:6000'
# manually get an A key ->
admin_key = '73e32c378a77b18cbf4307f3f218eeb6d4522e4874b0c43b62cd9dcf1ff5704b'

tehran = [
    [35.788158, 51.328564],
    [35.766610, 51.263318],
    [35.732402, 51.205000],
    [35.682704, 51.229829],
    [35.614201, 51.374178],
    [35.617017, 51.470026],
    [35.692083, 51.493699],
    [35.790657, 51.491336],
]

step = {
    'intersections': [
        {'out': 0, 'entry': [True], 'bearings': [277], 'location': [51.42381, 35.662129]},
        {'out': 2, 'location': [51.423373, 35.662172], 'bearings': [45, 90, 270], 'entry': [True, False, True], 'in': 1},
        {'out': 1, 'location': [51.423049, 35.662203], 'bearings': [90, 285], 'entry': [False, True], 'in': 0}
    ],
    'driving_side': 'right',
    'geometry': 'igtxEyuzxHGvAE~@ETCH',
    'mode': 'driving',
    'duration': 14.1,
    'maneuver': {
        'bearing_after': 277,
        'type': 'depart',
        'modifier': 'right',
        'bearing_before': 0,
        'location': [51.42381, 35.662129]
    },
    'weight': 14.1, 'distance': 85.1,
    'name': 'رضا نصیری'
}


blu = Blueprint(__name__, url_prefix='/v0.1/client')
templates = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath=os.path.dirname(__file__) + '/templates/'), auto_reload=True)
app = templates.get_template("app.html")
demo = templates.get_template("demo.html")


@blu.route('/app')
async def _app(request):
    return html(app.render(map_api_key='AIzaSyDvQr0q3jxqbAv4ju68H9H8YEMJBmXZGl0'))


@blu.route('/demo')
async def _demo(request):
    return html(templates.get_template("demo.html").render())
