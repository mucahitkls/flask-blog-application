from flask import Blueprint, render_template, redirect, url_for, flash
from app.forms import LoginUserForm, RegisterUserForm
from app.database import db
from app.database import crud_user
from app.services import authentication
from flask_login import login_user, current_user, logout_user

# Blueprint definition
user_routes = Blueprint('user_routes', __name__)


@user_routes.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginUserForm()

    if login_form.validate_on_submit():

        user = crud_user.get_user_by_mail(db=db, email=login_form.email.data)
        password = login_form.password.data
        if not user:
            flash("User does not exist")
            return redirect(url_for("user_routes.login"))

        elif not authentication.confirm_password(user.password, password):
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
        user = crud_user.get_user_by_mail(db=db, email=register_form.email.data)
        if user:
            flash("user already exists, please try to login")
            return redirect(url_for('user_routes.login'))

        user_to_register = crud_user.create_user(db=db, register_form=register_form)
        if user_to_register:
            login_user(user_to_register)
            return redirect(url_for("post_routes.get_all_posts"))
    return render_template("register.html", form=register_form, current_user=current_user)


@user_routes.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("post_routes.get_all_posts"))
