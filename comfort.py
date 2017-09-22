import config as cfg
import requests

def estimate(start_lat, start_lng, end_lat, end_lng):
    tff_key = cfg.tff['api_key']
    country = 'Singapore'

    url = (f'https://api.taxifarefinder.com/fare?key={tff_key}&entity_handle={country}&origin={start_lat},{start_lng}&destination={end_lat},{end_lng}')
    data = requests.get(url).json()
    return str(data['total_fare'])
