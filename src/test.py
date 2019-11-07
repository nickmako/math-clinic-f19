# Testing ground
from functools import reduce
from matching import calc_DP_pairs
from location import *
import matplotlib.pyplot as plt

with open('../data/sample1/jobs.csv', 'rb') as f:
    data = [line[:-1].decode('utf-8').split(',') for line in f][1:]

landfills  = [Landfill.from_csv(l) for l in data if l[6] == "S"]
deliveries = [ServiceSite.from_csv(d) for d in data if d[6] == "D"]
pickups    = [ServiceSite.from_csv(p) for p in data if p[6] == "P"]
switches   = [ServiceSite.from_csv(s) for s in data if s[6] == "AA"]

jobs = deliveries + pickups + switches

for j in jobs:
    j.calc_nearest_landfill(landfills)

# triangles
pairs1 = calc_DP_pairs(list(deliveries), list(pickups), same_landfill=False)
pairs2 = calc_DP_pairs(list(deliveries), list(pickups), same_landfill=True)

# jobs which don't appear in triangles
non_stars1 = [d for (d,p) in pairs1] + [p for (d,p) in pairs1]
star_jobs1 = [j for j in jobs if j not in non_stars1] 

non_stars2 = [d for (d,p) in pairs2] + [p for (d,p) in pairs2]
star_jobs2 = [j for j in jobs if j not in non_stars2] 

# total route sums
s1 = reduce(lambda a,b: a+b,\
        [distance(j.nearest_landfill,j) + \
         distance(j,j.nearest_landfill) for j in star_jobs1])
s1 += reduce(lambda a,b: a+b,\
        [distance(d.nearest_landfill,d) + distance(d,p) +\
         distance(p,p.nearest_landfill) for (d,p) in pairs1])

s2 = reduce(lambda a,b: a+b,\
        [distance(j.nearest_landfill,j) + \
         distance(j,j.nearest_landfill) for j in star_jobs2])
s2 += reduce(lambda a,b: a+b,\
        [distance(d.nearest_landfill,d) + distance(d,p) +\
         distance(p,p.nearest_landfill) for (d,p) in pairs2])

s3 = reduce(lambda a,b: a+b,\
        [distance(j.nearest_landfill,j) + \
         distance(j,j.nearest_landfill) for j in jobs])

print("%.1f, %.1f%% saved" % (s1, 100 - float(100*s1)/s3))
print("%.1f, %.1f%% saved" % (s2, 100 - float(100*s2)/s3))
print("%.1f" % s3)

# plotting

for j in jobs:
    plt.plot([j.lonlat[0], j.nearest_landfill.lonlat[0]], [j.lonlat[1],
        j.nearest_landfill.lonlat[1]], 'grey', linestyle=":", linewidth=1)

for p in pairs1:
    plt.plot([p[0].lonlat[0], p[1].lonlat[0]], [p[0].lonlat[1], p[1].lonlat[1]], color='black', linewidth=3)

for p in pairs2:
    plt.plot([p[0].lonlat[0], p[1].lonlat[0]], [p[0].lonlat[1], p[1].lonlat[1]], color='cyan', linewidth=1)

for d in deliveries:
    plt.plot(d.lonlat[0], d.lonlat[1], 'go', markersize=3)

for p in pickups:
    plt.plot(p.lonlat[0], p.lonlat[1], 'ro', markersize=3)

for s in switches:
    plt.plot(s.lonlat[0], s.lonlat[1], 'mo', markersize=3)

for l in landfills:
    plt.plot(l.lonlat[0], l.lonlat[1], 'bo', markersize=7)

plt.show()
