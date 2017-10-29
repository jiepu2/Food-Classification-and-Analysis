import argparse, urllib, json
from datetime import datetime
from pymongo import MongoClient, GEOSPHERE
from pymongo.errors import (PyMongoError, BulkWriteError)
import generate_FoodList
import csv
import matplotlib.pyplot as plt
import time

client = MongoClient('localhost', 15986)
db = client['food_analysis']
filter_collection = db['pic_Info']
suburbs = db['suburbs']
richArea = ['camberwell']


def chooseArea(statistics, x):  # parameter is the statistics
    chosenArea = dict(sorted(statistics.items(), key=lambda item: sum(item[1].values()), reverse=True)[:x])
    return chosenArea


def chooseFood(suburb, x):  # parameter is the statistic[suburb]
    chosenFood = dict(sorted(suburb.items(), key=lambda item: item[1], reverse=True)[:x])
    return chosenFood


def determineFoodRange(foods, suburb):
    foods.update({'others': sum(suburb.values()) - sum(foods.values())})
    return foods


def draw_pie_chart(statistics):
    areas = chooseArea(statistics, 50)  # Choose Top X areas with most pictures to analyze
    for suburb in areas:
        plt.title(suburb+' Lunch')
        foods = chooseFood(statistics[suburb], 20)  # mewenti
        foodRange = determineFoodRange(foods, statistics[suburb])
        plt.pie([float(v) for v in foodRange.values()], labels=[k for k in foodRange.keys()],
                autopct='%1.1f%%')
        plt.show()
    return


def get_suburb(location):
    suburb_info = suburbs.find_one({"geometry": {"$geoIntersects": {"$geometry": location}}})
    suburb = 'None'
    if suburb_info:
        suburb = suburb_info['properties']['SA2_NAME16']
    return suburb


def suburb_statistics11():
    statistics = {}
    i = 0

    for item in filter_collection.find().limit(50000):
        classification = item['pic_pred']  # 以食物预测为分类依据
        location = item['pic_loc']  # 获取地点
        suburb = get_suburb(location)  # 获取地点所在area
        if suburb != 'None':  # 如果suburb不是空
            if suburb in statistics.keys():  # 如果有了这个suburb
                if classification in statistics[suburb].keys():  # 如果有了这个食物
                    statistics[suburb][classification] += 1  # foodCount += 1
                else:
                    statistics[suburb][classification] = 1  # foodCount = 1
            else:  # 如果这个suburb还没出现过
                statistics[suburb] = {}  # 建一个新的
                statistics[suburb][classification] = 1  # foodCount = 1
    writeStatisticCSV(statistics)
    return statistics


def getPeriodByTimestamp(timestamp):
    timePeriod = {'Breakfast': range(6, 9), 'Brunch': range(9, 11), 'Lunch': range(11, 15),
                  'Afternoon_Tea': range(15, 17), 'Dinner': range(17, 21),
                  'Late_Night_Supper': [21, 22, 23, 24, 1, 2, 3, 4, 5],
                  }
    st = time.localtime(timestamp)
    times = str(time.strftime('%Y-%m-%d %H:%M:%S', st))
    period = int(times.split(' ')[1].split(':')[0])
    for keys, values in timePeriod.items():
        if period in values:
            return keys


def suburb_statistics(timePoint):
    statistics = {}
    i = 0

    for item in filter_collection.find().limit(50000):
        classification = item['pic_pred']
        location = item['pic_loc']
        timestamp = item.get('pic_time')
        if timestamp is not None:
            period = getPeriodByTimestamp(timestamp)
            suburb = get_suburb(location)
            print(period)
            if period == timePoint and suburb != 'None':
                if suburb in statistics.keys():  # 如果有了这个suburb
                    if classification in statistics[suburb].keys():  # 如果有了这个食物
                        statistics[suburb][classification] += 1  # foodCount += 1
                    else:
                        statistics[suburb][classification] = 1  # foodCount = 1
                else:  # 如果这个suburb还没出现过
                    statistics[suburb] = {}  # 建一个新的
                    statistics[suburb][classification] = 1  # foodCount = 1
        print (i)
        i += 1
    return statistics


def nutritionFacts_analsis(statistics, foodInfo):
    result = {}

    for suburb in statistics:
        healthStar, protein, fat, carbohydrate, calorie, sodium, weighterTotal = 0, 0, 0, 0, 0, 0, 0
        foodDistribution = statistics[suburb]
        print(foodDistribution)
        foodCount = sum(statistics[suburb].values())
        for foods in foodDistribution:
            nutrition = foodInfo.get(foods)
            if nutrition != None:
                isMain = nutrition[7]
                weightedNum = foodDistribution[foods] if isMain == 0 else 4 * foodDistribution[foods]
                num = foodDistribution[foods]
                healthStar += 1 * float(nutrition[0]) * num if isMain == 0 else 4 * float(nutrition[0]) * num
                protein += float(nutrition[2]) * num if isMain == 0 else 4 * float(nutrition[2]) * num
                fat += float(nutrition[3]) * num if isMain == 0 else 4 * float(nutrition[3]) * num
                carbohydrate += float(nutrition[4]) * num if isMain == 0 else 4 * float(nutrition[4]) * num
                calorie += float(nutrition[5]) * num if isMain == 0 else 4 * float(nutrition[5]) * num
                sodium += float(nutrition[6]) * num if isMain == 0 else 4 * float(nutrition[6]) * num
                weighterTotal += weightedNum
        healthStar = round(healthStar / weighterTotal, 2)
        protein = round(protein / weighterTotal, 2)
        fat = round(fat / weighterTotal, 2)
        carbohydrate = round(carbohydrate / weighterTotal, 2)
        calorie = round(calorie / weighterTotal, 2)
        sodium = round(sodium / weighterTotal, 2)
        nutritionFacts = [healthStar, protein, fat, carbohydrate, calorie, sodium, foodCount]
        result[suburb] = nutritionFacts

    return result

def ethnic_group(statistics,foodInfo):
    ethnic = {}
    for suburb in statistics:
        for food in statistics[suburb]:
            info = foodInfo.get(food)
            if info is not None:
                nation = info[1]
                if suburb in ethnic.keys():
                    if nation in ethnic[suburb]:
                        ethnic[suburb][nation] += statistics[suburb][food]
                    else:
                        ethnic[suburb][nation] = 1
                else:
                    ethnic[suburb] = {}
                    ethnic[suburb][nation] = 1
    print (ethnic)
    return ethnic


def writeNationCSV(ethics):
    with open('nation.csv', 'w+') as csv_file:
        writer = csv.writer(csv_file)
        for key in ethics.keys():
            writer.writerow([key]+[[nation,count] for nation,count in ethics[key].items()])


def calculateavgMelb():
    healthStar, protein, fat, carbohydrate, calorie, sodium, num = 0, 0, 0, 0, 0, 0, 0
    result = {}

    csvreader = csv.reader(open('nutritionFacts.csv'))
    firstLine = next(csvreader)
    for row in csvreader:
        key = row[0]
        result[key] = list(row[1:])

    for keys in result:
        info = [float(a) for a in result[keys]]
        healthStar += info[0] * info[6]
        protein += info[1] * info[6]
        fat += info[2] * info[6]
        carbohydrate += info[3] * info[6]
        calorie += info[4] * info[6]
        sodium += info[5] * info[6]
        num += info[6]
        print(info[6])

    result = [round(nutrition / num, 2) for nutrition in [healthStar, protein, fat, carbohydrate, calorie, sodium]]
    print(result)
    print(num)


def writeNutritionCSV(dict):
    with open('nutritionFacts.csv', 'w+') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['SA2','HealthStar','Protein','Fat','Carb','Calorie','Sodium','Quantity'])
        for key in dict.keys():
            writer.writerow ([key]+ [i for i in dict[key]])


def writeStatisticCSV(dict):
    with open('suburbStatistics.csv','w+') as csv_file:
        writer = csv.writer(csv_file)
        for suburbs, foods in dict.items():
            print (suburbs)
            print (foods)
            writer.writerow([suburbs,] + [[food,count] for food,count in foods.items()])

def overallAnalysis():
    result = {}
    for item in filter_collection.find().limit(50000):
        pic_pred = item['pic_pred']
        if pic_pred in result.keys():
            result[pic_pred] += 1
        else:
            result[pic_pred] = 1
    return result


def writeOverallCSV(result):
    with open('overall.csv','w+') as csv_file:
        writer = csv.writer(csv_file)
        print (result)
        for foods in result:
            print (foods)
            writer.writerow([foods]+[result[foods]])




def preprocess_FoodInfo():
    csvreader = csv.reader(open('FoodInfo.csv'))
    result = {}
    firstLine = next(csvreader)
    for row in csvreader:
        key = row[0]
        result[key] = row[1:]
    return result

def processStatistics():
    csvreader = csv.reader(open('suburbStatistics.csv'))
    result = {}
    for row in csvreader:
        key = row[0]
        result[key] = row[1:]
    print (result)
    return result


def analysis():

    # foodInfo = preprocess_FoodInfo()
    # # # timePeriod = input("please choose a time period")
    statistics = suburb_statistics('Late_Night_Supper')
    # result = nutritionFacts_analsis(statistics, foodInfo)
    # nation = ethnic_group(statistics,foodInfo)
    # writeNationCSV(nation)
    # print (111)
    # writeNutritionCSV(result)
    # print (222)
    # calculateavgMelb()

    draw_pie_chart(statistics)
    # # subUrbfoodInfo = processStatistics()
    # # AnalysisFromCSV(subUrbfoodInfo,foodInfo)



if __name__ == '__main__':
    analysis()
