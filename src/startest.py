from location import *
from matching import *


def transition(landstart, landfinish):
    # picks a transition maximizing savings if optimal transition exists and minimizing cost otherwise
    tranindex = 0
    trancost = 10000
    for z in alljobs:
        if z[0].used != 1:
            temp = distance(z[0], landfills[landstart]) + distance(z[1], landfills[landfinish]) - distance(z[0], z[0].nearest_landfill) \
                   - distance(z[1], z[1].nearest_landfill) - distance(z[0], z[1])
        else:
            temp = 10000
        if temp < trancost:
            trancost = temp
            tranindex = z
    tranindex[0].transition_cost = distance(tranindex[0], landfills[landstart]) + distance(tranindex[1], landfills[landfinish]) \
                                   + distance(tranindex[0], tranindex[1])
    return tranindex


def nontransition(landcurr):
    # finds unused routes for the current landfill and picks the one furthest from the base
    # while highly penalized routes with just the delivery in the zone will be picked if no other legal routes exist
    cost = ind = -1
    for y in alljobs:
        if not y[0].used:
            if y[0].nearest_landfill == y[1].nearest_landfill == landfills[landcurr]:
                temp1 = distance(y[0], landfills[0]) - distance(y[0], y[0].nearest_landfill) + distance(y[1], landfills[0]) \
                        - distance(y[1], y[1].nearest_landfill)
                if temp1 > cost:
                    cost = temp1
                    ind = y
            elif y[1].nearest_landfill == landfills[landcurr]:
                temp1 = distance(y[0], landfills[0]) - distance(y[0], y[0].nearest_landfill) + distance(y[1], landfills[0])\
                        - distance(y[1], y[1].nearest_landfill)
                temp1 = temp1/100
                if temp1 > cost:
                    cost = temp1
                    ind = y
    return ind


def assignroute(driver0, driverstop0, route, transitiontrue, tolandfill):
    # first update driver time to include additional added by new route/s
    if transitiontrue:
        driversschedule[driver0][0] = driversschedule[driver0][0] + route[0].transition_cost
    else:
        driversschedule[driver0][0] = driversschedule[driver0][0] + distance(route[0], route[0].nearest_landfill) \
                                      + distance(route[1], route[1].nearest_landfill) + distance(route[0], route[1])
    route[0].used = True
    # then add the locations that are part of the route to the drivers route
    if route[0].address == route[1].address:
        driversschedule[driver][driverstop0] = route[0]
        driverstop0 += 1
        driversschedule[driver][driverstop0] = landfills[tolandfill]
    else:
        driversschedule[driver][driverstop0] = route[0]
        driverstop0 += 1
        driversschedule[driver][driverstop0] = route[1]
        driverstop0 += 1
        driversschedule[driver][driverstop0] = landfills[tolandfill]
        route[1].used = True
    driverstop0 += 1
    return driverstop0


with open('../data/sample1/jobs.csv', 'rb') as f:
#with open('jobs.csv', 'rb') as f:
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
alljobs = pairs1+star_jobs1
# alljobs = pairs2+star_jobs2

total3 = 0
for x in alljobs:
    total3 = total3+distance(x[0], x[0].nearest_landfill) + distance(x[1], x[1].nearest_landfill) + distance(x[0], x[1])
print(total3)

finish = driver = base = 0
current_landfill = 3
fullday = 480
driversschedule = [[0 for x in range(100)] for y in range(20)]
# while loop runs until all routes are assigned
while finish < 1:
    driverstop = 2
    nextdriver = 0
    driversschedule[driver][0] = 0
    driversschedule[driver][1] = landfills[0]
    temp_landfill = current_landfill
    # if landfill isn't the base assign transitions there and back
    if current_landfill > 0:
        transition1 = transition(base, current_landfill)
        driverstop = assignroute(driver, driverstop, transition1, True, temp_landfill)
        # transition 2 is determined for calculations, but not assigned immediately as it may be discarded
        transition2 = transition(base, current_landfill)
    # while loop runs until driver's schedule is full
    while nextdriver < 1:
        # determine a nontransition route if any exist for the landfill the driver is at
        nontran = nontransition(temp_landfill)
        if nontran != -1:
            # if the landfill is not the base the transition is counted against the full day to determine whether the route can be used
            if temp_landfill > 0:
                if distance(nontran[0], nontran[0].nearest_landfill) + distance(nontran[1], nontran[1].nearest_landfill) \
                        + distance(nontran[1], nontran[0]) + transition2[0].transition_cost + driversschedule[driver][0] < fullday:
                    driverstop = assignroute(driver, driverstop, nontran, False, temp_landfill)
                else:
                    driverstop = assignroute(driver, driverstop, transition2, True, 0)
                    nextdriver = 1
            else:
                if distance(nontran[0], nontran[0].nearest_landfill) + distance(nontran[1], nontran[1].nearest_landfill) \
                        + distance(nontran[1], nontran[0]) + driversschedule[driver][0] < fullday:
                    driverstop = assignroute(driver, driverstop, nontran, False, temp_landfill)
                else:
                    nextdriver = 1
        # if no more non tran routes exist for the landfill the landfill is changed if not the base and if it is the base the day is finished
        elif current_landfill > 0:
            # if transition 2 includes a point in the landfill being finished it must be used next and then the driver will finish near the base
            if transition2[0].nearest_landfill == landfills[current_landfill] or transition2[1].nearest_landfill == landfills[current_landfill]:
                current_landfill = current_landfill - 1
                temp_landfill = 0
                driverstop = assignroute(driver, driverstop, transition2, True, temp_landfill)
            # otherwise 2 new transitions are assigned: 1 to the next landfill and 1 from the next landfill to the base
            else:
                temp_landfill = current_landfill
                current_landfill = current_landfill - 1
                transition3 = transition(temp_landfill, current_landfill)
                transition4 = transition(current_landfill, base)
                # if bothe new transitions can be done without willing the day the transition to the next landfill is assigned
                # and the new transition to base replaces the old transition 2
                if transition4[0].transition_cost + transition3[0].transition_cost + driversschedule[driver][0] < fullday:
                    temp_landfill = current_landfill
                    driverstop = assignroute(driver, driverstop, transition3, True, temp_landfill)
                    transition2 = transition4
                # if both cannot be done the driver uses transition 2  to go back to the base and finishes the day there
                else:
                    temp_landfill = 0
                    driverstop = assignroute(driver, driverstop, transition2, True, temp_landfill)
        else:
            finish = 1
            nextdriver = 1
    driver += 1
total = 0
for x in driversschedule:
    total = total+x[0]
print(total)
