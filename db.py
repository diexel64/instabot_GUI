from pymongo import MongoClient
import pandas as pd
from datetime import datetime

# Functions #


def check_in_collection(c, to_check):
    client = MongoClient('localhost', 27017)
    db = client.instagram
    collection = db.get_collection(c)
    return collection.find_one({'pic_id': to_check})


def add_to_mongo(c, dictionary):
    client = MongoClient('localhost', 27017)
    db = client.instagram
    collection = db.get_collection(c)
    collection.insert_one(dictionary)


def get_from_mongo(c):
    client = MongoClient('localhost', 27017)
    db = client.instagram
    collection = db.get_collection(c)
    nb = collection.find().count()
    all = collection.find({}, {'_id': 0, 'pic_id':1, 'username':1, 'hashtag':1, 'date':1, 'text':1})
    all = [x for x in all]
    all = pd.DataFrame.from_dict(all)
    return all, nb


def query_user(c, username):
    client = MongoClient('localhost', 27017)
    db = client.instagram
    collection = db.get_collection(c)
    res_username = collection.find({'username': username}, {'_id': 0, 'pic_id':1, 'username':1, 'hashtag':1, 'text':1, 'date':1})
    res_username = [x for x in res_username]
    res_username = pd.DataFrame.from_dict(res_username)
    return res_username


def query_date(c, date):
    client = MongoClient('localhost', 27017)
    db = client.instagram
    collection = db.get_collection(c)
    date = datetime(int(date.split('/')[2]), int(date.split('/')[1]), int(date.split('/')[0]))
    res_date = collection.find({'date': {'$gt': date}}, {'_id': 0, 'pic_id':1, 'username':1, 'hashtag':1, 'text':1, 'date':1})
    nb = res_date.count()
    res_date = [x for x in res_date]
    res_date = pd.DataFrame.from_dict(res_date)
    return res_date, nb


# Testing #

if __name__ == '__main__':
    client = MongoClient('localhost', 27017)
    db = client.instagram

    # Collections #
    FOLLOWED = db.FOLLOWED
    UNFOLLOWED = db.UNFOLLOWED
    LIKES = db.LIKES
    MESSAGES = db.MESSAGES
    BLOCKED = db.BLOCKED
