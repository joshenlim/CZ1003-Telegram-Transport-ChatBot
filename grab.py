# Math algorithm for Grab based on this URL:
# https://blog.moneysmart.sg/this-vs-that/uber-vs-grab-vs-taxis-which-is-the-cheapest-mode-of-transport-and-when/

def estimate(distance):
    base_fare = 3
    distance_fare = (distance / 1000) * 0.80
    total_fare = base_fare + distance_fare
    return format(total_fare, '.2f')

# Create a range - + 10% for upper limit
