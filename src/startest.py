from location import *
from matching import *


def transition(nodesf, nodef):
    temp = tranindex = tranindex1 = 0
    trancost = 10000
    for z in alljobs:
        if z[0].used != 1:
            temp = distance(z[0], landfills[nodesf])+distance(z[1], landfills[nodef])-distance(z[0], z[0].nearest_landfill) - distance(z[1], z[1].nearest_landfill)
        else:
            temp = 10000
        if temp < trancost:
            trancost = temp
            tranindex = z
    tranindex[0].transition_cost = distance(tranindex[0], landfills[nodesf])+distance(tranindex[1], landfills[nodef])+distance(tranindex[0], tranindex[1])
    return tranindex


def nontransition(nodef2):
    temp1 = cost = count = -1
    for y in alljobs:
        if not y[0].used:
            if y[0].nearest_landfill == y[1].nearest_landfill == landfills[nodef2]:
                count += 1
                temp1 = distance(y[0], landfills[0]) - distance(y[0], y[0].nearest_landfill) + distance(y[1], landfills[0]) \
                        - distance(y[1], y[1].nearest_landfill)
                if temp1 > cost:
                    cost = temp1
                    ind = y
            elif y[1].nearest_landfill == landfills[nodef2]:
                count += 1
                temp1 = distance(y[0], landfills[0]) - distance(y[0], y[0].nearest_landfill) + distance(y[1], landfills[0])\
                        - distance(y[1], y[1].nearest_landfill)
                temp1 = temp1/100
                if temp1 > cost:
                    cost = temp1
                    ind = y
    if count < 0:
        ind = -1
    return ind


def assignroute(driverf, driverstopf, route, transitiontrue):
    if transitiontrue:
        driversschedule[driverf][0] = driversschedule[driverf][0] +route[0].transition_cost
    else:
        driversschedule[driverf][0] = driversschedule[driverf][0] + distance(route[0], route[0].nearest_landfill) + distance(route[1], route[1].nearest_landfill) + distance(route[0], route[1])
    route[0].used = True
    if route[0].address == route[1].address:
        driversschedule[driver][driverstopf] = route[0].address
    else:
        driversschedule[driver][driverstopf] = route[0].address
        driverstopf += 1
        driversschedule[driver][driverstopf] = route[1].address
        route[1].used = True
    driverstopf += 1
    return driverstopf


#with open('../data/sample1/jobs.csv', 'rb') as f:
with open('jobs.csv', 'rb') as f:
    data = [line[:-1].decode('utf-8').split(',') for line in f][1:]

landfills = [Landfill.from_csv(l) for l in data if l[6] == "S"]
deliveries = [ServiceSite.from_csv(d) for d in data if d[6] == "D"]
pickups = [ServiceSite.from_csv(p) for p in data if p[6] == "P"]
switches = [ServiceSite.from_csv(s) for s in data if s[6] == "AA"]

jobs = deliveries + pickups + switches

for x in jobs:
    x.calc_nearest_landfill(landfills)
pairs1 = calc_DP_pairs(list(deliveries), list(pickups), same_landfill=False)
pairs2 = calc_DP_pairs(list(deliveries), list(pickups), same_landfill=True)

non_stars1 = [d for (d, p) in pairs1] + [p for (d, p) in pairs1]
non_stars2 = [d for (d, p) in pairs2] + [p for (d, p) in pairs2]
star_jobs1 = [(j, j) for j in jobs if j not in non_stars1]
star_jobs2 = [(j, j) for j in jobs if j not in non_stars2]
#alljobs = pairs1+star_jobs1
alljobs = pairs2+star_jobs2
total3 = 0
for x in alljobs:
    total3 = total3+distance(x[0], x[0].nearest_landfill) + distance(x[1], x[1].nearest_landfill) + distance(x[0], x[1])
print(total3)


finish = driver = nextdriver = base = 0
driverstop = 2
current_landfill = temp_landfill = 3
driversschedule = [[0 for x in range(30)] for y in range(30)]
fullday = 480
while finish < 1:
    if current_landfill > 0:
        transition1 = transition(base, current_landfill)
        transition1[0].used = True
        driversschedule[driver][0] = transition1[0].transition_cost
        if transition1[0].address == transition1[1].address:
            driversschedule[driver][1] = transition1[0].address
        else:
            driversschedule[driver][1] = transition1[0].address
            driversschedule[driver][2] = transition1[1].address
            transition1[1].used = True
            driverstop += 1
        transition2 = transition(base, current_landfill)
    while nextdriver < 1:
        nontran = nontransition(temp_landfill)
        if nontran != -1:
            if temp_landfill > 0:
                if distance(nontran[0], nontran[0].nearest_landfill) + distance(nontran[1], nontran[1].nearest_landfill) + distance(nontran[1], nontran[0]) + transition2[0].transition_cost + driversschedule[driver][0] < fullday:
                    driverstop = assignroute(driver, driverstop, nontran, False)
                else:
                    driverstop = assignroute(driver, driverstop, transition2, True)
                    nextdriver = 1
            else:
                if distance(nontran[0], nontran[0].nearest_landfill) + distance(nontran[1], nontran[1].nearest_landfill) + distance(nontran[1], nontran[0]) + driversschedule[driver][0] < fullday:
                    driverstop = assignroute(driver, driverstop, nontran, False)
                else:
                    nextdriver = 1
        elif current_landfill > 0:
            if transition2[0].nearest_landfill == landfills[current_landfill] or transition2[1].nearest_landfill == landfills[current_landfill]:
                current_landfill = current_landfill - 1
                temp_landfill = current_landfill
                transition3 = transition(current_landfill, base)
                if distance(transition2[0], landfills[current_landfill]) + distance(transition2[1], landfills[current_landfill-1]) + transition3[0].transition_cost + driversschedule[driver][0] < fullday:
                    driverstop = assignroute(driver, driverstop, transition2, True)
                    transition2 = transition3
                else:
                    driverstop = assignroute(driver, driverstop, transition2, True)
                    temp_landfill = 0
            else:
                temp_landfill = current_landfill
                current_landfill = current_landfill - 1
                transition3 = transition(temp_landfill, current_landfill)
                transition4 = transition(current_landfill, base)
                if transition4[0].transition_cost + transition3[0].transition_cost + driversschedule[driver][0] < 480:
                    driverstop = assignroute(driver, driverstop, transition3, True)
                    transition2 = transition4
                else:
                    driverstop = assignroute(driver, driverstop, transition2, True)
                    nextdriver = 1
                temp_landfill = current_landfill
        else:
            if temp_landfill < current_landfill:
                nextdriver = 1
            elif current_landfill > 0:
                driverstop = assignroute(driver, driverstop, transition2, True)
                current_landfill = 0
            else:
                finish = 1
                nextdriver = 1
    driver += 1
    driverstop = 2
    nextdriver = 0
    temp_landfill = current_landfill
total = 0
for x in driversschedule:
    total = total+x[0]
print(total)
