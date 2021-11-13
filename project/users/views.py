from flask import render_template, redirect, url_for, flash, session, request, Blueprint
from sqlalchemy.exc import IntegrityError

from project.models import User
from project.users.forms import LoginForm, RegisterForm
from project import db

users_blueprint = Blueprint('users', __name__)


@users_blueprint.route('/register/', methods=['GET', 'POST'], endpoint='register')
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
                return redirect(url_for('.login'))
            except IntegrityError:
                error = 'That username and/or email already exist.'
                return render_template('register.html', form=form, error=error)
    return render_template('register.html', form=form, error=error)


@users_blueprint.route('/logout/', methods=['GET'], endpoint='logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_role', None)
    flash('Goodbye!')
    return redirect(url_for('.login'))


@users_blueprint.route('/', methods=['GET', 'POST'], endpoint='login')
def login():
    form = LoginForm(request.form)
    error = None
    if request.method == 'POST':
        if form.validate():
            user = User.query.filter_by(name=form.name.data).first()
            if user and user.password == form.password.data:
                session['logged_in'] = True
                session['user_id'] = user.id
                session['user_name'] = user.name
                session['user_role'] = user.role
                flash('Welcome')
                return redirect(url_for('tasks.tasks'))
            else:
                error = 'Invalid username or password.'
    return render_template('login.html', form=form, error=error)
