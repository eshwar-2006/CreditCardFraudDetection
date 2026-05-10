import os
from pymongo import MongoClient
from urllib.parse import quote_plus

MONGO_URI = os.environ.get('MONGO_URI', '')
MONGO_USER = os.environ.get('MONGO_USER', '')
MONGO_PASS = os.environ.get('MONGO_PASS', '')
MONGO_HOST = os.environ.get('MONGO_HOST', 'localhost')
MONGO_PORT = os.environ.get('MONGO_PORT', '27017')
MONGO_DB = os.environ.get('MONGO_DB', 'fraud_detection')


def get_connection_uri():
    if MONGO_URI:
        return MONGO_URI

    if MONGO_USER and MONGO_PASS:
        user = quote_plus(MONGO_USER)
        password = quote_plus(MONGO_PASS)
        return f'mongodb://{user}:{password}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}'

    return f'mongodb://{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}'


def get_database():
    client = MongoClient(get_connection_uri())
    return client[MONGO_DB]


def get_collection(name='predictions'):
    db = get_database()
    return db[name]
