from functclass import *


def authenticate(schedule, buffer, fullday):
    node = 3
    for y in schedule:
        for z in y:
            if z.service_type != 'L':
                if z.transition_cost < 1 and z.schedule_time < fullday-buffer:
                    node = authenticateroute(z, schedule, node, buffer, fullday)
                if z.node_shift:
                    node += -1


def authenticateroute(route, schedule, node, buffer, fullday):
    if route.can_size == '6':
        countsix = route.nearest_landfill.num6
        node = authenticateroutecont(route, schedule, node, countsix, buffer, fullday)
    elif route.can_size == '9':
        countnine = route.nearest_landfill.num9
        node = authenticateroutecont(route, schedule, node, countnine, buffer, fullday)
    elif route.can_size == '12':
        counttwelve = route.nearest_landfill.num12
        node = authenticateroutecont(route, schedule, node, counttwelve, buffer, fullday)
    elif route.can_size == '16':
        countsixteen = route.nearest_landfill.num16
        node = authenticateroutecont(route, schedule, node, countsixteen, buffer, fullday)
    return node


def authenticateroutecont(route, schedule, node, count, buffer, fullday):
    for i in schedule:
        for j in i:
            if j.service_type != 'L' and j.nearest_landfill == landfills[node] and j.can_size == route.can_size and j.transition_cost < 1:
                if j.service_type == 'P':
                    if j.driver == route.driver:
                        if route.schedule_time > j.schedule_time:
                            count += 1
                    else:
                        if route.schedule_time*(1-buffer/fullday) > j.schedule_time:
                            count += 1
                elif j.service_type == 'D':
                    if j.driver == route.driver:
                        if route.schedule_time > j.schedule_time:
                            count += -1
                    else:
                        if route.schedule_time*(1+buffer/fullday) > j.schedule_time:
                            count += -1
                elif j.service_type == 'S':
                    if j.driver != route.driver:
                        if route.schedule_time*(1 - buffer / fullday) < j.schedule_time < route.schedule_time*(1 + buffer / fullday):
                            count += -1
    if count < 0:
        swap(route, schedule, node, buffer, fullday)
    return node


def swap(route, schedule, node, buffer, fullday):
    route.swapped = True
#   for k in schedule:
#       for l in k:


# variables to change:
# multiplier for drive time to account traffic etc.
drivermultiplier = 1.1
# fixed times in minutes divided by driver multiplier
emptytime = 5
servicetime = 5
canswaptime = 5
buffer = 30
fullday = 480
# fullday >= Sum(Route*DM+modifiers)
# number of nodes -1
current_landfill = 3
# end variables to change

# with open('../data/sample1/jobs.csv', 'rb') as f:
with open('jobs.csv', 'rb') as f:
    data = [line[:-1].decode('utf-8').split(',') for line in f][1:]

landfills = [Landfill.from_csv(l) for l in data if l[6] == "S"]
deliveries = [ServiceSite.from_csv(d) for d in data if d[6] == "D"]
pickups = [ServiceSite.from_csv(p) for p in data if p[6] == "P"]
switches = [ServiceSite.from_csv(s) for s in data if s[6] == "AA"]
jobs = deliveries + pickups + switches


# replace below with input
base = 1
for x in landfills:
    if base == 1:
        x.num6 = 10
        x.num9 = 10
        x.num12 = 10
        x.num16 = 10
        base = 0
    else:
        x.num6 = 5
        x.num9 = 5
        x.num12 = 5
        x.num16 = 5

cancount(landfills, jobs)

pairs1 = calc_DP_pairs(list(deliveries), list(pickups), same_landfill=False)
non_stars1 = [d for (d, p) in pairs1] + [p for (d, p) in pairs1]
star_jobs1 = [(j, j) for j in jobs if j not in non_stars1]
alljobs = pairs1+star_jobs1

returntup = createschedule(current_landfill, emptytime, servicetime, canswaptime, fullday, alljobs, landfills, drivermultiplier)
driversschedule = returntup[0]
drivertime = returntup[1]
authenticate(driversschedule, buffer, fullday)
total = scheduleout(driversschedule, drivertime)
teleporttotal = 0
for x in alljobs:
    teleporttotal = teleporttotal + distance(x[0], x[0].nearest_landfill) + distance(x[1], x[1].nearest_landfill) + distance(x[0], x[1])
print(teleporttotal)
print(total)

plot(driversschedule, deliveries, pickups, switches, landfills)
