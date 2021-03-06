from flask import render_template, redirect, jsonify, json
from flask.ext.login import login_required, logout_user, current_user
from flask import render_template, redirect, session, url_for, request
from flask.ext.login import login_required, logout_user, login_user

from cal import app
from cal import db
from oauth2client.client import OAuth2WebServerFlow
from apiclient.discovery import build_from_document, build
from oauth2client.file import Storage
from oauth2client.client import OAuth2Credentials
import httplib2
import datetime, time
from cal import social
from dateutil import parser
import json
from evernote.edam.type.ttypes import *
from evernote.api.client import *
from evernote.edam.notestore.ttypes import *
from cal.models import User,Event, Response

@app.route('/')
def main():
  if current_user.is_authenticated():
    events = get_events(user=current_user, finalized_only=True)
    results = []
    for e in events:
      entry = {'title': str(e.name), 'start': str(e.suggested_from_time), 'allDay': False}
      if entry not in results:
        results.append({'title': str(e.name), 'start': str(e.suggested_from_time), 'allDay': False})
    return render_template('dashboard.html', user_name=current_user.name,
      events=json.dumps(results))
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
  finalized_only = False
  user = User.objects.get(id=user_id)
  created_events = Event.objects(creator=user.id)
  invited_events = Event.objects(invitees=user.id)

  results = {
    'created_events': [x.to_json() for x in created_events],
    'invited_events': [x.to_json() for x in invited_events],
  }
  return jsonify(results)

@app.route('/events')
def current_events():
  user = current_user
  created_events = Event.objects(creator=user.id)
  invited_events = Event.objects(invitees=user.id)

  results = {
    'created_events': [x.to_json() for x in created_events],
    'invited_events': [x.to_json() for x in invited_events],
  }
  return jsonify(results)

@app.route('/overview')
def overview():
  events = get_events(user=current_user)
  events['created_events'] = reversed(events['created_events'])
  events['invited_events'] = reversed(events['invited_events'])
  return render_template('list_events.html', events=events,
    user_name=current_user.name)


def get_events(user, finalized_only=False):
  created_events = Event.objects(creator=user.id)
  invited_events = Event.objects(invitees=user.id)
  if finalized_only:
    finalized_events = []
    for event in created_events:
      if event.status == 'Finalized':
        finalized_events.append(event)
    for event in invited_events:
      if event.status == 'Finalized':
        finalized_events.append(event)
    return finalized_events

  results = {
    'created_events': [x.to_json() for x in created_events],
    'invited_events': [x.to_json() for x in invited_events],
  }
  for event in results['invited_events']:
    response = Response.objects(event=Event.objects().get(id=event['id']), responder=user.id)
    if response is not None and len(response) > 0:
      if response[0].response:
        event['res'] = 'Yes'
      else:
        event['res'] = 'No'
    else:
      event['res'] = 'notfound'
  return results

@app.route('/events')
def all_events():
  u = current_user
  created_events = Event.objects(creator=u.id)
  invited_events = Event.objects(invitees=u.id)
  results = {
    'created_events': [x.to_json() for x in created_events],
    'invited_events': [x.to_json() for x in invited_events],
  }
  return results

@app.route('/users')
def users():
  return jsonify(data=[x.to_json() for x in User.objects.all()])

@app.route('/usernames')
def usernames():
  dic_array = []
  for x in User.objects:
    dic_array.append({'name':x.name})
  return json.dumps(dic_array)

@app.route('/events/add',  methods=['GET', 'POST'])
def add_event():
  data = request.values
  invitees = []
  for i in data.getlist('invitees') or data.getlist('invitees[]'):
    invitees += [x.strip() for x in i.split(',')]

  invitees = list(set(invitees))
  print str(data)
  days = data.get('days','mtw')

  from_time_range = parser.parse(data['from_time_range'])
  to_time_range = parser.parse(data['to_time_range'])
  if current_user.is_authenticated():
    creator = current_user
  else:
    creator = User.objects.get(id=data['cookie'])
  event = Event(name=data['name'],from_time_range=from_time_range,
    to_time_range=to_time_range,location=data['location'],duration_minutes=data['duration'],
    creator=creator.id,threshold=data['threshold'], days=''.join(days))
  for invitee_name in invitees:
    if not invitee_name.strip():
      continue
    u = User.objects.get(name__icontains=invitee_name.strip())
    event.invitees.append(u)
  
  #event.suggested_from_time = event.from_time_range
  event.suggested_from_time = datetime.datetime(month=2, day=20, year=2014, hour=11)
  #evernote stuff
  store = EvernoteClient(token='S=s1:U=8df7b:E=14b91fcbdb9:C=1443a4b91bb:P=1cd:A=en-devtoken:V=2:H=58cee1b9b995670db8f66230ec99b5e1').get_note_store()
  note = Note()
  note.title = 'Event ' + str(request.values.get('name'))
  note.content = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
  content = 'Selected date: ' + event.suggested_from_time.strftime('%A %B %d at %I:%M %p') + '<br/>'
  for i in invitees:
    content += i +  ' - Waiting for response' + '<br />'
  note.content += '<en-note>%s</en-note>' % content
  createdNote = store.createNote(note)
  event.note_guid = createdNote.guid
  print 'note guid is ' + createdNote.guid
  event.save()
  event.send_invites()
  return 'OK'

@login_required
@app.route('/events/respond_web', methods=['POST'])
def res():
  data = request.values
  event_id = data['event_id']
  user_id = current_user.id
  response = data['response']
  r = Response(response=response, event=event_id, responder=user_id)
  r.save()
  return 'OK'


@app.route('/events/respond/<event_id>')
def respond(event_id):
  print 'hi'
  data = request.values
  data = request.values
  user_response = data.get('user_response',True)
  if user_response == 'True' or user_response == 'true' or user_response == True:
    user_response = True
  else:
    user_response = False
  event = Event.objects.get(id=event_id)
  
  token = 'S=s1:U=8df7b:E=14b91fcbdb9:C=1443a4b91bb:P=1cd:A=en-devtoken:V=2:H=58cee1b9b995670db8f66230ec99b5e1'
  store = EvernoteClient(token=token).get_note_store()
  note = store.getNote(token, event.note_guid, True, True, True, True)

  if data.get('cookie',''):
    responder = User.objects.get(id=data['cookie'])
  else:
    responder = current_user
  try:
    r = Response.objects.get(db.Q(event=event.id) & db.Q(responder=responder.id))
  except:
    r = Response(response=user_response, event=event.id, responder=responder.id)
  r.response = user_response
  r.save()
  num_response = Response.objects(event=event).count()
  if num_response >= int(event.threshold):
    event.status = 'Finalized'
    event.final_from_field = event.suggested_from_time
    event.save()
    notify_users(event)

  note.content = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'

  content = 'Selected date: ' + event.suggested_from_time.strftime('%A %B %d at %I:%M %p') + '<br/>'

  for i in event.invitees:
    try:
      r = Response.objects.get(db.Q(event=event.id) & db.Q(responder=i.id))
      content += i.name +  ' - Responded ' + str(r.response) + '<br />'
    except Exception as e:
      print str(e)
      content += i.name +  ' - Still waiting for response' + '<br />'
  note.content += '<en-note>%s</en-note>' % content
  store.updateNote(note)
  return redirect(url_for('main'))

@app.route('/force_login/<user>')
def force_login(user):
  u = User.objects.get(name__icontains=user)
  login_user(u)
  return redirect(url_for('main'))

@app.route('/events/create')
def create_event():
  return render_template('event_creation.html',user_name=current_user.name,user_list=User.objects.all())

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

import requests

def mail(to, subject):
  url = 'https://api.sendgrid.com/api/mail.send.json'
  data = {'api_user':'iotasquared', 'api_key': 'Calhack1', 'to[]':to, 'subject':subject}
  r = requests.post(url, data=json.dumps(data), headers = {'Content-type': 'application/json', 'Accept': 'text/plain'})
  print r.json()
