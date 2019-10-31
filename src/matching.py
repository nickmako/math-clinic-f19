# Calculations for matchings
# Dalton Burke

# Munkres is an implementation of the hungarian algorithm
from munkres import Munkres, DISALLOWED, make_cost_matrix

# benefit is how much you gain by using the triangle over doing them individually

# list of jobs, pulled from somewhere else, empty for now
jobs = []

deliveries  = filter(lambda x: x.service_type == "D", jobs)
pickups     = filter(lambda x: x.service_type == "P", jobs)

# construct the benefit matrix to feed to munkres
benefit_matrix = []

for d in deliveries:
    row = []
    for p in pickups:
        benefit = (2*distance(d,d.nearest_landfill) + 2*distance(p,p.nearest_landfill)\
                - distance(d,d.nearest_landfill) + distance(d,p) + distance(p,p.nearest_landfill))
        if not compatible(d,p, same_landfill=True) or benefit < 0:
            row.apppend(DISALLOWED)
        else:
            row.append(benefit)
    benefit_matrix.append(row)

m = Munkres()
cost_matrix = make_cost_matrix(benefit_matrix)
indices = m.compute(cost_matrix)

pairs = []
for row, col in indices:
    pairs.append((deliveries[row],pickups[col]))

# will need to process the output more after we have some data to test
