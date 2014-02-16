from flask import Flask, url_for, abort, request, render_template, redirect, g
from flask.ext.mongoengine import MongoEngine
from flask.ext import login
from raven.contrib.flask import Sentry

app = Flask(__name__)


app.config['MONGODB_SETTINGS'] = {
    'DB': 'calendar',
    'HOST': 'paulo.mongohq.com',
    'PORT': 10069,
    'USERNAME': 'pieota4',
    'PASSWORD': 'pieota4abc',
    # 'USERNAME': 'pieota',
    # 'PASSWORD': 'asd789supersonicpie234',
    # 'HOST': 'candidate.2.mongolayer.com',
    # 'PORT': 10088,
}
#connect('project1', host='mongodb://localhost/database_name')
app.config['SECRET_KEY'] = 'supersecretkey12345'
db = MongoEngine(app)
sentry = Sentry(app)

app.config['SOCIAL_AUTH_FACEBOOK_KEY'] = '1463976000492316'
app.config['SOCIAL_AUTH_FACEBOOK_SECRET'] = 'b2cb45b169e0349eeacab0cf9fdaee3d'
app.config['SOCIAL_AUTH_GOOGLE_KEY'] = '610521713571-3v093rdrgspspv9gf5kcgsgj4s1adjqj.apps.googleusercontent.com'
app.config['SOCIAL_AUTH_GOOGLE_SECRET'] = 'mKH_3DZFWGdP_NrG168OFNMn'
app.config['SOCIAL_AUTH_FACEBOOK_SCOPE'] = ['email','user_about_me','user_events']
app.config['SOCIAL_AUTH_GOOGLE_SCOPE'] = ['calendar']
app.config['SOCIAL_GOOGLE'] = {
    'consumer_key': '610521713571.apps.googleusercontent.com',
    'consumer_secret': 'FJgybwIs_wU8eautMC41PRE0'
}


login_manager = login.LoginManager()
login_manager.login_view = 'main'
login_manager.login_message = ''
login_manager.init_app(app)


@app.before_request
def global_user():
    g.user = login.current_user

from cal.models import User
@login_manager.user_loader
def load_user(userid):
    try:
    	return User.objects.get(id=userid)
    except:
        pass
# Make current user available on templates
@app.context_processor
def inject_user():
    try:
        return {'user': g.user}
    except AttributeError:
        return {'user': None}


from cal import routes
from cal import models

if __name__ == '__main__':
  app.run()