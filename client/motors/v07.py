import time
from datetime import datetime
from threading import Thread
import requests
from client import host, tehran, osrm_host
from tools.maths import rnd
from random import randint


class Motor:
    def __init__(self, name, key, lat, lng, hang='food', fastness=1):
        self.name = name
        self.key = key
        self.hang = hang
        self.fastness = fastness
        self.location = [lat, lng]
        self.route = None
        self.thread = Thread(target=self.play)
        self.msg_box = []
        self.s = 0
        self.n = 0
        self.points = []

    def shift(self, head, tail):
        requests.post(host + '/{}/{}@shifts={}:{}:{};{}:{}:{}'.format(
            self.hang, self.name,
            int(head / 3600), int(head / 60) % 60, head % 60,
            int(tail / 3600), int(tail / 60) % 60, tail % 60,
        ), data={'key': self.key, 'fcm': self.name, 'capacity': 20})

    # after active porters to white_db -> have to send location(not for random solver)
    def ack_location(self):
        requests.post(host + '/{}/{}/@{},{}{}'.format(self.hang, self.name, *self.location, '/~' + ';'.join(self.points) if self.points else ''), data={'key': self.key}, timeout=2)

    def dst(self, dst):
        self.route = requests.get(osrm_host + '/route/v1/driving/{},{};{},{}'.format(
            self.location[1], self.location[0], dst[1], dst[0]
        ), params={'steps': 'true'}).json()
        self.route = self.route['routes'][0]['legs'][0]['steps']
        self.route = [{
            'destination': [step['maneuver']['location'][1], step['maneuver']['location'][0]],
            'duration': step['duration'],
            'distance': step['distance'],
        } for step in self.route]

    def play(self):
        while True:
            if not self.route:
                if self.msg_box and self.msg_box[0]['points']:
                    points = self.msg_box[0]['points']
                    if not self.points:
                        self.points = list(set(p['_id'] for p in points))
                    self.msg_box[0]['points'] = points[1:]
                    self.dst(points[0]['location'])
                else:
                    if self.msg_box:
                        while True:
                            try:
                                requests.post(host + '/food/~{}/@done'.format(self.msg_box[0]['_id']), data={'key': self.key})
                                self.points = []
                                break
                            except: time.sleep(1)
                        self.msg_box = self.msg_box[1:]
                        self.n += 1
                    # print("-- {}'s current path finished -- let's wait here.".format(self.name))
            if self.route:
                self.move()
            self.ack_location()
            time.sleep(30 / self.fastness)

    def move(self):
        ammo = 30
        self.s += ammo
        while ammo and self.route:
            step = self.route[0]
            if ammo >= step['duration']:
                self.location = step['destination']
                ammo -= step['duration']
                self.route = self.route[1:]
            else:
                duration = step['duration']
                step['duration'] -= ammo
                step['distance'] *= step['duration'] / duration
                self.location[0] += (step['destination'][0] - self.location[0]) * ammo / duration
                self.location[1] += (step['destination'][1] - self.location[1]) * ammo / duration
                ammo = 0
        self.s -= ammo
        # can set remain for ammo_remain for next turn


if __name__ == '__main__':
    m = Motor('ali', '12', 31, 53, hang='food', fastness=48)
    m.re_shift()
    # let's test
