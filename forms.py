from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Length, Email


class RegisterUserForm(FlaskForm):
    """Form for registering users"""

    username = StringField(
        "Username",
        validators=[InputRequired(), Length(max=20)])

    password = PasswordField("Password",
                             validators=[InputRequired(), Length(max=100)])

    email = StringField("Email",
                       validators=[InputRequired(), Length(max=50), Email()])

    first_name = StringField("First Name",
                             validators=[InputRequired(), Length(max=30)])

    last_name = StringField("Last Name",
                            validators=[InputRequired(), Length(max=30)])


class LoginForm(FlaskForm):
    """ Form for user login """
    username = StringField("Username",
                           validators=[InputRequired()])

    password = PasswordField("Password",
                             validators=[InputRequired()])

class NewNoteForm(FlaskForm):
    """ Form to add new note """

    title = StringField(
        "Note Title",
        validators=[InputRequired(), Length(max=100)]
    )
    content = TextAreaField(
        "Note Content",
        validators=[InputRequired()]

    )


class UpdateNoteForm(NewNoteForm):
    """ Form to add new note """



class CSRFProtectForm(FlaskForm):
    """Form just for CSRF Protection"""
