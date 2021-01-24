from pymongo import MongoClient
import os, datetime

class Mongo():
    '''MongoDB Database Management'''

    def __init__(self):
        self.db_client = MongoClient(os.environ['COMTRIS_MONGODB_URI'])
        self.db_cursor = self.db_client['COMTRIS']

    def client(self):
        '''DB client cursor 반환'''
        return self.db_client

    def cursor(self):
        '''RAAS cursor 반환'''
        return self.db_cursor

    def __del__(self):
        self.db_client.close()

def db_init():
    db = Mongo()

    review_cnt_check = db.cursor()['master_config'].find_one({'key':'review_cnt'})
    gallery_cnt_check = db.cursor()['master_config'].find_one({'key':'gallery_cnt'})
    if not review_cnt_check:
        db.cursor()['master_config'].insert_one({'key':'review_cnt', 'value':1})
    if not gallery_cnt_check:
        db.cursor()['master_config'].insert_one({'key':'gallery_cnt', 'value':1})
    print('selenium_init complete...')

if __name__=="__main__":
    db_init()