import httplib2
import gflags

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

LOCALHOST_KEY = 'AIzaSyDj78--VaFyDvfommSibE9dv6Pr8HxRr00'

app = Flask(__name__)



