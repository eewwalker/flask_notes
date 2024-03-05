import os

from flask import Flask, request, redirect, render_template, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User
from forms import RegisterUserForm, LoginForm, CSRFProtectForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", 'postgresql:///flask_notes')
app.config['SECRET_KEY'] = "oh-so-secret"



# app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

toolbar = DebugToolbarExtension(app)


@app.get('/')
def redirect_root_to_register():
    """ Root route to register """
    return redirect('/register')


@app.route('/register', methods = ['GET', 'POST'])
def register():
    """ Register/Create User or Renders registration form """

    form = RegisterUserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        if User.query.filter_by(username = username).one_or_none():
            form.username.errors = ["Username already exists"]
            return render_template("register_form.html", form=form)
        if User.query.filter_by(email = email).one_or_none():
            form.email.errors = ["Email already exists"]
            return render_template("register_form.html", form=form)


        new_user = User.register(username, password, email, first_name, last_name)

        db.session.add(new_user)
        db.session.commit()

        session["username"] = new_user.username

        return redirect(f"users/{new_user.username}")

    else:
        return render_template("register_form.html", form=form)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    """ Login page to process form or render page """

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session["username"] = user.username
            return redirect(f"users/{user.username}")
        else:
            form.username.errors = ["Invalid Username or Password"]

    return render_template("login_form.html", form=form)



@app.get("/users/<username>")
def render_user_page(username):
    """Render secure page for user information"""

    form = CSRFProtectForm()

    if "username" not in session or username != session["username"]:
        flash("You are not authorized!")
        return redirect("/")

    user = User.query.get_or_404(username)


    return render_template("user.html", user=user, form=form)


@app.post("/logout")
def logout():
    """Logs user out and redirects to homepage."""

    form = CSRFProtectForm()

    if form.validate_on_submit():
        session.pop("username", None)

    return redirect("/")