import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from cal import app
from flask.ext.script import Manager, Server

from gcal import Gcal

manager = Manager(app)

manager.add_command('runserver', Server(
  use_debugger = True,
  use_reloader = True))

@app.route('/gcal/connect/')
def gcal_connect:
  gcal = Gcal()


if __name__ == '__main__':
  app.config['DEBUG'] = True
  app.debug = True
  manager.run()