from flask import render_template, redirect, jsonify
from flask.ext.login import login_required, logout_user, current_user
from flask import render_template, redirect, session, url_for, request
from flask.ext.login import login_required, logout_user

from cal import app
from cal import db
from oauth2client.client import OAuth2WebServerFlow
from apiclient.discovery import build_from_document, build
from oauth2client.file import Storage
from oauth2client.client import OAuth2Credentials
import httplib2
import datetime, time
from cal.models import User,Event
from cal import social
from dateutil import parser
@app.route('/')
def main():
  if current_user.is_authenticated():
    return render_template('dashboard.html', user_name=current_user.name)
  return render_template('home.html')

@app.route('/home')
def home():
  return render_template('home.html')


@login_required
@app.route('/done/')
def done():
  return render_template('done.html')

@login_required
@app.route('/friends')
def friends():
  return jsonify(current_user.get_friends())

@app.route('/logout')
def logout():
  """Logout view"""
  logout_user()
  return redirect('/')

@app.route('/add_fakedata')
def add_fakedata():
  user1 = User(username='frost_test',name='Frost Li TEST')
  user1.save()
  user2 = User(username='frost_test2', name='Hello world')
  user2.save()
  event = Event(name='Why not dinner?',from_time_range=datetime.datetime.now(),
    to_time_range=datetime.datetime.now() + datetime.timedelta(hours=2),
    location='birate',duration_minutes=120,creator=user2.id,threshold=1)
  event.invitees.append(user2)
  event.save()
  return 'done'

@app.route('/events/<user_id>')
def events(user_id):
  u = User.objects.get(id=user_id)
  created_events = Event.objects(creator=u)
  invited_events = Event.objects(invitees=u)
  results = {
    'created_events': [x.to_json() for x in created_events],
    'invited_events': [x.to_json() for x in invited_events],
  }
  return jsonify(**results)

@app.route('/events')
def all_events():
  u = current_user
  created_events = Event.objects(creator=u.id)
  invited_events = Event.objects(invitees=u.id)
  import ipdb
  ipdb.set_trace()
  results = {
    'created_events': ['a','b'],
    'invited_events': [x.to_json() for x in invited_events.to_json()]
  }
  return jsonify(results)

@app.route('/users')
def users():
  return jsonify(data=[x.to_json() for x in User.objects])

@login_required
@app.route('/events/add',  methods=['GET', 'POST'])
def add_event():
  data = request.values
  from_time_range = parser.parse(data['from_time_range'])
  to_time_range = parser.parse(data['to_time_range'])
  creator = current_user
  event = Event(name=data['name'],from_time_range=from_time_range,
    to_time_range=to_time_range,location=data['location'],duration_minutes=data['duration'],
    creator=creator.id,threshold=data['threshold'])
  for invitee_name in data.getlist('invitees'):
    u = User.objects.get(name__icontains=invitee_name)
    event.invitees.append(u)
  event.save()
  return 'OK'

@app.route('/events/respond')
def respond():
  data = reqeust.POST
  response = data['response']
  event = Event.objects.get(id=data['event_id'])
  responder = User.objects.get(id=data['responder'])
  r = Response(response=response, event=event, responder=responder)
  r.save()
  num_response = Response.objects(event=event).count()
  if num_response >= event.threshold:
    event.status = 'Finalized'
    event.final_from_field = event.suggested_from_time
    event.save()
    notify_users(event)
  return 'OK'

# send out emails/notifications to users
def notify_users(event):
  # for invitee in event.invitees:
  pass

@app.route('/google_connect', methods=['GET', 'POST'])
def google_connect():
  print 'current key ' + str(current_user.google_key)
  if not current_user.is_authenticated() or not current_user.google_key:
    return redirect(url_for('send_google'))

  credentials = OAuth2Credentials.from_json(current_user.google_key)

  if credentials is None or credentials.invalid == True:
    return redirect(url_for('send_google'))

  
  http = httplib2.Http()
  http = credentials.authorize(http)
  service = build("calendar", "v3", http=http)
  calendar_list = service.calendarList().list().execute()

  print calendar_list
  return redirect('/')

@app.route('/profile2')
def profile():
    return render_template(
        'profile.html',
        content='Profile Page',
        facebook_conn=social.facebook.get_connection())

@app.route('/test')
def test():
  if not current_user.google_key:
    return redirect(url_for('send_google'))
  credentials = OAuth2Credentials.from_json(current_user.google_key)

  if credentials is None or credentials.invalid == True:
      return redirect(url_for('send_google'))

  http = httplib2.Http()
  http = credentials.authorize(http)
  service = build("calendar", "v3", http=http)
  calendar_list = service.calendarList().list().execute()
  import ipdb
  ipdb.set_trace()
  ids = [x['id'] for x in calendar_list['items']]
  for calendar_id in ids:
    page_token = None
    while True:
      events = service.events().list(calendarId='primary', pageToken=page_token).execute()
      for event in events['items']:
        print event['summary']
      page_token = events.get('nextPageToken')
      if not page_token:
        break
  return str(calendar_list) + '\n' + str(current_user.facebook_me())

CLIENT_ID = '610521713571-3v093rdrgspspv9gf5kcgsgj4s1adjqj.apps.googleusercontent.com'
CLIENT_SECRET = 'mKH_3DZFWGdP_NrG168OFNMn'

@app.route('/send_google')
def send_google():
  flow = OAuth2WebServerFlow(client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    scope='https://www.googleapis.com/auth/calendar',
    redirect_uri='http://localhost:5000/oauth2callback',
    approval_prompt='force',
    access_type='offline')

  auth_uri = flow.step1_get_authorize_url()
  return redirect(auth_uri)

@app.route('/oauth2callback')
def oauth2callback():
  code = request.args.get('code')
  if code:
    # exchange the authorization code for user credentials
    flow = OAuth2WebServerFlow(CLIENT_ID,
      CLIENT_SECRET,
      "https://www.googleapis.com/auth/calendar")
    flow.redirect_uri = request.base_url
    try:
      credentials = flow.step2_exchange(code)
    except Exception as e:
      print "Unable to get an access token because ", e.message

  current_user.google_key = credentials.to_json()
  print 'google key set to ' + current_user.google_key
  current_user.save()
  #save

  return redirect(url_for('home'))
