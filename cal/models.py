from flask.ext.login import UserMixin
from cal import db
import facebook

users = db.Table('users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
)

class User(db.Model, UserMixin):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(200))
  password = db.Column(db.String(200), default='')
  name = db.Column(db.String(100))
  email = db.Column(db.String(200))
  active = db.Column(db.Boolean, default=True)
  created_events = db.relationship('Event', backref='user',
                            lazy='dynamic')

  def is_active(self):
    return self.active

  def facebook_me(self):
    token = self.social_auth.first().extra_data['access_token']
    graph = facebook.GraphAPI(token)
    profile = graph.get_object("me")
    return profile

  def to_json(self):
    return {
        'id': self.id,
        'username': self.username,
        'name': self.name
    }  

def dump_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), default='New Event')
    from_time_range = db.Column(db.DateTime)
    to_time_range = db.Column(db.DateTime)
    location = db.Column(db.String(200))
    duration_minutes = db.Column(db.Integer)
    invitees = db.relationship('User', secondary=users,
        backref=db.backref('events', lazy='dynamic'))
    final_from_time = db.Column(db.DateTime)
    suggested_from_time = db.Column(db.DateTime)
    status = db.Column(db.String(200), default='started')
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    threshold = db.Column(db.Integer)

    def to_json(self, is_creator=False):
        json = {
            'id': self.id,
            'name': self.name,
            'duration_minutes': self.duration_minutes,
            'status': status,
            'creator_id': creator_id,
            'invitees': self.get_invitees_json
        }
        if status == 'finalized':
            json = json.update({
                'final_from_time': dump_datetime(final_from_time)
            })
        elif is_creator:
            json = json.update({
                'from_time_range': dump_datetime(from_time_range),
                'to_time_range': dump_datetime(to_time_range),
                'threshold': threshold
            })
        else:
            json = json.update({
                'suggested_from_time': dump_datetime(suggested_from_time)
            })
        return json

    @property
    def get_invitees_json(self):
       return [ invitee.to_json for invitee in self.invitees]

