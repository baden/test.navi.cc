#!/bin/env python

from pymongo import MongoClient
from bson import Binary
import gridfs

import sys
import time

if sys.platform == "win32":
    profiler_timer = time.clock     # On Windows, the best timer is time.clock()
else:
    profiler_timer = time.time      # On most other platforms the best timer is time.time()


connection = MongoClient()     # Single connection for all instanses
db = connection['test_bingps']

bingps = db['bingps']
bingps.ensure_index([("imei", 1), ("dt", 1)])
bingps.drop()

#filesystem = gridfs.GridFS(db, collection='bingps_fs')
#filesystem.put('123213', filename='1_1')


TRACKERS = 100
REPEATS = 100

print('Start test')

start = profiler_timer()

for t in range(REPEATS):
    for imei in range(TRACKERS):
        """
        point = {
            "dt": t,
            "lat": 12343434,
            "lon": 23415145,
            "speed": 23.2,
            "alt": 2123.5,
            "fsource": 5,
            "in1": 0,
            "in2": 2,
            "in3": 1,
            "ign": False,
            "case": True
        }
        """
        point = Binary("01234567890123456789012345678901"*400)
        bingps.update(
            {
                'imei': str(imei),
                'dt': t // 60*60
            },
            {
                '$push': {
                    'data': point
                }
            },
            True
        )

duration = profiler_timer() - start

print("Test result")
print(" Duration: {}".format(duration))
print(" Push/sec: {}".format(TRACKERS*REPEATS/duration))

