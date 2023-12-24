from flask import Blueprint, render_template, redirect, url_for, abort, flash
from app.forms import LoginUserForm, RegisterUserForm
from functools import wraps
from app.models import User, db
from flask_login import login_user, current_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

# Blueprint definition
user_routes = Blueprint('user_routes', __name__)


@user_routes.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginUserForm()

    if login_form.validate_on_submit():

        user = db.session.execute(db.select(User).where(User.email == login_form.email.data)).scalar()
        password = login_form.password.data
        if not user:
            flash("User does not exist")
            return redirect(url_for("user_routes.login"))

        elif not check_password_hash(user.password, password):
            flash("email or password is wrong")
            return redirect(url_for("user_routes.login"))
        else:
            login_user(user)
            return redirect(url_for("post_routes.get_all_posts"))

    return render_template("login.html", form=login_form, current_user=current_user)


@user_routes.route("/register", methods=["GET", "POST"])
def register():
    register_form = RegisterUserForm()

    if register_form.validate_on_submit():
        result = db.session.execute(db.select(User).where(User.email == register_form.email.data))
        user = result.scalar()

        if user:
            flash("user already exists, please try to login")
            return redirect(url_for('user_routes.login'))

        password_to_save = generate_password_hash(register_form.password.data, method='pbkdf2', salt_length=10)
        user_to_register = User(
            email=register_form.email.data,
            name=register_form.name.data,
            password=password_to_save
        )
        db.session.add(user_to_register)
        db.session.commit()
        login_user(user_to_register)

        return redirect(url_for("post_routes.get_all_posts"))

    return render_template("register.html", form=register_form, current_user=current_user)


@user_routes.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("post_routes.get_all_posts"))
