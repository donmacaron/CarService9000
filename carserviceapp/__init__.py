import platform
from os import path
from flask import Flask
from flask_login import LoginManager, login_manager
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
DB_NAME = 'database.db'
PLATOFRM = platform.system()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'DucksAreEatenBy'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    db.init_app(app)
    
    from .views import views
    from .auth import auth
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    from .models import User, Client, Service, Part, Master, Repair
    # , clients_services, masters_services, repairs_services, masters_repairs
  
    create_db(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Войдите в свой аккаунт, чтобы просматривать страницу"
    login_manager.login_message_category = "warning"
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
        
    return app

def create_db(app):
    if not path.exists('carserviceapp/' + DB_NAME):
        db.create_all(app=app)
        print('\n##### DB WAS CREATED #####\n')