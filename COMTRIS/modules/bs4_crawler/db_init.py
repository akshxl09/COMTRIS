import os
from pymongo import *


def db_init():
    myclient = MongoClient(os.environ["COMTRIS_MONGODB_URI"])
    db = myclient['COMTRIS']
    col = db["master_config"]

    cnt_check = col.find_one({'key': 'quote_cnt'})
    if not cnt_check:
        col.insert_one({'key':'quote_cnt', 'value': 0})
    print("bs4 init complete")
if __name__ == '__main__':
    db_init()