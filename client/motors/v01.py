import time
from datetime import datetime
from threading import Thread

import requests
from client import fastness, host, gmaps, tehran
from tools.maths import rnd


class Motor:
    def __init__(self, name, lat, lng, company='food'):
        self.name = name
        self.company = company
        self.location = [lat, lng]
        self.route = None
        self.thread = Thread(target=self.play)

    def ack_location(self):
        requests.get('{}/{}/@{},{}'.format(host, self.name, *self.location))

    def dst(self):
        while not self.route:
            dst = rnd(tehran)
            self.route = gmaps.directions(self.location, dst,
                                          # mode="transit",
                                          departure_time=datetime.now())
        self.route = self.route[0]['legs'][0]['steps']
        self.route = [{
            'destination': [step['end_location']['lat'], step['end_location']['lng']],
            'duration': step['duration']['value'],
            'distance': step['distance']['value'],
        } for step in self.route]

    def move(self):
        ammo = 30
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
        # can set remain for ammo_remain for next turn

    def play(self):
        while True:
            if not self.route:
                print("-- {}'s current route finished --".format(self.name))
                self.dst()
            self.move()
            self.ack_location()
            time.sleep(30 / fastness)


if __name__ == '__main__':
    motors = [Motor(name, *rnd(tehran)) for name in [
        'shahin',
        'alireza',
        'mehrad',
        'mohsen',
        'novid',
        'mohammad',
        'naqi',
        'taqi',
        'javad',
        'kazem',

        'nosrat',
        'effat',
        'shokat',
        'sakineh',
        'halimeh',
        'naemeh',
        'maryam',
        'zahra',
        'narjes',
        'zeynab',

        'bil',
        'jack',
        'muses',
        'nick',
        'liam',
        'william',
        'james',
        'benjamin',
        'mason',
        'logan',

        'iris',
        'zeus',
        'hera',
        'poseidon',
        'demeter',
        'ares',
        'athena',
        'apollo',
        'hermes',
        'artemis',

        'thor',
        'odin',
        'ironman',
        'vision',
        'hulk',
        'thanos',
        'superman',
        'captain',
        'spiderman',
        'flash'
    ]]
    for motor in motors:
        motor.thread.start()
