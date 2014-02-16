from flask.ext.login import UserMixin
from cal import db
import facebook


class User(db.Model, UserMixin):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(200))
  password = db.Column(db.String(200), default='')
  name = db.Column(db.String(100))
  email = db.Column(db.String(200))
  active = db.Column(db.Boolean, default=True)

  def is_active(self):
    return self.active

  def facebook_me(self):
    token = self.social_auth.first().extra_data['access_token']
    graph = facebook.GraphAPI(token)
    profile = graph.get_object("me")
    return profile