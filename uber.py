from uber_rides.session import Session
from uber_rides.client import UberRidesClient
import config as cfg

server_token = cfg.uber['server_token']

session = Session(server_token=server_token)
client = UberRidesClient(session)

response = client.get_price_estimates(
    start_latitude=1.354100,
    start_longitude=103.688100,
    end_latitude=1.3395,
    end_longitude=103.7066,
    seat_count=1
)

estimate = response.json.get('prices')

for price in estimate:
    if price['localized_display_name'] == 'uberX':
        low_estimate = int(price['low_estimate'])
        high_estimate = int(price['high_estimate'])
        print(price['currency_code'] + ' ' + str(low_estimate) + ' - ' + str(high_estimate))
        # print(price)
