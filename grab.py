# Math algorithm for Grab based on this URL:
# https://www.grab.com/sg/car/

import math

def estimate(distance, duration):
    base_fare = 2.50
    distance_fare = (distance / 1000) * 0.50
    duration_fare = (duration / 60) * 0.16
    total_fare = base_fare + distance_fare + duration_fare

    # We decided to provide a price range to improve accuracy and decided
    # on having the upper limit at 110% of the calculated price
    estimate_upper_range = str(math.ceil(total_fare * 1.1))
    estimate_lower_range = str(math.ceil(total_fare))

    return estimate_lower_range + " - " + estimate_upper_range
