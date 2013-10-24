
from pymongo import MongoClient
from gridfs import GridFS
import ast
import datetime
from util import *
import magic

# Data save in MongoDB
# Received Data is position data type
# another data is contents data 
data_insert_qry = '{ "user" : "%s", "time" : "%s", "poi" : [%s] }'
data_update_qry1 = '{ "user" : "%s" }'
data_update_qry2 = '{ "$push" : { "poi" : %s }}'

def find_user(user_id) :
  qry= { 'user' : user_id }
  return db_user.find(qry).count()

# mongodb insert item 
# Bucket size 
msg_bucket_size = 10
def insert_msg(value) :
  room_name = "korea"
  room = Room()
  mb = MessageBox()
  m = Message()
  pv = json2obj(value)
  mb.email = pv.email
  mb.bucket_size = 0
  mb.time = current_time()
  # write message
  m.email = pv.email
  m.poi = pv.poi
  m.mtime = pv.time
  m.message = pv.message
  m.filename = pv.filename
  mb.data.append(m.__dict__)

  # call mongodb insert 
  qry = { "room" : room_name }
  msg_count = 0
  try :
    msg_count = db_room.find_one(qry, {"counter": 1})['counter']
  except :
    #db_room.insert({"room" : "korea", "msgs" : 0})
    db_room.insert(room.__dict__)

  print("msg_count = %d" % msg_count)
  bucket_size = int(msg_count / msg_bucket_size)
  try :
    if ((msg_count % msg_bucket_size) == 0) :
      mb.bucket = bucket_size
      db_msg.insert(mb.__dict__)
    else :
      qry_up = { "bucket" : bucket_size }
      print (qry_up)
      qry_up_item = { "$push" : { "data" : m.__dict__ }}
      print (qry_up_item)
      db_msg.update(qry_up, qry_up_item, upsert=False)
  except :
    return 

  # update room's message count 
  # There are no error. if code come here
  msg_count = msg_count + 1
  print("update msg_count = %d" % msg_count)
  db_room.update(qry, { "$set" : { "counter" : msg_count }}, upsert=False)

# Point Bucket number 
point_bucket_size = 100
def store_user_point(value) :
  room_name = "korea"

  pv = json2obj(value)
  
  pb = PointBox()
  pb.room = room_name
  pb.email = pv.email
  pb.bucket = 0
  pb.time = current_time()

  pt = Point()
  pt.poi = pv.poi
  pt.mtime = pv.time

  pt_room = PointRoom()
  pt_room.room = room_name
  pt_room.counter = 0
  pt_room.email = pv.email

  # call mongodb insert 
  qry = { "room" : room_name, "email" : pv.email }
  point_size = 0
  try :
    point_size = db_data.find_one(qry, {"counter": 1})['counter']
  except:
    # make new one
    db_data.insert(pt_room.__dict__)

  print("point_count = %d" % point_size)
  bucket_size = int(point_size / point_bucket_size)
  try : 
    if ((point_size % point_bucket_size) == 0) :
      pb.bucket = bucket_size
      pb.data.append(pt.__dict__)
      db_data.insert(pb.__dict__)
    else :
      qry_up = { "email" : pv.email, "bucket" : bucket_size }
      print (qry_up)
      qry_up_item = { "$push" : { "data" : pt.__dict__ }}
      print (qry_up_item)
      db_data.update(qry_up, qry_up_item, upsert=False)
  except :
    return
  # update room's message count 
  point_size = point_size + 1
  print("update point count = %d" % point_size)
  db_data.update(qry, { "$set" : { "counter" : point_size }} , upsert=False)

# /user/$user_id/$file_name format 
# Put a binary to GridFS directly.
def store_user_file(msg) :
  print("message size = %d" % len(msg.payload) )
  element_topic = msg.topic.split('/')
  element_topic_count = len(element_topic)
  email = element_topic[2]
  file_name = element_topic[3]
  print("********************************")
  print("email : " + email)
  print("file  : " + file_name)
  # mime type check, Using python magic 
  mime_type = magic.from_buffer(msg.payload, mime=True)
  print("check mime type is : " + mime_type)
  print("********************************")

  # inforce stop message, I will cover to put a msge for payload 
  db_fs.put(msg.payload, content_type=mime_type, filename=file_name)


def close() :
  db_client.close()

# instance mongo
db_client = MongoClient()
mongo_db = db_client.am2v
db_user = mongo_db.user
db_data = mongo_db.data
db_msg = mongo_db.msg
db_room = mongo_db.room
db_fs = GridFS(mongo_db)

