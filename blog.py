# blog.py controller
from flask import Flask, render_template, request, session, flash, redirect, url_for, g
from functools import wraps

import sqlite3

# Configurations
DATABASE = 'blog.db'
USERNAME = 'admin'
PASSWORD = 'admin'
SECRET_KEY = 'hard_to_guess'


app = Flask(__name__)

app.config.from_object(__name__)


def login_required(test):
    @wraps(login)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash("You are not authorized access this page")
            return redirect(url_for('login'))
    return wrap


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


@app.route('/', methods=['GET', 'POST'], endpoint='login')
def login():
    error = None
    status_code = 200
    if request.method=='POST':
        if request.form['username'] != app.config['USERNAME'] or request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid credentials. Please try again.'
            status_code = 401
        else:
            session['logged_in'] = True
            return redirect('main')
    return render_template('login.html'), status_code


@app.route('/logout', methods=['GET'], endpoint='logout')
def logout():
    session.pop('logged_in', None)
    flash('Logged out')
    return redirect(url_for('login'))


@app.route('/main', endpoint='main')
@login_required
def main():
    g.db = connect_db()
    cur = g.db.execute('SELECT * from posts')
    posts = [dict(title=row[0], post=row[1]) for row in cur.fetchall()]
    g.db.close()
    return render_template('main.html', posts=posts)


@app.route('/add', methods=['POST'], endpoint='add')
@login_required
def add():
    title = request.form['title']
    post = request.form['post']
    if not title or not post:
        flash("All fields are required. Please try again")
        return redirect(url_for('main'))
    else:
        g.db = connect_db()
        g.db.execute('INSERT INTO posts (title, post) values (?,?)', [request.form['title'], request.form['post']])
        g.db.commit()
        g.db.close()
        flash('New post successfully added')
        return redirect(url_for('main'))


if __name__ == '__main__':
    app.run(debug=True)
