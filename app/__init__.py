from config import Config
from app.database import db
from flask import Flask
from app.blueprints import user_routes, post_routes, static_routes
from flask_bootstrap import Bootstrap5
from app.models import User
from app.database import db
from flask_gravatar import Gravatar
from flask_login import LoginManager
from flask_ckeditor import CKEditor
from app.utilities import setup_logger


def create_app(config_class=Config):
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(config_class)
    Bootstrap5(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()

    ckeditor = CKEditor(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    gravatar = Gravatar(app,
                        size=100,  # Adjusted size
                        rating='g',
                        default='retro',
                        force_default=False,
                        force_lower=False,
                        use_ssl=False,
                        base_url=None)

    app.register_blueprint(user_routes)
    app.register_blueprint(post_routes)
    app.register_blueprint(static_routes)
    setup_logger()

    return app
