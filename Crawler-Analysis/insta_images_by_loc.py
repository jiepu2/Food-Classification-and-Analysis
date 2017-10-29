import csv
import json
import analyze1
import requests
import generate_FoodList
from skimage import io
from pymongo import MongoClient
from CrawlerAndAnalysis import main
import generate_FoodList
import pprint

client_id = "fcea843200a7447b967cc616e9efa79d"  # client ID
client_secret = "eba26794ddee490687e35cdb172357d5"  # client Secret
redirect_uri = "http://localhost"  # redirect uri
grant_type = "authorization_code"  # default option provided by Instagram

client = MongoClient('localhost', 15984)
db = client['testdb']
filter_collection = db['picture']
original_collection = db['original']
timestamp_collection = db['timestamp']


def get_access_token():
    access_token = "2392735078.e029fea.b9d9af55ba704713b2a3f545279200bf"

    # "6043932862.e029fea.ff5885a49d8040c5baa08a1ef633fdf1"
    # "715368389.0912694.a9b928f66e5e4ed5997b9012e4ddc602"

    return access_token


def get_coordinates(locations):
    search = []
    for row in locations:
        if len(row):
            coordinate = []
            coordinate.append(row[0])
            coordinate.append(row[1])
            search.append(coordinate)
    return search


def media_search(lat, lng, access_token, timestamp):
    try:
        max_timestamp = timestamp
        while max_timestamp > timestamp - 3600:
            url = "https://api.instagram.com/v1/media/search?lat=" + lat + "&lng=" + lng + "&distance=5000" + "&access_token=" + access_token + "&max_timestamp=" + str(
                max_timestamp)
            r = requests.get(url)
            resp = json.loads(r.text)
            timestamps = []
            for i in range(len(resp['data'])):
                pic_url = resp['data'][i]['images']['standard_resolution']['url']  # getting the image url
                if original_collection.find({"pic_url": pic_url}).count() != 0:  # prevent duplicate
                    continue
                coordinates = tuple([resp['data'][i]['location']['longitude'], resp['data'][i]['location']['latitude']])
                pic_loc = {'type': 'Point', 'coordinates': coordinates}
                print (111)
                print (resp['data'][i]['user']['id'])
                post_id = resp['data'][i]['id']
                store_info = {'post_id': post_id, 'pic_loc': pic_loc, 'pic_url': pic_url}
                original_collection.insert_one(store_info)
                # p=requests.get(pic_url)
                # f_name=resp['data'][i]['id'] + '.jpg'
                # with open(f_name,'wb') as f:
                #     f.write(p.content)
                #     f.close()
                foodList = generate_FoodList.generate()
                tagsFromIns = resp['data'][i]['tags']
                isFood = False
                for food in foodList:
                    if food in tagsFromIns:
                        isFood = True
                        break  # tags = analyze1.analyze("{'url':'" + pic_url + "'}")
                analyze_result = analyze1.analyze("{'url':'" + pic_url + "'}")
                if(type(analyze_result) is dict):
                    print ("volume run out")
                    exit()
                if isFood or 'food' in analyze_result:
                    image = io.imread(pic_url)
                    score = main.predict_10_crop(main.np.array(image), 0)[0]  # score for each part of the pic
                    preds = main.ix_to_class[
                        main.collections.Counter(score).most_common(1)[0][0]]  # prediction for the pic
                    store_info = {'post_id': post_id, 'pic_pred': preds, 'pic_loc': pic_loc, 'pic_url': pic_url}
                    filter_collection.insert_one(store_info)
                    print(score)
                    print(main.ix_to_class[main.collections.Counter(score).most_common(1)[0][0]])
                timestamps.append(int(resp['data'][i]['created_time']))
                print(timestamps)
                time_info = {'timestamp': min(timestamps)}
                max_timestamp = min(timestamps) - 60
                print(time_info)
                timestamp_collection.drop()
                timestamp_collection.insert(time_info) # record the timestamp for each iteration
    except Exception as e:
        print(e)
        pass

locations = "./Coordinates.csv"

with open(locations, 'rt') as file:
    reader = csv.reader(file)
    locations = list(reader)

coordinates = get_coordinates(locations)
access_token = get_access_token()

startTime = timestamp_collection.find_one().get('timestamp')
timeStamp = range(1503498187, 1404600000, -3600)

for stamp in timeStamp:
    for item in coordinates:
        lat = str(item[1])
        lng = str(item[0])
        media_search(lat, lng, access_token, stamp)
