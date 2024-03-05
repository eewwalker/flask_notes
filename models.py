from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database."""

    app.app_context().push()
    db.app = app
    db.init_app(app)


class User(db.Model):
    """ Blueprint for making User instances """
    __tablename__ = "users"

    username = db.Column(
        db.String(20),
        primary_key = True
    )
    hashed_password = db.Column(
        db.String(100),
        nullable = False
    )
    email = db.Column(
        db.String(50),
        nullable = False,
        unique = True
    )
    first_name = db.Column(
        db.String(30),
        nullable = False
    )
    last_name = db.Column(
        db.String(30),
        nullable = False
    )
    @classmethod
    def register(cls, username, password):
        hashed = bcrypt.generate_password_hash(password).decode('utf8')

        return cls(username=username, password=hashed)

    @classmethod
    def authenticate(cls, username, password):
        u = cls.query.filter_by(username=username).one_or_none()

        if u and bcrypt.check_password_hash(u.password, password):
            return u
        else:
            return False
