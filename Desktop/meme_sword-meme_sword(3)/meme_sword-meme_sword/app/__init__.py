from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
app=Flask(__name__)
app.config["SECRET_KEY"]=os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"]=os.environ.get("SQLALCHEMY_DATABASE_URI")
app.config["UPLOAD_EXTENSIONS"] = [".jpg", ".jpeg", ".png", ".gif",".mp4"]
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "imgs")
app.config["FLASK_DEBUG"]=os.environ.get("FLASK_DEBUG")
app.config['MAIL_SERVER'] = os.environ.get("MAIL_SERVER")# Gmail SMTP server
app.config['MAIL_PORT'] = os.environ.get("MAIL_PORT")
app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
db=SQLAlchemy(app)
app.app_context().push()
migrate=Migrate(app,db)
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view="users.login"
mail=Mail(app)

from app.users.routes import users
from app.posts.routes import posts
from app.main.routes import main
app.register_blueprint(users)
app.register_blueprint(posts)
app.register_blueprint(main)