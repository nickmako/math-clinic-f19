# Location class, subclasses, and functions
# Dalton Burke
import math

# this should be processed in another file and then sent here for the distance function
with open('../data/sample1/minutes.csv', 'rb') as f:
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
        return Landfill(ID,address,lonlat)

class ServiceSite(Location):
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
        return str(self.ID) + ", " + self.address + ", (%.2f,%.2f)," % (self.lonlat[0],self.lonlat[1]) + \
               self.service_type + "," + self.service_time

def distance(from_location, to_location):
    return distance_matrix[from_location.ID - 1][to_location.ID - 1]
#\
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
    #if delivery.truck_type 
    
    return True
