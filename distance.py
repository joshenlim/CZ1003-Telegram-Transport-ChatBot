# Retrieve the road distance from a start and end point
# Using Google's Distance Matrix API

import googlemaps
import config as cfg

gmaps_key = cfg.google['places_key']
gmaps = googlemaps.Client(key=gmaps_key)

def estimate(origin, destination):
    origin_id = 'place_id:' + origin
    destination_id = 'place_id:' + destination
    distance_estimate = gmaps.distance_matrix(
        origins=origin_id,
        destinations=destination_id,
        mode='driving'
    )

    # print(distance_estimate)

    status = distance_estimate['rows'][0]['elements'][0]['status']

    # print(status)

    if status == 'ZERO_RESULTS':
        return 0
    else:
        return distance_estimate['rows'][0]['elements'][0]
