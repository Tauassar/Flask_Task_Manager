from datetime import datetime
from functools import wraps

from flask import Blueprint, flash, session, redirect, url_for, render_template, request
from project.models import Task
from project.tasks.forms import AddTaskForm
from project import db

tasks_blueprint = Blueprint('tasks', __name__)


# Helpers

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash("You are not authorized to view this page")
            return redirect(url_for('users.login'))

    return wrap


def open_tasks():
    return db.session.query(Task).filter_by(
        status='1').order_by(Task.due_date.asc())


def closed_tasks():
    return db.session.query(Task).filter_by(
        status='0').order_by(Task.due_date.asc())


# Views


@tasks_blueprint.route('/tasks/', methods=['GET'], endpoint='tasks')
@login_required
def tasks():
    return render_template(
        'tasks.html',
        form=AddTaskForm(request.form),
        closed_tasks=closed_tasks(),
        open_tasks=open_tasks()
    )


@tasks_blueprint.route('/add/', methods=['GET', 'POST'], endpoint='new_task')
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
                posted_date=datetime.today(),
            )
            db.session.add(task_to_add)
            db.session.commit()
            flash('New entry was successfully posted. Thanks.')
            return redirect(url_for('.tasks'))
    return render_template(
        'tasks.html',
        form=form,
        error=error,
        open_tasks=open_tasks(),
        closed_tasks=closed_tasks()
    )


@tasks_blueprint.route('/complete/<int:task_id>/', endpoint='complete')
@login_required
def complete(task_id):
    task = db.session.query(Task).filter_by(task_id=task_id)
    if session['user_id'] == task.first().user_id or session['user_role'] == 'admin':
        task.update({'status': '0'})
        db.session.commit()
        flash('The task was marked as complete')
    else:
        flash('You can only update tasks that belong to you.')
    return redirect(url_for('.tasks'))


@tasks_blueprint.route('/delete/<int:task_id>/')
@login_required
def delete_entry(task_id):
    task = db.session.query(Task).filter_by(task_id=task_id)
    if session['user_id'] == task.first().user_id or session['user_role'] == 'admin':
        task.delete()
        db.session.commit()
        flash('The task was deleted.')
    else:
        flash('You can only delete tasks that belong to you.')
    return redirect(url_for('.tasks'))


def flash_error(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text, error),
                  'error'
                  )
