import csv
import requests
from pymongo import MongoClient

googleAPIKEY = 'AIzaSyDBLLd4c5JutShD1ZiCcQJFq4AqOas3Cnw'
client = MongoClient('localhost', 15986)
database = client['food_analysis']
ff_collection = database['FF_Restaurant']


def ff_search(lat, lng, ff):
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=' + lat + ',' + lng + '&radius=5000&type=restaurant&keyword=' + ff + '&key=AIzaSyDBLLd4c5JutShD1ZiCcQJFq4AqOas3Cnw'
    reps = requests.get(url).json()
    if reps.get('next_page_token') != None:
        print('more than 20')
    for i in range(len(reps['results'])):
        result = reps['results'][i]
        ff_coordinates = tuple([result['geometry']['location']['lng'], result['geometry']['location']['lat']])
        geolocation = {'type': 'Point', 'coordinates': ff_coordinates}
        if ff_collection.find({'ff_loc': geolocation}).count() != 0:
            continue
        print(ff_coordinates)
        store_info = {'ff_brand': ff, 'ff_loc': geolocation}
        ff_collection.insert_one(store_info)


locations = "Coordinates.csv"

with open(locations, 'rt') as file:
    reader = csv.reader(file)
    locations = list(reader)

ff_restaurants = "FF_Restaurant.csv"

with open(ff_restaurants, 'rt') as file:
    reader = csv.reader(file)
    ff_restaurants = list(reader)

for ff in ff_restaurants:
    for location in locations:
        lat = str(location[1])
        lng = str(location[0])
        ff_search(lat, lng, str(ff))
