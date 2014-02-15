from flask import Flask, url_for, abort, request, render_template, redirect
from flask.ext.mongoengine import MongoEngine

app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {
    'HOST': 'mongodb://pieota3:passcodeabc123@paulo.mongohq.com:10069/calendar',
    'DB': 'calendar',
    # 'USERNAME': 'pieota',
    # 'PASSWORD': 'asd789supersonicpie234',
    # 'HOST': 'candidate.2.mongolayer.com',
    # 'PORT': 10088,
}
#connect('project1', host='mongodb://localhost/database_name')
app.config['SECRET_KEY'] = 'supersecretkey12345'
db = MongoEngine(app)

from cal import routes
from cal import models

if __name__ == '__main__':
  app.run()