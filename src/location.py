# Location class, subclasses, and functions
# Dalton Burke

class Location:
    def __init__(self, address):
        self.address = address

class Landfill(Location):
    def __init__(self, address, num6, num9, num12, num16):
        super(self, address)
        self.num6 = num6
        self.num9 = num9
        self.num12 = num12
        self.num16 = num16

class ServiceSite(Location):
    def __init__(self, address, map_code, truck_type, service_time, can_size, service_type):
        super(self, address)
        self.map_code = map_code
        self.truck_type = truck_type
        self.service_time = service_time
        self.can_size = can_size
        self.name = name
        self.service_type = service_type
    
    def calc_nearest_landfill(landfills):
        self.nearest_landfill = min(landfills, key=lambda x: distance(self, x))

def distance(from_location, to_location):

    return

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
