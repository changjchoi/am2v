from flask import Flask, url_for, redirect, render_template, request
from flask import jsonify
from flask.ext.mongoengine import MongoEngine
from flask import make_response
from flask import send_file

from wtforms import form, fields, validators

from flask.ext import admin
#from flask.ext.login import login
import flask.ext.login as login
from flask.ext.admin.contrib.mongoengine import ModelView
from flask.ext.admin import helpers
from flask.ext.pymongo import PyMongo
import datetime
import simplejson as json
from util import *
import os
from decimal import Decimal

# mosquitto broker connection -- drop
import mosquitto

from subprocess import PIPE, STDOUT, Popen


# it's Debug... import
from flask.ext.login import AnonymousUserMixin

from flask import logging
import time
log = logging.getLogger('werkzeug')
#log = logging.getLogger()
count = 0

# Create application
app = Flask(__name__)

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'

# MongoDB settings
app.config['MONGODB_SETTINGS'] = {'DB': 'am2v'}
db = MongoEngine()
db.init_app(app)

# Hum~~ MongoDB another tools
app.config['MONGO_DBNAME'] = 'am2v'
mongo = PyMongo(app)


# Create user model. For simplicity, it will store passwords in plain text.
# Obviously that's not right thing to do in real world application.
class User(db.Document):
  # duplicate error for Mongoengine... 
  '''
  meta = { 
    'abstract' : True, 
  }
  '''
  #login = db.StringField(max_length=80, unique=True)
  # email login 
  email = db.StringField(max_length=120, unique=True)
  name = db.StringField(max_length=64)
  password = db.StringField(max_length=64)

  # Flask-Login integration
  def is_authenticated(self):
    return True

  def is_active(self):
    return True

  def is_anonymous(self):
    return False

  def get_id(self):
    return str(self.id)

  # Required for administrative interface
  def __unicode__(self):
    return self.user


# Define login and registration forms (for flask-login)
class LoginForm(form.Form):
  email = fields.TextField(validators=[validators.required()])
  password = fields.PasswordField(validators=[validators.required()])

  def validate_login(self, field):
    user = self.get_user()

    if user is None:
      raise validators.ValidationError('Invalid user')

    if user.password != self.password.data:
      raise validators.ValidationError('Invalid password')

  # login or user ?, what is correct parameter ? vagues thing
  def get_user(self):
    return User.objects(email=self.email.data).first()


class RegistrationForm(form.Form):
  #login = fields.TextField(validators=[validators.required()])
  #user = fields.TextField(validators=[validators.required()])
  email = fields.TextField()
  name = fields.TextField()
  password = fields.PasswordField(validators=[validators.required()])

  def validate_login(self, field):
    if User.objects(email=self.email.data):
      raise validators.ValidationError('Duplicate username')

# Anonymous User Define class
class Anonymous(AnonymousUserMixin):
  def __init__(self):
    self.email = 'guest@guest.com'

# Initialize flask-login
def init_login():
  login_manager = login.LoginManager()
  login_manager.setup_app(app)
  # Is it possible ?.. class?
  login_manager.anonymous_user = Anonymous

  # Create user loader function
  # cj: class User returns user objects
  @login_manager.user_loader
  def load_user(user_id):
    return User.objects(id=user_id).first()


# Create customized model view class
class MyModelView(ModelView):
  def is_accessible(self):
    return login.current_user.is_authenticated()


# Create customized index view class
class MyAdminIndexView(admin.AdminIndexView):
  '''
  @admin.expose('/')
  def index(self):
    return "Hello F !"
  '''
  def is_accessible(self):
    return login.current_user.is_authenticated()

# GooglMap Display Test 
'''
class MapView(admin.BaseView):
  @admin.expose('/')
  def index(self):
    return self.render('mapview.html')
'''

# Flask views
@app.route('/')
def index():
  return render_template('index.html', user=login.current_user)


@app.route('/login/', methods=('GET', 'POST'))
def login_view():
  form = LoginForm(request.form)
  if request.method == 'POST' and form.validate():
    user = form.get_user()
    login.login_user(user)
    return redirect(url_for('index'))

  return render_template('form.html', form=form)


@app.route('/register/', methods=('GET', 'POST'))
def register_view():
  form = RegistrationForm(request.form)
  if request.method == 'POST' and form.validate():
    user = User()

    form.populate_obj(user)
    user.save()

    login.login_user(user)
    return redirect(url_for('index'))

  return render_template('form.html', form=form)


@app.route('/logout/')
def logout_view():
  login.logout_user()
  return redirect(url_for('index'))

def _on_dummy(mosq, obj, rc) :
  pass

def _on_publish(mosq, obj, rc) :
  log.warning('###### some thing')
  mosq.disconnect()

# this function is called by moquitto client broker 
def _on_mosquitto_connect(mosq, obj, rc):
  pass
  # file information and user 
  '''
  log.warning(request.files.get('file'))
  log.warning(login.current_user.get_id())
  log.warning(login.current_user.email)
  '''
  log.warning("start come here ##################")

  req_file = request.files['file']

  if req_file:
    mosq.publish('/user/%s/%s/upload' % (email, filename), req_file.read()) 
    log.warning('coming here')
  
  send_write_msg = CommandMessage()
  send_write_msg.command = "message"
  send_write_msg.email = login.current_user.email
  send_write_msg.time = current_time()
  send_write_msg.poi = [127, 60]
  send_write_msg.message = request.form['body']
  send_write_msg.filename = req_file.filename

#mosq.publish('/user/command', send_write_msg.tojson())
#mosq.publish('/user/command', "Test TEst")
  log.warning(send_write_msg.tojson())

  log.warning("end here ##################")
#mosq.loop(-1)
#mosq.disconnect()

@app.route('/write_message', methods=['POST'])
def _write_message() :
  # check file name and each contents
  #log.warning(request.files.get('file'))
  log.warning(request.form['body'])

  req_file = None
  req_file_name = None
  pt_lon = 0.0
  pt_lat = 0.0
  try :
    # Test... needed .. 
    req_file = request.files['file']
    req_file_name = req_file.filename
  except :
    log.warning("******* Test 1 -----")
    req_file_name = ""

  try :
    pt_lon = float(request.form['pt_lon'])
    pt_lat = float(request.form['pt_lat'])
    log.warning("******* Test 0 -----" + request.form['pt_lon'])
    log.warning("******* Test 0 -----" + request.form['pt_lat'])
  except :
    pass


  if req_file:
    shell_cmd = "mosquitto_pub -t "
    shell_cmd += "/user/%s/%s/upload -s " % (login.current_user.email, 
                                             req_file.filename)
    '''
    p = Popen([shell_cmd], shell=True, stdin= PIPE)
    p.stdin.write(req_file.read())
    p.communicate()[0]
    '''
    p = os.popen(shell_cmd, 'w', req_file.content_length)
    p.write(req_file.read())
    p.close()

  send_write_msg = CommandMessage()
  send_write_msg.command = "message"
  send_write_msg.email = login.current_user.email
  send_write_msg.time = current_time()
  send_write_msg.poi = [pt_lon, pt_lat]
  send_write_msg.message = request.form['body']
  send_write_msg.filename = req_file_name

  #mqtt_client.loop()
  # single quote problem.. arised..
  # force control
  shell_cmd = "mosquitto_pub -t /user/command -m "
  shell_cmd += "'" + escape_single_quote(send_write_msg.tojson()) + "'"
  Popen([shell_cmd], shell=True)
  log.warning(shell_cmd)
  

  # hum, need ajax call... in client 
  # return redirect(url_for('index'))



  # plz... working
  '''
  mqtt_client = mosquitto.Mosquitto()
  mqtt_client.connect('125.131.73.166', 1883, 60)
  mqtt_client.on_connect = _on_mosquitto_connect
  mqtt_client.on_message = _on_dummy
  mqtt_client.on_publish = _on_publish
  mqtt_client.on_subscribe = _on_dummy

  send_write_msg = CommandMessage()
  send_write_msg.command = "message"
  send_write_msg.email = login.current_user.email
  send_write_msg.time = current_time()
  send_write_msg.poi = [127, 60]
  send_write_msg.message = request.form['body']
  send_write_msg.filename = req_file.filename

  while mqtt_client.loop() == 0:
    mqtt_client.publish("/user/command", send_write_msg.tojson())
    time.sleep(0.2)
    log.warning("main loop in mqtt.. #####")
    pass
  '''

  return '' 

# This code will send a mongodb' gridfs binary data to a client
@app.route('/media/<path:filename>')
def get_media(filename) :
  log.warning('request media file : %s' % filename) 
  # client ... error arised, because of no content-type header !
  # so...
  '''
  return send_file(mongo.send_file(filename), 
      attachment_filename=filename, as_attachment=True)
  '''
  # flask - PyMongo alway have a Response Header
  # We Don't add header in send_file of flask 
  return mongo.send_file(filename)

@app.route('/media_test/<path:filename>')
def get_test_media(filename) :
  return send_file(filename)


@app.route('/json_test')
def json_get_test():
  msg = { 'message' : 'hard to coding' }
  return jsonify(msg)
    
@app.route('/new_message', methods=('GET', 'POST'))
def make_new_message():
  msg = {}
  # data check ... @todo 
  # init value is msg_s = msg_e = 0
  msg_s = int(request.form['msg_s'])
  msg_e = int(request.form['msg_e'])
  msg_reverse = int(request.form['msg_reverse'])
  log.warning('** msg start = %d - msg end = %d' % (msg_s, msg_e))

  # connect mongodb and get a msg count
  # We supposes first time to be the region in korea
  last_msg_index = 0
  # We put a list less than 10 msgs
  one_page = 20
  request_msg_count = abs(msg_e - msg_s)
  # small index = msg_s, large index = msg_e
  if (msg_s > msg_e) : 
    msg_s, msg_e = msg_e, msg_s

  if (request_msg_count == 0 and msg_e != 0) :
    msg = { 'msg_s' : msg_s, 'msg_e' : msg_e, 'data' : {} }
    return jsonify(msg)

  rcv_obj = mongo.db.room.find_one( { 'room' : 'korea' } )
  # Are there exist an objects ?
  last_msg_index = int(rcv_obj['counter']) 
  log.warning("last message index = %d" % (last_msg_index))
  # Default value is set by User.
  if (msg_s == 0 and msg_e == 0) :
    msg_e = last_msg_index
    msg_s = last_msg_index - one_page

  if (msg_e > last_msg_index) :
    msg_e = last_msg_index

  if (msg_s < 0) :
    msg_s = 0

  # Do nothing.. 
  if (abs(msg_e-msg_s) == 0) :
    msg = { 'msg_s' : msg_s, 'msg_e' : msg_e, 'data' : {} }
    return jsonify(msg)
  # Make 10 items, only the reverse is zero
  if (msg_e - msg_s > 10 and msg_reverse == 0) :
    msg_s = msg_e - 10

  bucket_num_e = int((msg_e-1) / 10)
  bucket_num_s = int(msg_s / 10)
  '''
  # Ok... read all contents
  rcv_obj = mongo.db.msg.find_one( { 'bucket' : bucket_num_s } )
  msg_list = rcv_obj['data']
  # two page read
  if (bucket_num_s != bucket_num_e) :
    rcv_obj = mongo.db.msg.find_one( { 'bucket' : bucket_num_e } )
    msg_list_b = rcv_obj['data']
    msg_list = msg_list + msg_list_b
  '''
  msg_list = []
  for idx in range(bucket_num_s, bucket_num_e+1) : 
    log.warning("db read bucket index is = %d" % (idx))
    rcv_obj = mongo.db.msg.find_one( { 'bucket' : idx } )
    msg_list += rcv_obj['data']

  p_msg_e = msg_e - bucket_num_s * 10
  p_msg_s = msg_s - bucket_num_s * 10

  if (msg_reverse == 1) :
    msg_list_rvs = msg_list[p_msg_s:p_msg_e]
    msg_list_rvs.reverse()
    msg = { 'command' : 'new_message', 'msg_s' : msg_s, 'msg_e' : msg_e, 
      'msg_reverse' : msg_reverse, 
      'data' : msg_list_rvs }
  else :
    msg = { 'command' : 'new_message', 'msg_s' : msg_s, 'msg_e' : msg_e, 
      'data' : msg_list[p_msg_s:p_msg_e] }

  log.warning('** arraged msg start = %d - msg end = %d' % (msg_s, msg_e))
  log.warning('last msgs count = %d', last_msg_index) 
  log.warning(msg) 

  return jsonify(msg)

if __name__ == '__main__':
  # Initialize flask-login
  init_login()

  # Create admin
  admin = admin.Admin(app, 'Auth', index_view=MyAdminIndexView())

  # Add view
  admin.add_view(MyModelView(User))
  #admin.add_view(MapView(name='MapView'))

  # Start app
  app.run(debug=True, host='0.0.0.0')
