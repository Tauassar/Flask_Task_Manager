from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired, Length, EqualTo, Email


class RegisterForm(Form):
    name = StringField(
        'Username',
        validators=[DataRequired(), Length(min=6, max=40)]
    )
    email = StringField(
        'Email',
        validators=[DataRequired(), Email(), Length(min=6, max=40)]
    )
    password = StringField(
        'Password',
        validators=[DataRequired(), Length(min=6, max=40)]
    )
    confirm_password = StringField(
        'Confirm password',
        validators=[
            DataRequired(),
            Length(min=6, max=40),
            EqualTo(
                'password',
                message='Passwords must match'
            )
        ]
    )


class LoginForm(Form):
    name = StringField(
        'Username',
        validators=[DataRequired()]
    )
    password = StringField(
        'Password',
        validators=[DataRequired()]
    )
