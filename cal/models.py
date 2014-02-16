from flask.ext.login import UserMixin
from cal import db
import facebook

class User(db.Document, UserMixin):
  google_key = db.StringField()
  fb_key = db.StringField()
  created_events = db.ReferenceField('Event')
  username = db.StringField()
  name = db.StringField()
  def to_json(self):
    return {
        'id': self.id,
        'fb_key': self.fb_key,
        'google_key': self.google_key,
    }  

def dump_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]

class Response(db.Document):
    responder = db.ReferenceField('User')
    event = db.ReferenceField('Event')
    response = db.BooleanField()

class Event(db.Document):
    name = db.StringField(default='New Event')
    from_time_range = db.DateTimeField()
    to_time_range = db.DateTimeField()
    location = db.StringField()
    duration_minites = db.IntField()
    invitees = db.ListField(db.ReferenceField('User'))
    final_from_field = db.DateTimeField()
    suggested_from_time = db.DateTimeField()
    status = db.StringField(default='started')
    creator = db.ReferenceField('User')
    threshold = db.IntField()

    def to_json(self, is_creator=False):
        json = {
            'id': self.id,
            'name': self.name,
            'duration_minutes': self.duration_minutes,
            'status': status,
            'creator_id': creator.id,
            'invitees': self.get_invitees_json
        }
        if self.status == 'finalized':
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

