# Retrieve ComfortDelGro's fare estimate
# Using TaxiFareFinder's API

import config as cfg
import math
import requests

def estimate(start_lat, start_lng, end_lat, end_lng):
    tff_key = cfg.tff['api_key']
    country = 'Singapore'

    url = (f'https://api.taxifarefinder.com/fare?key={tff_key}&entity_handle={country}&origin={start_lat},{start_lng}&destination={end_lat},{end_lng}')
    data = requests.get(url).json()

    # print(data)

    # We decided to provide a price range to improve accuracy and decided
    # on having the upper limit at 110% of the calculated price
    estimate_upper_range = str(math.ceil(data['total_fare'] * 1.1))
    estimate_lower_range = str(math.ceil(data['total_fare']))

    # print(estimate_lower_range)
    # print(estimate_upper_range)

    return estimate_lower_range + " - " + estimate_upper_range
