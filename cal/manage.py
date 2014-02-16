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
    print 'dropping all'
    db.drop_all()
    print 'creating all'
    db.create_all()
    print 'done'

if __name__ == '__main__':
  manager.run()