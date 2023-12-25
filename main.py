from flask import Flask
from app.blueprints import user_routes, post_routes, static_routes
from flask_bootstrap import Bootstrap5
from functools import wraps
from flask import abort
from app.models import User
from app.database import db
from flask_gravatar import Gravatar
from flask_login import LoginManager, current_user
from flask_ckeditor import CKEditor

import dotenv
import os

dotenv.load_dotenv()

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = os.getenv("APP_SECRET_KEY")
Bootstrap5(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URL")
db.init_app(app)

with app.app_context():
    db.create_all()

# CKEditor
ckeditor = CKEditor()
ckeditor.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

gravatar = Gravatar(app,
                    size=10,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


app.register_blueprint(user_routes)
app.register_blueprint(post_routes)
app.register_blueprint(static_routes)

if __name__ == "__main__":
    app.run(debug=True, port=5003)
