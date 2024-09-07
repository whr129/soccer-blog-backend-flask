from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase
from flask_cors import CORS
from flask_session import Session
from dotenv import load_dotenv
import redis
import os

class Base(DeclarativeBase):
  pass

load_dotenv()

db = SQLAlchemy(model_class=Base)

def create_app():
    app = Flask(__name__)

    CORS(app, supports_credentials=True)
    # Details on the Secret Key: https://flask.palletsprojects.com/en/3.0.x/config/#SECRET_KEY
    # NOTE: The secret key is used to cryptographically-sign the cookies used for storing
    #       the session identifier.
    app.secret_key = os.getenv('SECRET_KEY', default='BAD_SECRET_KEY')

    # Configure Redis for storing the session data on the server-side
    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_PERMANENT'] = True
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_REDIS'] = redis.from_url('redis://127.0.0.1:6379')

    # Create and initialize the Flask-Session object AFTER `app` has been configured
    server_session = Session(app)

    password = os.getenv('PASSWORD')
    host_name = 'localhost'
    port = '5432'
    database = 'soccerBlog'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://postgres:{password}@{host_name}:{port}/{database}"

    db.init_app(app)

    #import and register all blueprints
    from soccer_app.user.routes import user
    app.register_blueprint(user, url_prefix='/user')
    from soccer_app.group.routes import group
    app.register_blueprint(group, url_prefix='/group')
    from soccer_app.comment.routes import comment
    app.register_blueprint(comment, url_prefix='/comment')

    migrate = Migrate(app, db)

    return app