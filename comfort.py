import math
import datetime
import time

distance = 11000

def surcharge():
    today = datetime.datetime.now()
    current_day = datetime.date.weekday(today)
    current_time = int(time.strftime('%H') + time.strftime('%M'))

    if 0 <= current_day <= 4 and 600 <= current_time <= 929:
        # Morning Peak
        return 1.25
    elif 1800 <= current_time <= 2359:
        # Evening Peak
        return 1.25
    elif 0 <= current_time <= 559:
        # Midnight Charge
        return 1.5
    else:
        return 1

def estimate(distance):
    base_fare = 3.20
    surge = surcharge()
    if distance <= 1000:
        # print(base_fare * surge)
        return str(base_fare * surge)
    elif 1000 < distance <= 10000:
        distance_factor = math.ceil((distance - 1000) / 400)
        calculated_estimate = (distance_factor*0.22) + base_fare
        # print("less than 10000 " + str(calculated_estimate * surge))
        return str(calculated_estimate * surge)
    else:
        distance_factor = math.ceil((distance - 10000) / 350)
        calculated_estimate = (distance_factor * 0.22) + (0.22 * 23) + base_fare
        # print("more than 10000 " + str(calculated_estimate * surge))
        return str(calculated_estimate * surge)

estimate(distance)
print(surcharge())
