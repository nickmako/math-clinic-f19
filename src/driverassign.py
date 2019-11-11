#from location import *

with open('../data/sample1/minutes.csv', 'rb') as f:
#with open('minutes.csv', 'rb') as f:
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
    def __init__(self, ID, address, lonlat, num6=0, num9=0, num12=0, num16=0):
        super().__init__(ID, address, lonlat)
        self.num6 = num6
        self.num9 = num9
        self.num12 = num12
        self.num16 = num16

    @staticmethod
    def from_csv(csv_line):
        ID = int(csv_line[0])
        address = csv_line[2][1:] + "," + csv_line[3][:-1]
        lonlat = (float(csv_line[4]), float(csv_line[5]))
        return Landfill(ID, address, lonlat)


class ServiceSite(Location):
    nearest_landfill: object

    def __init__(self, ID, address, lonlat, map_code, truck_type, service_time, can_size, name, service_type, used, transition_cost):
        super().__init__(ID, address, lonlat)
        self.map_code = map_code
        self.truck_type = truck_type
        self.service_time = service_time
        self.can_size = can_size
        self.name = name
        self.service_type = service_type
        self.used = used
        self.transition_cost = transition_cost

    @staticmethod
    def from_csv(csv_line):
        ID = int(csv_line[0])
        address = csv_line[2][1:] + "," + csv_line[3][:-1]
        lonlat = (float(csv_line[4]), float(csv_line[5]))
        service_type = csv_line[6]
        can_size = csv_line[7]
        return ServiceSite(ID, address, lonlat, map_code="", truck_type="",
                           service_time="ANY", can_size=can_size, name="", service_type=service_type, used=False, transition_cost=0)

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


def transition(nodesf, nodef):
    temp = tranindex = tranindex1 = 0
    trancost = 10000
    for x in deliveries:
        if x.used != 1:
            temp = distance(x, landfills[nodesf])+distance(x, landfills[nodef])-2*distance(x, x.nearest_landfill)
        else:
            temp = 10000
        if temp < trancost:
            trancost = temp
            tranindex = x
    for x in deliveries:
        if x.used != 1:
            temp = distance(x, landfills[nodesf])+distance(x, landfills[nodef])-2*distance(x, x.nearest_landfill)
        else:
            temp = 10000
        if temp < trancost:
            trancost = temp
            tranindex = x
    tranindex.transition_cost = distance(tranindex, landfills[nodesf])+distance(tranindex, landfills[nodef])
    return tranindex


def nontransition(nodef2):
    temp1 = cost = count = -1
    for x in deliveries:
        if x.nearest_landfill == landfills[nodef2]:
            if not x.used:
                count += 1
                temp1 = distance(x, landfills[0]) - distance(x, x.nearest_landfill)
                if temp1 > cost:
                    cost = temp1
                    ind = x
    for x in pickups:
        if x.nearest_landfill == landfills[nodef2]:
            if not x.used:
                count += 1
                temp1 = distance(x, landfills[0]) - distance(x, x.nearest_landfill)
                if temp1 > cost:
                    cost = temp1
                    ind = x
    if count < 0:
        ind = -1
    return ind


def assignroute(driverf, driverstopf, route, transitiontrue):
    if transitiontrue:
        driversschedule[driverf][0] = driversschedule[driverf][0] + route.transition_cost
    else:
        driversschedule[driverf][0] = driversschedule[driverf][0] + 2*distance(route, route.nearest_landfill)
    driversschedule[driver][driverstopf] = route.address
    route.used = True
    driverstopf += 1
    return driverstopf


with open('../data/sample1/jobs.csv', 'rb') as f:
#with open('jobs.csv', 'rb') as f:
    data = [line[:-1].decode('utf-8').split(',') for line in f][1:]

landfills = [Landfill.from_csv(l) for l in data if l[6] == "S"]
deliveries = [ServiceSite.from_csv(d) for d in data if d[6] == "D"]
pickups = [ServiceSite.from_csv(p) for p in data if p[6] == "P"]
switches = [ServiceSite.from_csv(s) for s in data if s[6] == "AA"]
for x in deliveries:
    x.calc_nearest_landfill(landfills)
for x in pickups:
    x.calc_nearest_landfill(landfills)
finish = driver = nextdriver = base = 0
driverstop = 2
current_landfill = temp_landfill = 3
driversschedule = [[0 for x in range(30)] for y in range(30)]
while finish < 1:
    if current_landfill > 0:
        transition1 = transition(base, current_landfill)
        transition1.used = True
        driversschedule[driver][0] = transition1.transition_cost
        driversschedule[driver][1] = transition1.address
        transition2 = transition(base, current_landfill)
    while nextdriver < 1:
        nontran = nontransition(temp_landfill)
        if nontran != -1:
            if 2 * distance(nontran, nontran.nearest_landfill) + transition2.transition_cost + driversschedule[driver][0] < 480:
                driverstop = assignroute(driver, driverstop, nontran, False)
            else:
                if current_landfill > 0:
                    driverstop = assignroute(driver, driverstop, transition2, True)
                    nextdriver = 1
                else:
                    nextdriver = 1
        elif current_landfill > 0:
            if transition2.nearest_landfill == landfills[current_landfill]:
                current_landfill = current_landfill - 1
                temp_landfill = current_landfill
                transition3 = transition(current_landfill, base)
                if distance(transition2, landfills[current_landfill]) + distance(transition2, landfills[current_landfill-1]) + transition3.transition_cost + driversschedule[driver][0] < 480:
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
                if transition4.transition_cost + transition3.transition_cost + driversschedule[driver][0] < 480:
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
total2 = 0
for x in deliveries:
    total2 = total2+2*distance(x, x.nearest_landfill)
for x in pickups:
    total2 = total2+2*distance(x, x.nearest_landfill)
print(total2)
