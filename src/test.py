# Testing ground
from random import random
from matching import calc_DP_pairs
from location import *
import matplotlib.pyplot as plt

def rand_site():
    r = random()
    if r <= .1:
        service = "S"
    elif r <= .55:
        service = "D"
    else:
        service = "P"

    r = random()
    if r <= .1:
        time = "AM"
    elif r <= .2:
        time = "PM"
    else:
        time = "ANY"

    return ServiceSite((10*random(), 10*random()), "", "",  service_time=time, can_size="", name="", service_type=service)


landfills = [Landfill((x,y), "", "", "", "") for x in [2.5,7.5] for y in [2.5, 7.5]]
jobs = [rand_site() for x in range(100)]

for j in jobs:
    j.calc_nearest_landfill(landfills)

deliveries = filter(lambda x: x.service_type == "D", jobs)
pickups    = filter(lambda x: x.service_type == "P", jobs)
switches   = filter(lambda x: x.service_type == "S", jobs)

pairs = calc_DP_pairs(jobs)

for p in pairs:
    plt.plot([p[0].address[0], p[1].address[0]], [p[0].address[1], p[1].address[1]], color='black')

for d in deliveries:
    plt.plot(d.address[0], d.address[1], 'go', markersize=3)

for p in pickups:
    plt.plot(p.address[0], p.address[1], 'ro', markersize=3)

for s in switches:
    plt.plot(s.address[0], s.address[1], 'mo', markersize=3)

for l in landfills:
    plt.plot(l.address[0], l.address[1], 'bo', markersize=7)


plt.show()
