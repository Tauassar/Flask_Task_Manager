# views.py controller
import sqlite3

from flask import Flask, render_template, request, session, flash, redirect, url_for, g
from functools import wraps

from forms import AddTaskForm

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


@app.route('/logout/', methods=['GET'], endpoint='logout')
def logout():
    session.pop('logged_in', None)
    flash('Logged out')
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'], endpoint='login')
def login():
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME'] or \
                request.form['password'] != app.config['PASSWORD']:
            error = 'INVALID CREDENTIALS. PLEASE TRY AGAIN'
            return render_template('login.html', error=error)
        else:
            session['logged_in'] = True
            flash('Welcome')
            return redirect(url_for('tasks'))
    return render_template('login.html')


@app.route('/tasks/', methods=['GET'], endpoint='tasks')
@login_required
def tasks():
    g.db = connect_db()
    cursor = g.db.execute('SELECT name, due_date, priority, task_id from tasks where status=1')
    open_tasks = [
        dict(
            name=row[0],
            due_date=row[1],
            priority=row[2],
            task_id=row[3]
        ) for row in cursor.fetchall()
    ]
    cursor = g.db.execute('SELECT name, due_date, priority, task_id from tasks where status=0')
    closed_tasks = [
        dict(
            name=row[0],
            due_date=row[1],
            priority=row[2],
            task_id=row[3]
        ) for row in cursor.fetchall()
    ]
    g.db.close()
    return render_template(
        'tasks.html',
        form=AddTaskForm(request.form),
        closed_tasks=closed_tasks,
        open_tasks=open_tasks
    )


@app.route('/add/', methods=["POST"], endpoint='new_task')
@login_required
def new_task():
    g.db = connect_db()
    name = request.form['name']
    date = request.form['due_date']
    priority = request.form['priority']

    if not (priority or date or name):
        flash("All fields are required. Please try again.")
        return redirect(url_for('tasks'))
    else:
        g.db.execute('INSERT INTO tasks (name, due_date, priority, status) VALUES (?,?,?,1)', [
            name, date, priority
        ])
        g.db.commit()
        g.db.close()
        flash('New entry was successfully posted. Thanks.')
        return redirect(url_for('tasks'))


@app.route('/complete/<int:task_id>/', endpoint='complete')
@login_required
def complete(task_id):
    g.db = connect_db()
    g.db.execute('UPDATE tasks SET status=0 WHERE task_id=' + str(task_id))
    g.db.commit()
    g.db.close()
    flash('The task was marked as complete')
    return redirect(url_for('tasks'))


@app.route('/delete/<int:task_id>/')
@login_required
def delete_entry(task_id):
    g.db = connect_db()
    g.db.execute('DELETE FROM tasks where task_id=' + str(task_id))
    g.db.commit()
    g.db.close()
    flash('The task was deleted.')
    return redirect(url_for('tasks'))
