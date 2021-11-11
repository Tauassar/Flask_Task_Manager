# views.py controller
import datetime

from flask import Flask, render_template, request, session, flash, redirect, url_for
from functools import wraps

from flask_sqlalchemy import SQLAlchemy

from forms import AddTaskForm

# configurations
app = Flask(__name__)
app.config.from_object('_config')
db = SQLAlchemy(app)

from models import Task


# Helpers

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
    open_tasks = db.session.query(Task). \
        filter_by(status='1').order_by(Task.due_date.asc())
    closed_tasks = db.session.query(Task). \
        filter_by(status='0').order_by(Task.due_date.desc())
    return render_template(
        'tasks.html',
        form=AddTaskForm(request.form),
        closed_tasks=closed_tasks,
        open_tasks=open_tasks
    )


@app.route('/add/', methods=['GET', 'POST'], endpoint='new_task')
@login_required
def new_task():
    form = AddTaskForm(request.form)
    if request.method == 'POST':
        if form.validate() or True:
            print(form.due_date)
            new_task = Task(
                form.name.data,
                form.due_date.data,
                form.priority.data,
                '1',
            )
            db.session.add(new_task)
            db.session.commit()
            flash('New entry was successfully posted. Thanks.')
            return redirect(url_for('tasks'))
        else:
            flash('All fields are required.')
            return redirect(url_for('tasks'))
    return render_template('tasks.html', form=form)


@app.route('/complete/<int:task_id>/', endpoint='complete')
@login_required
def complete(task_id):
    db.session.query(Task).filter_by(task_id=task_id).update({'status': '0'})
    db.session.commit()
    flash('The task was marked as complete')
    return redirect(url_for('tasks'))


@app.route('/delete/<int:task_id>/')
@login_required
def delete_entry(task_id):
    db.session.query(Task).filter_by(task_id=task_id).delete()
    db.session.commit()
    flash('The task was deleted.')
    return redirect(url_for('tasks'))
