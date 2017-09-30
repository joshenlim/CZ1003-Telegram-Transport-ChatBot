# Retrieve Uber's fare estimate
# Using Uber's Fare Estimation API

from uber_rides.session import Session
from uber_rides.client import UberRidesClient
import config as cfg

server_token = cfg.uber['server_token']

session = Session(server_token=server_token)
client = UberRidesClient(session)

def get_price_estimate(start_lat, start_lng, end_lat, end_lng):
    response = client.get_price_estimates(
        start_latitude=start_lat,
        start_longitude=start_lng,
        end_latitude=end_lat,
        end_longitude=end_lng,
        seat_count=1
    )

    estimate = response.json.get('prices')

    for price in estimate:
        if price['localized_display_name'] == 'uberX':
            # print(price)
            low_estimate = int(price['low_estimate'])
            high_estimate = int(price['high_estimate'])
            return price['currency_code'] + ' ' + str(low_estimate) + ' - ' + str(high_estimate)
