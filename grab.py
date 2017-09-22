# Math algorithm for Grab based on this URL:
# https://blog.moneysmart.sg/this-vs-that/uber-vs-grab-vs-taxis-which-is-the-cheapest-mode-of-transport-and-when/

import math

def estimate(distance, duration):
    base_fare = 2.50
    distance_fare = (distance / 1000) * 0.50
    duration_fare = (duration / 60) * 0.16
    total_fare = base_fare + distance_fare + duration_fare
    estimate_upper_range = str(math.ceil(total_fare * 1.1))
    estimate_lower_range = str(math.ceil(total_fare))

    return estimate_lower_range + " - " + estimate_upper_range
