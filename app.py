import os

from flask import Flask, request, redirect, render_templates, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, Pet

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", 'postgresql:///flask_notes')
debug = DebugToolbarExtension(app)

app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = "oh-so-secret"

connect_db(app)


@app.get('/')
def redirect_root_to_register():
    """ Root route to register """
    return redirect('/register')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    """ Register/Create User or Renders registration form """