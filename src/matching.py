# Calculations for matchings
# Dalton Burke

# Munkres is an implementation of the hungarian algorithm
from munkres import Munkres
from location import distance, compatible

def calc_DP_pairs(deliveries, pickups, same_landfill=True, interzone_penalty=0):
    #deliveries  = [d for d in jobs if d.service_type == "D"]
    #pickups     = [p for p in jobs if p.service_type == "P"]    

    # construct the benefit matrix to feed to munkres
    # benefit is how much you gain by using the triangle over doing them individually
    benefit_matrix = []
    
    for d in deliveries:
        row = []
        for p in pickups:
            # because munkres minimizes, we need to transform the variables a bit
            benefit = 10000 - \
                    (distance(d.nearest_landfill,d) +\
                    distance(d,d.nearest_landfill) +\
                    distance(p.nearest_landfill,p) +\
                    distance(p,p.nearest_landfill) -\
                    (distance(d.nearest_landfill,d) + distance(d,p) + distance(p,p.nearest_landfill)))

            if benefit > 10000:
                benefit = 10000

            if d.nearest_landfill != p.nearest_landfill:
                benefit += interzone_penalty

            if not compatible(d,p, same_landfill):
                row.append(1000000)
            else:
                row.append(benefit)
        benefit_matrix.append(row)
    
    m = Munkres()
    indices = m.compute(benefit_matrix)
    pairs = [(deliveries[x],pickups[y]) for x,y in indices if benefit_matrix[x][y] < 10000]
    
    return pairs
