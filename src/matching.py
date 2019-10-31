# Calculations for matchings
# Dalton Burke

# Munkres is an implementation of the hungarian algorithm
from munkres import Munkres

# benefit is how much you gain by using the triangle over doing them individually
# Munkres minimizes "cost", our goal is to maximize benefit, so we can
# take a large number and subtract benefit from it, and minimize that

# We also don't want to use an edge at all if it isn't possible, or if
# the benefit is negative (ie, it's better to just do them separately)
# so we give these edges huge costs so that it's obvious when one is chosen, and
# so that we can remove them from the solution at the end. We have to do this
# because Munkres returns a maximum matching (ie, everything is paired up)

# list of jobs, pulled from somewhere else, empty for now
jobs = []

deliveries  = filter(lambda x: x.service_type == "D", jobs)
pickups     = filter(lambda x: x.service_type == "P", jobs)

# construct the cost matrix to feed to munkres
cost_matrix = []

for d in deliveries:
    row = []
    for p in pickups:
        benefit = 1000 - (2*distance(d,d.nearest_landfill) + 2*distance(p,p.nearest_landfill)\
                - distance(d,d.nearest_landfill) + distance(d,p) + distance(p,p.nearest_landfill))
        if not compatible(d,p) or benefit > 1000:
            row.apppend(1000000)
        else:
            row.append(benefit)
    cost_matrix.append(row)

m = Munkres()
indices = m.compute(cost_matrix)
# will need to process the output more
