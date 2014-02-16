from flask.ext.login import UserMixin
from cal import db
import facebook
from flask.ext.security import Security, MongoEngineUserDatastore, \
    UserMixin, RoleMixin, login_required
import requests
from dateutil import parser
import datetime

def get_match(users, start, end, duration):
  events_list = [u.fb_events() for u in users]
  while start < end:
    if all(is_available(events, start) for events in events_list):
      return start
    start += datetime.timedelta(minutes=30)

def is_available(events, time, duration):
  # duration is ignored
  print 'checking ' + str(time) + ' in ' + str(events)
  for e in events:
    if e['start_time'] < time and e['end_time'] > time:
      print 'miss ' + str(e)
      return False
  return True

events_a = [
  {
    'start_time': datetime.datetime(month=2,day=15,year=2014, hour=5),
    'end_time': datetime.datetime(month=2, day=15, year=2014, hour=7)
  },
  {
    'start_time': datetime.datetime(month=2,day=15,year=2014, hour=6),
    'end_time': datetime.datetime(month=2, day=15, year=2014, hour=7)
  }
]
events_b = [
  {
    'start_time': datetime.datetime(month=2,day=15,year=2014, hour=8),
    'end_time': datetime.datetime(month=2, day=15, year=2014, hour=10)
  },
  {
    'start_time': datetime.datetime(month=2,day=15,year=2014, hour=9),
    'end_time': datetime.datetime(month=2, day=15, year=2014, hour=11)
  }
]

class User(db.Document, UserMixin):
  fb_id = db.StringField()
  google_id = db.StringField()
  google_key = db.StringField()
  fb_key = db.StringField()
  created_events = db.ReferenceField('Event')
  username = db.StringField()
  name = db.StringField()
  active = db.BooleanField(default=True)
  confirmed_at = db.DateTimeField()
  roles = db.ListField(db.ReferenceField('Role'), default=[])
  def to_json(self):
    return {
        'id': self.id,
        'fb_key': self.fb_key,
        'google_key': self.google_key,
    }  

  def fb_events(self):
    url = 'https://graph.facebook.com/me/events?access_token=%s'
    ret = []
    r = requests.get(url % self.fb_key).json()
    print str(r)
    ret = r['data']
    next = r['paging']['next']
    while next:
      r = requests.get(next).json()
      print str(r)
      ret += r['data']
      try:
        next = r['paging']['next']
      except:
        next = None

    for r in ret:
      if 'T' not in r['start_time']:
        r['end_time'] = r['start_time'] + 'T23:59:59-0800'
        r['end_time'] = parser.parse(r['end_time']).replace(tzinfo=None)
        r['start_time'] += 'T00:00:00-0800'
        r['start_time'] = parse.parse(r['start_time']).replace(tzinfo=None)
    ret = [x for x in ret if x['rsvp_status'] == 'available']
    return sorted(ret, key=lambda x: x['start_time'])


  def get_friends(self):
    graph = facebook.GraphAPI(self.fb_key)
    friends = graph.get_connections("me", "friends")
    return friends['data']

  def get_available_times(self):
    times = []
    # fb
    graph = facebook.GraphAPI(self.fb_id)
    profile = graph.get_object("me")
    friends = graph.get_connections("me", "friends")
    pass

def dump_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]

class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)


class Connection(db.Document):
    user_id = db.ReferenceField('User')
    provider_id = db.StringField()
    provider_user_id = db.StringField()
    access_token = db.StringField()
    secret = db.StringField()
    display_name = db.StringField()
    profile_url = db.StringField()
    image_url = db.StringField()
    rank = db.IntField()
class Response(db.Document):
    responder = db.ReferenceField('User')
    event = db.ReferenceField('Event')
    response = db.BooleanField()

class Event(db.Document):
    name = db.StringField(default='New Event')
    from_time_range = db.DateTimeField()
    to_time_range = db.DateTimeField()
    location = db.StringField()
    duration_minutes = db.IntField()
    invitees = db.ListField(db.ReferenceField('User'))
    final_from_field = db.DateTimeField()
    suggested_from_time = db.DateTimeField()
    status = db.StringField(default='started')
    creator = db.ReferenceField('User')
    threshold = db.IntField()

    def get_suggested_time(self):
      pass

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

