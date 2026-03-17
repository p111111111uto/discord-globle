import csv
import datetime
import random
import math

def load_countries():
    countries_list = []
    with open('countries.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            countries_list.append(row)
        return countries_list
    
def daily_country(countries_list):
    date_as_seed = int(datetime.date.today().strftime('%Y%m%d'))
    random.seed(date_as_seed)
    return random.choice(countries_list)

def find_country(name, countries_list):

    for country in countries_list:
        if country['COUNTRY'].lower() == name.lower():
            return country
    return None

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
    
    # Earth's radius
    R = 6371

    return R * c