import httplib2
import gflags

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

FLAGS = gflags.FLAGS

FLOW = OAuth2WebServerFlow(
  client_id='610521713571.apps.googleusercontent.com',
  client_secret='FJgybwIs_wU8eautMC41PRE0',
  scope='https://www.googleapis.com/auth/calendar',
  user_agent='mutualCalendar/v1')

LOCALHOST_KEY = 'AIzaSyDj78--VaFyDvfommSibE9dv6Pr8HxRr00'

class Gcal:

  def get_list(self):
    storage = Storage('calendar.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid == True:
      credentials = run(FLOW, storage)
      return redirect('/')

    http = httplib2.Http()
    http = credentials.authorize(http)

    service = build(serviceName='calendar', version='v3', http=http,
           developerKey=LOCALHOST_KEY)

    calendar_list = service.calendarList().list().execute()

    print calendar_list
