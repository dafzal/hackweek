import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from cal import app
from cal import db
from flask.ext.script import Manager, Server

manager = Manager(app)

manager.add_command('runserver', Server(
  use_debugger = True,
  use_reloader = True))

@manager.command
def syncdb():
    from cal.models import User
    from social.apps.flask_app import models
    db.drop_all()
    db.create_all()

if __name__ == '__main__':
  app.config['DEBUG'] = True
  app.debug = True
  manager.run()