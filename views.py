# views.py controller
from flask import Flask, render_template, request, session, flash, redirect, url_for, g
from functools import wraps

import sqlite3

# configurations
app = Flask(__name__)
app.config.from_object('_config')


# Helpers
def connect_db():
    return sqlite3.connect(app.config['DATABASE_PATH'])


def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash("You are not authorized to view this page")
            return redirect(url_for('main'))

    return wrap


# Route handlers


@app.route('/logout/', endpoint='logout')
def logout():
    session.pop('logged_in', None)
    flash('Logged out')
    return redirect(url_for('login'))


@app.route('/', endpoint='login')
def login():
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME'] or \
                request.form['password'] != app.config['PASSWORD']:
            error = 'INVALID CREDENTIALS. PLEASE TRY AGAIN'
            return render_template('login.html', error=error)
        else:
            session['logged_in'] = True
            flash('Welcome')
            return redirect(url_for('main'))
    return render_template('login.html')
