# Munkres is an implementation of the hungarian algorithm
from munkres import Munkres
import matplotlib.pyplot as plt


with open('minutes.csv', 'rb') as f:
    # ignore last character of line (always '\n'), decode bytestring to string,
    # split strings on ',' into list, ignore first element of that list (deleting first column),
    # convert elements of the list to floats, then ignore the first row
    distance_matrix = [[float(x) for x in line[:-1].decode('utf-8').split(',')[1:]] for line in f][1:]


class Location:
    def __init__(self, ID, address, lonlat=()):
        self.ID = ID
        self.address = address
        self.lonlat = lonlat


class Landfill(Location):
    def __init__(self, ID, address, lonlat, num6=0, num9=0, num12=0, num16=0, service_type='L'):
        super().__init__(ID, address, lonlat)
        self.num6 = num6
        self.num9 = num9
        self.num12 = num12
        self.num16 = num16
        self.service_type = service_type

    @staticmethod
    def from_csv(csv_line):
        ID = int(csv_line[0])
        address = csv_line[2][1:] + "," + csv_line[3][:-1]
        lonlat = (float(csv_line[4]), float(csv_line[5]))
        return Landfill(ID, address, lonlat)


class ServiceSite(Location):
    def __init__(self, ID, address, lonlat, map_code, truck_type, service_time, can_size, name, service_type, used, transition_cost,
                 schedule_time, driver=0, swapped=False, node_shift=False):
        super().__init__(ID, address, lonlat)
        self.map_code = map_code
        self.truck_type = truck_type
        self.service_time = service_time
        self.can_size = can_size
        self.name = name
        self.service_type = service_type
        self.used = used
        self.transition_cost = transition_cost
        self.schedule_time = schedule_time
        self.driver = driver
        self.swapped = swapped
        self.node_shift = node_shift

    @staticmethod
    def from_csv(csv_line):
        ID = int(csv_line[0])
        address = csv_line[2][1:] + "," + csv_line[3][:-1]
        lonlat = (float(csv_line[4]), float(csv_line[5]))
        service_type = csv_line[6]
        can_size = csv_line[7]
        return ServiceSite(ID, address, lonlat, map_code="", truck_type="",
                           service_time="ANY", can_size=can_size, name="", service_type=service_type, used=False, transition_cost=0, schedule_time=0)

    def calc_nearest_landfill(self, landfills):
        self.nearest_landfill = min(landfills, key=lambda x: distance(self, x))

    def __str__(self):
        return str(self.ID) + ", " + self.address + ", (%.2f,%.2f)," % (self.lonlat[0], self.lonlat[1]) + \
               self.service_type + "," + self.service_time


def distance(from_location, to_location):
    return distance_matrix[from_location.ID - 1][to_location.ID - 1]


# \
#            math.sqrt(\
#              (from_location.address[0]-to_location.address[0])**2\
#            + (from_location.address[1]-to_location.address[1])**2)


def compatible(delivery, pickup, same_landfill=False):
    if delivery.nearest_landfill != pickup.nearest_landfill and same_landfill == True:
        return False

    if delivery.service_type != "D" or pickup.service_type != "P":
        return False

    if delivery.service_time != "ANY" and \
            pickup.service_time != "ANY" and \
            delivery.service_time != pickup.service_time:
        return False

    # need to determine specific rules for truck types
    # if delivery.truck_type

    return True


def calc_DP_pairs(deliveries, pickups, same_landfill=True, interzone_penalty=0):
    # deliveries  = [d for d in jobs if d.service_type == "D"]
    # pickups     = [p for p in jobs if p.service_type == "P"]

    # construct the benefit matrix to feed to munkres
    # benefit is how much you gain by using the triangle over doing them individually
    benefit_matrix = []

    for d in deliveries:
        row = []
        for p in pickups:
            # because munkres minimizes, we need to transform the variables a bit
            benefit = 10000 - \
                      (distance(d.nearest_landfill, d) +
                       distance(d, d.nearest_landfill) +
                       distance(p.nearest_landfill, p) +
                       distance(p, p.nearest_landfill) -
                       (distance(d.nearest_landfill, d) + distance(d, p) + distance(p, p.nearest_landfill)))

            if benefit > 10000:
                benefit = 10000

            if d.nearest_landfill != p.nearest_landfill:
                benefit += interzone_penalty

            if not compatible(d, p, same_landfill):
                row.append(1000000)
            else:
                row.append(benefit)
        benefit_matrix.append(row)

    m = Munkres()
    indices = m.compute(benefit_matrix)
    pairs = [(deliveries[x], pickups[y]) for x, y in indices if benefit_matrix[x][y] < 10000]

    return pairs


def cancount(landfills, jobs):
    for x in jobs:
        x.calc_nearest_landfill(landfills)
        if x.service_type == 'D':
            if x.can_size == '12':
                x.nearest_landfill.num12 += -1
            if x.can_size == '9':
                x.nearest_landfill.num9 += -1
            if x.can_size == '6':
                x.nearest_landfill.num6 += -1
            if x.can_size == '16':
                x.nearest_landfill.num16 += -1
        elif x.service_type == 'P':
            if x.can_size == '12':
                x.nearest_landfill.num12 += 1
            if x.can_size == '9':
                x.nearest_landfill.num9 += 1
            if x.can_size == '6':
                x.nearest_landfill.num6 += 1
            if x.can_size == '16':
                x.nearest_landfill.num16 += 1


def createschedule(current_landfill, emptytime, servicetime, canswaptime, fullday, alljobs, landfills, drivermultiplier):
    # while loop runs until all routes are assigned
    driversschedule = [[0 for x in range(200)] for y in range(20)]
    drivertime = [[0 for x in range(1)] for y in range(20)]
    finish = driver = base = 0
    while finish < 1:
        driverstop = 1
        nextdriver = 0
        drivertime[driver][0] = 0
        driversschedule[driver][0] = landfills[0]
        temp_landfill = current_landfill
        deficit = [0, 0, 0, 0, 0]
        zeroarray = [0, 0, 0, 0, 0]
        # if landfill isn't the base assign transitions there and back
        if current_landfill > 0:
            if landfills[current_landfill].num6 < 0:
                deficit[0] = landfills[current_landfill].num6
                deficit[4] = deficit[4] - landfills[current_landfill].num6
            if landfills[current_landfill].num9 < 0:
                deficit[1] = landfills[current_landfill].num9
                deficit[4] = deficit[4] - landfills[current_landfill].num9
            if landfills[current_landfill].num12 < 0:
                deficit[2] = landfills[current_landfill].num12
                deficit[4] = deficit[4] - landfills[current_landfill].num12
            if landfills[current_landfill].num16 < 0:
                deficit[3] = landfills[current_landfill].num16
                deficit[4] = deficit[4] - landfills[current_landfill].num16
            transition1 = transition(base, current_landfill, deficit, alljobs, landfills)
            driverstop = assignroute(driver, driverstop, transition1, True, temp_landfill, driversschedule, drivertime, landfills, emptytime, servicetime, canswaptime, drivermultiplier)
            if deficit[4] > 0:
                deficit[4] += -1
                if transition1[1].can_size == '6':
                    deficit[0] += 1
                    landfills[current_landfill].num6 += 1
                elif transition1[1].can_size == '9':
                    deficit[1] += 1
                    landfills[current_landfill].num9 += 1
                elif transition1[1].can_size == '12':
                    deficit[2] += 1
                    landfills[current_landfill].num12 += 1
                elif transition1[1].can_size == '16':
                    deficit[3] += 1
                    landfills[current_landfill].num16 += 1
            if deficit[0] < 0 or deficit[1] < 0 or deficit[2] < 0 or deficit[3] < 0:
                fix = 1
                while fix > 0:
                    clone = deficit[4]
                    deficit[4] = 1
                    transitionf = transition(base, current_landfill, deficit, alljobs, landfills)
                    deficit[4] = clone-1
                    driverstop = assignroute(driver, driverstop, transitionf, True, temp_landfill, driversschedule, drivertime, landfills, emptytime, servicetime, canswaptime, drivermultiplier)
                    test = nontransition(temp_landfill, alljobs, landfills)
                    if test == -1:
                        driversschedule[driver][driverstop - 1].node_shift = True
                    if transition1[1].can_size == '6':
                        deficit[0] += 1
                        landfills[current_landfill].num6 += 1
                    elif transition1[1].can_size == '9':
                        deficit[1] += 1
                        landfills[current_landfill].num9 += 1
                    elif transition1[1].can_size == '12':
                        deficit[2] += 1
                        landfills[current_landfill].num12 += 1
                    elif transition1[1].can_size == '16':
                        deficit[3] += 1
                        landfills[current_landfill].num16 += 1
                    if deficit[4] < 1:
                        fix = 0

            # transition 2 is determined for calculations, but not assigned immediately as it may be discarded
            transition2 = transition(base, current_landfill, zeroarray, alljobs, landfills)
        # while loop runs until driver's schedule is full
        while nextdriver < 1:
            # determine a nontransition route if any exist for the landfill the driver is at
            nontran = nontransition(temp_landfill, alljobs, landfills)
            if nontran != -1:
                # if the landfill is not the base the transition is counted against the full day to determine whether the route can be used
                if temp_landfill > 0:
                    if distance(nontran[0], nontran[0].nearest_landfill) + distance(nontran[1], nontran[1].nearest_landfill) \
                            + distance(nontran[1], nontran[0]) + transition2[0].transition_cost + drivertime[driver][0] < fullday:
                        driverstop = assignroute(driver, driverstop, nontran, False, temp_landfill, driversschedule, drivertime, landfills, emptytime, servicetime, canswaptime, drivermultiplier)
                    else:
                        driverstop = assignroute(driver, driverstop, transition2, True, 0, driversschedule, drivertime, landfills, emptytime, servicetime, canswaptime, drivermultiplier)
                        nextdriver = 1
                else:
                    if distance(nontran[0], nontran[0].nearest_landfill) + distance(nontran[1], nontran[1].nearest_landfill) \
                            + distance(nontran[1], nontran[0]) + drivertime[driver][0] < fullday:
                        driverstop = assignroute(driver, driverstop, nontran, False, temp_landfill, driversschedule, drivertime, landfills, emptytime, servicetime, canswaptime, drivermultiplier)
                    else:
                        nextdriver = 1
                test = nontransition(temp_landfill, alljobs, landfills)
                if test == -1:
                    driversschedule[driver][driverstop-1].node_shift = True
            # if no more non tran routes exist for the landfill the landfill is changed if not the base and if it is the base the day is finished
            elif current_landfill > 0:
                # if transition 2 includes a point in the landfill being finished it must be used next and then the driver will finish near the base
                if transition2[0].nearest_landfill == landfills[current_landfill] or transition2[1].nearest_landfill == landfills[current_landfill]:
                    current_landfill = current_landfill - 1
                    temp_landfill = 0
                    driverstop = assignroute(driver, driverstop, transition2, True, temp_landfill, driversschedule, drivertime, landfills, emptytime, servicetime, canswaptime, drivermultiplier)
                # otherwise 2 new transitions are assigned: 1 to the next landfill and 1 from the next landfill to the base
                else:
                    temp_landfill = current_landfill
                    current_landfill = current_landfill - 1
                    transition3 = transition(temp_landfill, current_landfill, zeroarray, alljobs, landfills)
                    transition4 = transition(current_landfill, base, zeroarray, alljobs, landfills)
                    # if bothe new transitions can be done without willing the day the transition to the next landfill is assigned
                    # and the new transition to base replaces the old transition 2
                    if transition4[0].transition_cost + transition3[0].transition_cost + drivertime[driver][0] < fullday:
                        temp_landfill = current_landfill
                        driverstop = assignroute(driver, driverstop, transition3, True, temp_landfill, driversschedule, drivertime, landfills, emptytime, servicetime, canswaptime, drivermultiplier)
                        transition2 = transition4
                    # if both cannot be done the driver uses transition 2  to go back to the base and finishes the day there
                    else:
                        temp_landfill = 0
                        driverstop = assignroute(driver, driverstop, transition2, True, temp_landfill, driversschedule, drivertime, landfills, emptytime, servicetime, canswaptime, drivermultiplier)
            else:
                finish = 1
                nextdriver = 1
        driver += 1
    length = len(drivertime)
    i = 0
    while i < length:
        if drivertime[i] == [0]:
            drivertime.remove(drivertime[i])
            length += -1
            continue
        i += 1
    length = len(driversschedule)
    i = 0
    while i < length:
        if driversschedule[i][0] == 0:
            driversschedule.remove(driversschedule[i])
            length += -1
            continue
        i += 1
    for x in driversschedule:
        length = len(x)
        i = 0
        while i < length:
            if x[i] == 0:
                x.remove(x[i])
                length += -1
                continue
            i += 1
    return driversschedule, drivertime


def transition(landstart, landfinish, deficits, alljobs, landfills):
    # picks a transition maximizing savings if optimal transition exists and minimizing cost otherwise
    tranindex = 0
    trancost = 10000
    for x in alljobs:
        if x[0].used != 1:
            if deficits[4] == 1:
                if x[1].nearest_landfill != landfills[landfinish]:
                    temp = distance(x[0], landfills[landfinish]) + distance(x[1], landfills[landfinish]) - distance(x[0], x[0].nearest_landfill) \
                       - distance(x[1], x[1].nearest_landfill)
                    if x[1].can_size == '6' and deficits[0] < 0:
                        temp = temp - 1000
                    elif x[1].can_size == '9' and deficits[1] < 0:
                        temp = temp - 1000
                    elif x[1].can_size == '12' and deficits[2] < 0:
                        temp = temp - 1000
                    elif x[1].can_size == '16' and deficits[3] < 0:
                        temp = temp - 1000
                else:
                    temp = 1000
            elif deficits[4] > 1:
                if x[1].nearest_landfill != landfills[landfinish]:
                    temp = distance(x[0], landfills[landfinish]) + distance(x[1], landfills[landfinish]) - distance(x[0], x[0].nearest_landfill) \
                       - distance(x[1], x[1].nearest_landfill)
                    if x[1].can_size == '6' and deficits[0] < 0:
                        temp = temp - 1000
                    elif x[1].can_size == '9' and deficits[1] < 0:
                        temp = temp - 1000
                    elif x[1].can_size == '12' and deficits[2] < 0:
                        temp = temp - 1000
                    elif x[1].can_size == '16' and deficits[3] < 0:
                        temp = temp - 1000
                else:
                    temp = 1000
            else:
                temp = distance(x[0], landfills[landstart]) + distance(x[1], landfills[landfinish]) - distance(x[0], x[0].nearest_landfill) \
                       - distance(x[1], x[1].nearest_landfill)
                if x[0].nearest_landfill != x[1].nearest_landfill:
                    temp = temp - distance(x[1], x[0].nearest_landfill) + distance(x[1], x[1].nearest_landfill)

            if deficits[4] > 0:
                if x[1].can_size == '6' and x[1].nearest_landfill.num6 < 1:
                    temp = 1000
                elif x[1].can_size == '9' and x[1].nearest_landfill.num9 < 1:
                    temp = 1000
                elif x[1].can_size == '12' and x[1].nearest_landfill.num12 < 1:
                    temp = 1000
                elif x[1].can_size == '16' and x[1].nearest_landfill.num16 < 1:
                    temp = 1000
        else:
            temp = 10000
        if temp < trancost:
            trancost = temp
            tranindex = x
    tranindex[0].transition_cost = distance(tranindex[0], landfills[landstart]) + distance(tranindex[1], landfills[landfinish]) \
                                   + distance(tranindex[0], tranindex[1])
    if tranindex[1].nearest_landfill != landfills[landfinish]:
        if tranindex[1].can_size == '6':
            landfills[landfinish].num6 += 1
            tranindex[1].nearest_landfill.num6 += -1
        elif tranindex[1].can_size == '9':
            landfills[landfinish].num9 += 1
            tranindex[1].nearest_landfill.num9 += -1
        elif tranindex[1].can_size == '12':
            landfills[landfinish].num12 += 1
            tranindex[1].nearest_landfill.num12 += -1
        elif tranindex[1].can_size == '16':
            landfills[landfinish].num16 += 1
            tranindex[1].nearest_landfill.num16 += -1
    return tranindex


def nontransition(landcurr, alljobs, landfills):
    # finds unused routes for the current landfill and picks the one furthest from the base
    # while highly penalized routes with just the delivery in the zone will be picked if no other legal routes exist
    cost = ind = -1
    for x in alljobs:
        if not x[0].used:
            if x[0].nearest_landfill == x[1].nearest_landfill == landfills[landcurr]:
                temp1 = distance(x[0], landfills[0]) - distance(x[0], x[0].nearest_landfill) + distance(x[1], landfills[0]) \
                        - distance(x[1], x[1].nearest_landfill)
                if temp1 > cost:
                    cost = temp1
                    ind = x
            elif x[1].nearest_landfill == landfills[landcurr]:
                temp1 = distance(x[0], landfills[0]) - distance(x[0], x[0].nearest_landfill) + distance(x[1], landfills[0])\
                        - distance(x[1], x[1].nearest_landfill)
                temp1 = temp1/100
                if temp1 > cost:
                    cost = temp1
                    ind = x
    return ind


def assignroute(driver, driverstop, route, transitiontrue, tolandfill, driversschedule, drivertime, landfills, emptytime, servicetime, canswaptime, drivermultiplier):
    # first update driver time to include additional added by new route/s
    route[0].used = True
    route[1].used = True
    route[0].driver = driver
    route[1].driver = driver
    if transitiontrue:
        if route[0].address == route[1].address:
            if driverstop > 2 and driversschedule[driver][driverstop-2].can_size == route[0].can_size:
                drivertime[driver][0] = drivertime[driver][0]
            else:
                drivertime[driver][0] = drivertime[driver][0] + canswaptime
            driversschedule[driver][driverstop] = route[0]
            driverstop += 1
            driversschedule[driver][driverstop] = landfills[tolandfill]
            if route[0].service_type == 'S' or 'D':
                route[0].schedule_time = drivertime[driver][0]
            drivertime[driver][0] = drivertime[driver][0] + route[0].transition_cost*drivermultiplier + servicetime + emptytime
            if route[0].service_type == 'P':
                route[0].schedule_time = drivertime[driver][0]
        else:
            if driverstop > 2 and driversschedule[driver][driverstop-2].can_size == route[0].can_size:
                drivertime[driver][0] = drivertime[driver][0]
            else:
                drivertime[driver][0] = drivertime[driver][0] + canswaptime
            driversschedule[driver][driverstop] = route[0]
            driverstop += 1
            driversschedule[driver][driverstop] = route[1]
            driverstop += 1
            driversschedule[driver][driverstop] = landfills[tolandfill]
            route[1].used = True
            route[0].schedule_time = drivertime[driver][0]
            drivertime[driver][0] = drivertime[driver][0] + route[0].transition_cost*drivermultiplier + 2*servicetime + emptytime
            route[1].schedule_time = drivertime[driver][0]
    else:
        if route[0].address == route[1].address:
            if driverstop > 2 and driversschedule[driver][driverstop-2].can_size == route[0].can_size:
                drivertime[driver][0] = drivertime[driver][0]
            else:
                drivertime[driver][0] = drivertime[driver][0] + canswaptime
            driversschedule[driver][driverstop] = route[0]
            driverstop += 1
            driversschedule[driver][driverstop] = landfills[tolandfill]
            if route[0].service_type == 'S' or 'D':
                route[0].schedule_time = drivertime[driver][0]
            drivertime[driver][0] = (drivertime[driver][0] + distance(route[0], route[0].nearest_landfill)
                                    + distance(route[1], route[1].nearest_landfill) + distance(route[0], route[1]))*drivermultiplier + servicetime + emptytime
            if route[0].service_type == 'P':
                route[0].schedule_time = drivertime[driver][0]
        else:
            if driverstop > 2 and driversschedule[driver][driverstop-2].can_size == route[0].can_size:
                drivertime[driver][0] = drivertime[driver][0]
            else:
                drivertime[driver][0] = drivertime[driver][0] + canswaptime
            driversschedule[driver][driverstop] = route[0]
            driverstop += 1
            driversschedule[driver][driverstop] = route[1]
            driverstop += 1
            driversschedule[driver][driverstop] = landfills[tolandfill]
            route[1].used = True
            route[0].schedule_time = drivertime[driver][0]
            drivertime[driver][0] = (drivertime[driver][0] + distance(route[0], route[0].nearest_landfill)
                                    + distance(route[1], route[1].nearest_landfill) + distance(route[0], route[1]))*drivermultiplier + 2*servicetime + emptytime
            route[1].schedule_time = drivertime[driver][0]
    driverstop += 1
    return driverstop


def scheduleout(driversschedule, drivertime):
    total = 0
    j = 1
    for x in driversschedule:
        print("")
        print("Driver " + str(j) + "'s schedule:")
        for y in x:
            print(y.address)
        j += 1
    for y in drivertime:
        total = total+y[0]
    return total


def plot(driversschedule, deliveries, pickups, switches, landfills):
    for drivers in driversschedule:
        plt.plot([x.lonlat[0] for x in drivers],
                 [x.lonlat[1] for x in drivers])

    for d in deliveries:
        plt.plot(d.lonlat[0], d.lonlat[1], 'go', markersize=3)

    for p in pickups:
        plt.plot(p.lonlat[0], p.lonlat[1], 'ro', markersize=3)

    for s in switches:
        plt.plot(s.lonlat[0], s.lonlat[1], 'mo', markersize=3)

    for l in landfills:
        plt.plot(l.lonlat[0], l.lonlat[1], 'bo', markersize=7)

    plt.show()
