from flask.ext.login import UserMixin
from cal import db
import facebook


class User(db.Document, UserMixin):
  google_key = db.StringField()
  fb_key = db.StringField()