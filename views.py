# views.py controller
import datetime

from flask import Flask, render_template, request, session, flash, redirect, url_for
from functools import wraps

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from forms import AddTaskForm, LoginForm, RegisterForm

# configurations
app = Flask(__name__)
app.config.from_object('_config')
db = SQLAlchemy(app)

from models import Task, User


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

@app.route('/register/', methods=['GET', 'POST'], endpoint='register')
def register():
    error = None
    form = RegisterForm(request.form)
    if request.method == 'POST':
        if form.validate():
            new_user = User(
                name=form.name.data,
                email=form.email.data,
                password=form.password.data
            )
            try:
                db.session.add(new_user)
                db.session.commit()
                flash('Thanks for registering. Please login')
                return redirect(url_for('login'))
            except IntegrityError:
                error = 'That username and/or email already exist.'
                return render_template('register.html', form=form, error=error)
    return render_template('register.html', form=form, error=error)


@app.route('/logout/', methods=['GET'], endpoint='logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    flash('Logged out')
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'], endpoint='login')
def login():
    form = LoginForm(request.form)
    error = None
    if request.method == 'POST':
        if form.validate():
            user = User.query.filter_by(email=form.name.data).first()
            if user and user.password == form.password.data:
                session['logged_in'] = True
                session['user_id'] = user.id
                flash('Welcome')
                return redirect(url_for('tasks'))
            else:
                error = 'Invalid username or password.'
        else:
            error = 'Both fields are required.'
    return render_template('login.html', form=form, error=error)


def open_tasks():
    return db.session.query(Task).filter_by(
        status='1').order_by(Task.due_date.asc())


def closed_tasks():
    return db.session.query(Task).filter_by(
        status='0').order_by(Task.due_date.asc())


@app.route('/tasks/', methods=['GET'], endpoint='tasks')
@login_required
def tasks():
    return render_template(
        'tasks.html',
        form=AddTaskForm(request.form),
        closed_tasks=closed_tasks(),
        open_tasks=open_tasks()
    )


@app.route('/add/', methods=['GET', 'POST'], endpoint='new_task')
@login_required
def new_task():
    error = None
    form = AddTaskForm(request.form)
    if request.method == 'POST':
        if form.validate():
            task_to_add = Task(
                name=form.name.data,
                due_date=form.due_date.data,
                priority=form.priority.data,
                status='1',
                user_id=session['user_id'],
                posted_date=datetime.date.today(),
            )
            db.session.add(task_to_add)
            db.session.commit()
            flash('New entry was successfully posted. Thanks.')
            return redirect(url_for('tasks'))
    return render_template(
        'tasks.html',
        form=form,
        error=error,
        open_tasks=open_tasks(),
        closed_tasks=closed_tasks()
    )


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


def flash_error(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text, error),
                  'error'
            )
