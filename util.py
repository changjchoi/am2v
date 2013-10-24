#!/usr/bin/python

import datetime
#import simplejson as json
import json
from collections import namedtuple

# all time code is.... 
# reference strftime('%Y/%m/%d - %H:%M:%S')
# Above code will be - 2013/10/18 - 18:23:44
def current_time() :
  return datetime.datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S')

def single_quote(value) :
  return value.replace("'", r"\'")

def escape_single_quote(value) :
  return value.replace("'", r"'\''")

# I want to change json to dictionary type
def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())
def json2obj(data): return json.loads(data, object_hook=_json_object_hook)

class Object :
  def tojson(self) :
    return json.dumps(self, default=lambda o: o.__dict__)

class CommandFormat(Object) :
  def __init__(self) :
    self.command = ""
    self.email = ""
  def fromjson(self, json_str) :
    made_dict = json.loads(json_str)
    self.command = made_dict['command'] 
    self.email = made_dict['email']

class ReturnFormat(Object) :
  def __init__(self) :
    self.command = ""
    self.code = ""
  def fromjson(self, json_str) :
    made_dict = json.loads(json_str)
    self.command = made_dict['command'] 
    self.code = made_dict['code']


class CommandMessage(CommandFormat) :
  def __init__(self) :
    self.time = ""
    self.poi = []
    self.message = ""
    self.filename = ""

class Room(Object) :
  def __init__(self) :
    self.room = "korea"
    self.counter = 0
  def fromjson(self, json_str) :
    made_dict = json.loads(json_str)
    self.room = made_dict['room'] 
    self.counter= made_dict['counter']

class PointRoom(Object) :
  def __init__(self) :
    self.room = "korea"
    self.email = ""
    self.counter = 0

class MessageBox(Object) :
  def __init__(self) :
    self.email = ""
    self.bucket = 0
    self.time = ""
    self.data = []
  def fromjson(self, json_str) :
    made_dict = json.loads(json_str)
    self.email = made_dict['email'] 
    self.bucket = made_dict['bucket']
    self.time = made_dict['time']
    self.data = made_dict['data']

class Message(Object) :
  def __init__(self) :
    self.email = ""
    self.poi = []
    self.mtime = ""
    self.message = []
    self.filename = []
  def fromjson(self, json_str) :
    made_dict = json.loads(json_str)
    self.email = made_dict['email'] 
    self.poi = made_dict['poi']
    self.mtime = made_dict['mtime']
    self.message = made_dict['message']
    self.filename = made_dict['filename']

class PointBox(Object) :
  def __init__(self) :
    self.room = ""
    self.email = ""
    self.bucket = 0
    self.time = ""
    self.data = []
  def fromjson(self, json_str) :
    made_dict = json.loads(json_str)
    self.room = made_dict['room'] 
    self.email = made_dict['email']
    self.bucket = made_dict['bucket']
    self.time = made_dict['time']
    self.data = made_dict['data']

class Point(Object) :
  def __init__(self) :
    self.poi = ""
    self.mtime = ""
  def fromjson(self, json_str) :
    made_dict = json.loads(json_str)
    self.poi = made_dict['poi'] 
    self.mtime = made_dict['mtime']

class PointCommand(Object) :
  def __init__(self) :
    self.type = ""
    self.email = ""
    self.time = ""
    self.poi = []
  def fromjson(self, json_str) :
    made_dict = json.loads(json_str)
    self.type = made_dict['type']
    self.email = made_dict['email']
    self.time = made_dict['time']
    self.poi = made_dict['poi'] 






