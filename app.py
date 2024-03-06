import os

from flask import Flask, request, redirect, render_template, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Note
from forms import RegisterUserForm, LoginForm, \
    CSRFProtectForm, NewNoteForm, UpdateNoteForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", 'postgresql:///flask_notes')
app.config['SECRET_KEY'] = "oh-so-secret"

AUTH_KEY = "username"

# app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

toolbar = DebugToolbarExtension(app)


@app.get('/')
def redirect_root_to_register():
    """ Root route to register """
    return redirect('/register')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """ Register/Create User or Renders registration form """

    form = RegisterUserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        if User.query.filter_by(username=username).one_or_none():
            form.username.errors = ["Username already exists"]
            return render_template("register_form.html", form=form)
        if User.query.filter_by(email=email).one_or_none():
            form.email.errors = ["Email already exists"]
            return render_template("register_form.html", form=form)

        new_user = User.register(
            username, password, email, first_name, last_name)

        db.session.add(new_user)
        db.session.commit()

        session[AUTH_KEY] = new_user.username

        return redirect(f"users/{new_user.username}")

    else:
        return render_template("register_form.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """ Login page to process form or render page """

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session[AUTH_KEY] = user.username
            return redirect(f"users/{user.username}")
        else:
            form.username.errors = ["Invalid Username or Password"]

    return render_template("login_form.html", form=form)


@app.get("/users/<username>")
def render_user_page(username):
    """Render secure page for user information"""

    form = CSRFProtectForm()

    if AUTH_KEY not in session or username != session[AUTH_KEY]:
        flash("You are not authorized!")
        return redirect("/")

    user = User.query.get_or_404(username)
    notes = user.notes

    return render_template("user.html", user=user, notes=notes, form=form)


@app.post("/logout")
def logout():
    """Logs user out and redirects to homepage."""

    form = CSRFProtectForm()

    if form.validate_on_submit():
        session.pop(AUTH_KEY, None)

    return redirect("/")


@app.post('/users/<username>/delete')
def delete_user(username):
    """ Delete user """
    form = CSRFProtectForm()

    if AUTH_KEY not in session or username != session[AUTH_KEY]:
        flash("You are not authorized!")
        return redirect("/")

    if form.validate_on_submit():
        user = User.query.get_or_404(username)

        Note.query.filter_by(owner_username=username).delete()

        db.session.delete(user)
        db.session.commit()
        session.pop(AUTH_KEY, None)

    return redirect("/")


@app.route('/users/<username>/notes/add', methods=['GET', 'POST'])
def update_note(username):
    """ Render form to add note or submit form data """
    user = User.query.get_or_404(username)

    form = NewNoteForm()

    if AUTH_KEY not in session or username != session[AUTH_KEY]:
        flash("You are not authorized!")
        return redirect("/")

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        new_note = Note(
            title=title,
            content=content,
            owner_username=username)

        db.session.add(new_note)
        db.session.commit()

        return redirect(f'/users/{username}')
    else:
        return render_template("add_note.html", form=form, user=user)


@app.route('/notes/<int:id>/update', methods=['GET', 'POST'])
def add_note(id):
    """ Render form to add note or submit form data """
    current_note = Note.query.get_or_404(id)
    current_user = current_note.user

    form = UpdateNoteForm(obj=current_note)

    if AUTH_KEY not in session or current_user.username != session[AUTH_KEY]:
        flash("You are not authorized!")
        return redirect("/")

    if form.validate_on_submit():
        current_note.title = form.title.data
        current_note.content = form.content.data

        db.session.commit()

        return redirect(f'/users/{current_user.username}')
    else:
        return render_template(
            "update_note.html",
            form=form,
            user=current_user)


@app.post("/notes/<int:id>/delete")
def delete_note(id):
    """ Delete a note from db and redirect to the userpage"""
    current_note = Note.query.get_or_404(id)
    current_user = current_note.user

    if AUTH_KEY not in session or current_user.username != session[AUTH_KEY]:
        flash("You are not authorized!")
        return redirect("/")

    db.session.delete(current_note)
    db.session.commit()

    return redirect(f'/users/{current_user.username}')