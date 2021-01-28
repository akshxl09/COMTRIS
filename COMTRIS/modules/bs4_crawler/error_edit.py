import os
from pymongo import *
myclient = MongoClient(os.environ["COMTRIS_MONGODB_URI"])
db = myclient['COMTRIS']
col = db['pc_quote']

 
col.update({}, {'$inc' : {'id' : 2000000}}, multi=True) # id 200만 증가

# col.update({}, {'$inc' : {'id' , '2000000'}})
# 이 에러는 key : value를 맞추지 않은 경우에 발생한다.
# bson.errors.InvalidDocument: cannot encode  object: {2000000, 'id'}, of type: <class 'set'>

# updateMany는 하나의 document의 여러 키 값을 바꿀 때 사용하는 것이다.
# update는 하나의 document의 하나의 키 값을 변경할 때 사용한다.
# 여러개의 document를 선택하려면, update의 multi를 True로 바꾸면 된다.
