from flask import render_template, redirect
from flask.ext.login import login_required, logout_user

from cal import app
from gcal import Gcal


@app.route('/')
def main():
    return render_template('home.html')


@login_required
@app.route('/done/')
def done():
    return render_template('done.html')


@app.route('/logout')
def logout():
    """Logout view"""
    logout_user()
    return redirect('/')

@app.route('/gcal/connect')
def gcal_connect():
  gcal = Gcal()
  gcal.get_list()