from flask import render_template, redirect, jsonify
from flask.ext.login import login_required, logout_user, current_user

from cal import app


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