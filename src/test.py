# Testing ground
from random import random
from functools import reduce
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

# triangles
pairs1 = calc_DP_pairs(list(jobs), same_landfill=False)
pairs2 = calc_DP_pairs(list(jobs), same_landfill=True)

# jobs which don't appear in triangles
non_stars1 = [x for (x,y) in pairs1] + [y for (x,y) in pairs1]
star_jobs1 = filter(lambda x: x not in non_stars1, jobs)

non_stars2 = [x for (x,y) in pairs2] + [y for (x,y) in pairs2]
star_jobs2 = filter(lambda x: x not in non_stars2, jobs)

# total route sums
s1 = reduce(lambda a,b: a+b, map(lambda x: distance(x.nearest_landfill,x) + \
        distance(x,x.nearest_landfill),  star_jobs1))
s1 += reduce(lambda a,b: a+b, map(lambda x:\
    distance(x[0].nearest_landfill,x[0]) + distance(x[0],x[1]) +\
    distance(x[1],x[1].nearest_landfill), pairs1))

s2 = reduce(lambda a,b: a+b, map(lambda x: distance(x.nearest_landfill,x) + \
        distance(x,x.nearest_landfill),  star_jobs2))
s2 += reduce(lambda a,b: a+b, map(lambda x:\
    distance(x[0].nearest_landfill,x[0]) + distance(x[0],x[1]) +\
    distance(x[1],x[1].nearest_landfill), pairs2))

s3 = reduce(lambda a,b: a+b, map(lambda x: distance(x.nearest_landfill,x) + \
        distance(x,x.nearest_landfill), jobs))

print(s1)
print(s2)
print(s3)

# plotting
plt.plot([0,10], [5, 5], color='grey')
plt.plot([5,5], [0, 10], color='grey')

for j in jobs:
    plt.plot([j.address[0], j.nearest_landfill.address[0]], [j.address[1],
        j.nearest_landfill.address[1]], 'grey', linestyle=":", linewidth=1)

for p in pairs1:
    plt.plot([p[0].address[0], p[1].address[0]], [p[0].address[1], p[1].address[1]], color='black', linewidth=3)

for p in pairs2:
    plt.plot([p[0].address[0], p[1].address[0]], [p[0].address[1], p[1].address[1]], color='cyan', linewidth=1)

for d in deliveries:
    plt.plot(d.address[0], d.address[1], 'go', markersize=3)

for p in pickups:
    plt.plot(p.address[0], p.address[1], 'ro', markersize=3)

for s in switches:
    plt.plot(s.address[0], s.address[1], 'mo', markersize=3)

for l in landfills:
    plt.plot(l.address[0], l.address[1], 'bo', markersize=7)

plt.show()
