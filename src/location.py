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
    def __init__(self, address, map_code, truck_type, delivery_time, can_size, service_type):
        super(self, address)
        self.map_code = map_code
        self.truck_type = truck_type
        self.delivery_time = delivery_time
        self.can_size = can_size
        self.name = name
        self.service_type = service_type
    
    def calc_nearest_landfill(landfills):
        self.nearest_landfill = min(landfills, key=lambda x: distance(self, x))

def distance(from_location, to_location):

    return
