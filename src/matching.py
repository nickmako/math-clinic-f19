# Calculations for matchings
# Dalton Burke

# Munkres is an implementation of the hungarian algorithm
from munkres import Munkres
from location import distance, compatible

def calc_DP_pairs(jobs, same_landfill=True):
    deliveries  = list(filter(lambda x: x.service_type == "D", jobs))
    pickups     = list(filter(lambda x: x.service_type == "P", jobs))
    
    # construct the benefit matrix to feed to munkres
    # benefit is how much you gain by using the triangle over doing them individually
    benefit_matrix = []
    
    for d in deliveries:
        row = []
        for p in pickups:
            benefit = (2*distance(d,d.nearest_landfill) + 2*distance(p,p.nearest_landfill)\
                    - distance(d,d.nearest_landfill) + distance(d,p) + distance(p,p.nearest_landfill))
            if not compatible(d,p, same_landfill) or benefit < 0:
                row.append(1000000)
            else:
                row.append(benefit)
        benefit_matrix.append(row)
    
    m = Munkres()
    indices = m.compute(benefit_matrix)
    valid_indices = list(filter(lambda x: benefit_matrix[x[0]][x[1]] < 1000, indices))
    
    pairs = []
    for row, col in valid_indices:
        pairs.append((deliveries[row],pickups[col]))
    
    return pairs
