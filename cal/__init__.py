from flask import Flask, url_for, abort, request, render_template, redirect
from flask.ext.mongoengine import MongoEngine

app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {
   
}
#connect('project1', host='mongodb://localhost/database_name')
app.config['SECRET_KEY'] = 'supersecretkey123456'
db = MongoEngine(app)

if __name__ == '__main__':
  app.run()