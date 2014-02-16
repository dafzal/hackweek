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
import datetime
from cal.models import User,Event

@app.route('/')
def main():
  return render_template('home.html')

@login_required
@app.route('/done/')
def done():
  return render_template('done.html')

@login_required
@app.route('/friends')
def friends():
  return jsonify(**current_user.get_friends()['data'])

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
    'created_events': created_events.to_json(),
    'invited_events': invited_events.to_json()
  }
  return jsonify(results)

@app.route('/google_connect')
def google_connect():
  print 'current key ' + str(current_user.google_key)
  if not current_user.google_key:
    return redirect(url_for('login'))
  credentials = OAuth2Credentials.from_json(current_user.google_key)

  if credentials is None or credentials.invalid == True:
    return redirect(url_for('login'))

  
  http = httplib2.Http()
  http = credentials.authorize(http)
  service = build("calendar", "v3", http=http)
  calendar_list = service.calendarList().list().execute()

  print calendar_list
  return redirect('/')

@app.route('/test')
def test():
  if not current_user.google_key:
    return redirect(url_for('login'))
  credentials = OAuth2Credentials.from_json(current_user.google_key)

  if credentials is None or credentials.invalid == True:
      return redirect(url_for('login'))

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

@app.route('/login')
def login():
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
  db.session.flush()
  import ipdb
  ipdb.set_trace()
  #save

  return redirect(url_for('done'))
