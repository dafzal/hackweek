from flask import Flask, url_for, abort, request, render_template, redirect, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext import login
from raven.contrib.flask import Sentry

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mzuragfsrqnokk:cb5U50DdTvMIrJH1TtdH7zZxe6@ec2-54-235-132-177.compute-1.amazonaws.com:5432/ddia1c9eioov14'
#connect('project1', host='mongodb://localhost/database_name')
app.config['SECRET_KEY'] = 'supersecretkey12345'
db = SQLAlchemy(app)
sentry = Sentry(app)


app.config['SOCIAL_AUTH_USER_MODEL'] = 'cal.models.User'
from social.apps.flask_app.routes import social_auth
app.register_blueprint(social_auth)
from social.apps.flask_app.models import init_social
init_social(app, db)

app.config['SOCIAL_AUTH_AUTHENTICATION_BACKENDS'] = (
    'social.backends.facebook.FacebookOAuth2',
    'social.backends.facebook.FacebookAppOAuth2',
)
app.config['SOCIAL_AUTH_FACEBOOK_KEY'] = '1463976000492316'
app.config['SOCIAL_AUTH_FACEBOOK_SECRET'] = 'b2cb45b169e0349eeacab0cf9fdaee3d'
app.config['SOCIAL_AUTH_FACEBOOK_SCOPE'] = ['email','user_about_me','user_events']

from social.apps.flask_app.template_filters import backends
app.context_processor(backends)

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
    	return User.query.get(int(userid))
    except (TypeError, ValueError):
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