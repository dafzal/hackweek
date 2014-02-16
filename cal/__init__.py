from flask import Flask, url_for, abort, request, render_template, redirect, g
from flask.ext.mongoengine import MongoEngine
from flask.ext import login
from raven.contrib.flask import Sentry
from flask.ext.social import Social
from flask.ext.social.datastore import MongoEngineConnectionDatastore
from flask.ext.social import Social,     login_failed, login_completed
from flask.ext.social.utils import get_connection_values_from_oauth_response
from flask.ext.login import login_user
# ... create the app ...
from flask.ext.login import user_logged_in


app = Flask(__name__)
app.config['SECURITY_POST_LOGIN'] = '/profile'


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

# app.config['SOCIAL_AUTH_FACEBOOK_KEY'] = '1463976000492316'
# app.config['SOCIAL_AUTH_FACEBOOK_SECRET'] = 'b2cb45b169e0349eeacab0cf9fdaee3d'
# app.config['SOCIAL_AUTH_GOOGLE_KEY'] = '610521713571-3v093rdrgspspv9gf5kcgsgj4s1adjqj.apps.googleusercontent.com'
# app.config['SOCIAL_AUTH_GOOGLE_SECRET'] = 'mKH_3DZFWGdP_NrG168OFNMn'
# app.config['SOCIAL_AUTH_FACEBOOK_SCOPE'] = ['email','user_about_me','user_events']
# app.config['SOCIAL_AUTH_GOOGLE_SCOPE'] = ['calendar']
app.config['SOCIAL_GOOGLE'] = {
    'consumer_key': '610521713571-3v093rdrgspspv9gf5kcgsgj4s1adjqj.apps.googleusercontent.com',
    'consumer_secret': 'mKH_3DZFWGdP_NrG168OFNMn',
    'request_token_params': {'scope': 'profile https://www.googleapis.com/auth/calendar.readonly'},
}
app.config['SOCIAL_FACEBOOK'] = {
    'consumer_key': '1463976000492316',
    'consumer_secret': 'b2cb45b169e0349eeacab0cf9fdaee3d',
    'request_token_params': {'scope': 'email,user_about_me,user_events'},
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
      print 'loading user ' + userid
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

@login_failed.connect_via(app)
@login_completed.connect_via(app)
def on_login_failed(sender, provider, oauth_response):
    print('Social Login Failed via %s; '
                     '&oauth_response=%s' % (provider.name, oauth_response))
    fb = provider.name.lower() == 'Facebook'.lower()
    token = oauth_response['access_token']
    cv = get_connection_values_from_oauth_response(provider, oauth_response)
    print str(provider)
    print str(oauth_response)
    print str(cv)
    print 'token is ' + token
    if login.current_user.is_authenticated():
      print 'current user is authenticated not creating new'
      u = login.current_user
      if fb:
        u.fb_key = token
      else:
        u.google_key = token
      u.save()
    else:
      try:
        if fb:
          u = User.objects.get(fb_id = cv['provider_user_id'])
          u.fb_key = token
        else:
          u = User.objects.get(google_id=cv['provider_user_id'])
          u.google_key = token
        u.save()
        login_user(u)
        return
      except:
        if fb:
          u = User(fb_id=cv['provider_user_id'], name=cv['full_name'], fb_key = token)
        else:
          u = User(google_id=cv['provider_user_id'], name=cv['display_name']['givenName'] + ' ' + cv['display_name']['familyName'], google_key = token)
        u.save()
        login_user(u)
        return

from cal import models
from cal.models import User, Connection, Role

from flask.ext.security import Security, MongoEngineUserDatastore, \
    UserMixin, RoleMixin, login_required
from flask.ext.social import Social
from flask.ext.social.datastore import MongoEngineConnectionDatastore

security = Security(app, MongoEngineUserDatastore(db, User, Role))
social = Social(app, MongoEngineConnectionDatastore(db, Connection))

from cal import routes
  

if __name__ == '__main__':
  app.run()