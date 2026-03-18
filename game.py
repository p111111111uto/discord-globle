import csv
import datetime
datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d")
import random
import math

# Loads CSV into a list of dictionaries
def load_countries():
    countries_list = []
    with open('countries.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            countries_list.append(row)
        return countries_list

# Seeded daily country pick
def daily_country(countries_list):
    date_as_seed = int(datetime.date.today().strftime('%Y%m%d'))
    random.seed(date_as_seed)
    return random.choice(countries_list)

# Case-insensitive country lookup
def find_country(name, countries_list):

    for country in countries_list:
        if country['COUNTRY'].lower() == name.lower():
            return country
    return None

# Distance in KM
def haversine(lat1, lon1, lat2, lon2):
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # Calculate distance in latitude and longitude
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine Formula
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Earth's radius in miles
    R = 3958.8

    return round(R * c,2)

# 0 - 100 score
def proximity_percent(distance):
    # Half of Earth's circumference in miles
    MAX_DIST = 12451
    # Proximity formula
    proximity = max(0, (100 - (distance / MAX_DIST * 100)))
    return int(proximity)

# Arrows pointing to the direction of the country
def directional_arrows(lat1, lon1, lat2, lon2):
    dlon = lon2 - lon1
    x = math.sin(math.radians(dlon)) * math.cos(math.radians(lat2))
    y = math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) - math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(math.radians(dlon))
    bearing = math.degrees(math.atan2(x, y))
    bearing = (bearing + 360) % 360

    if bearing >= 0 and bearing <= 22.5 or bearing > 337.5 and bearing <= 360:
        return '⬆️'
    elif bearing > 22.5 and bearing <= 67.5:
        return '↗️'
    elif bearing > 67.5 and bearing <= 112.5:
        return '➡️'
    elif bearing > 112.5 and bearing <= 157.5:
        return '↘️'
    elif bearing > 157.5 and bearing <= 202.5:
        return '⬇️'
    elif bearing > 202.5 and bearing <= 247.5:
        return '↙️'
    elif bearing > 247.5 and bearing <= 292.5:
        return '⬅️'
    else:
        return '↖️'