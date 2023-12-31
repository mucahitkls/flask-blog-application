from flask import Blueprint, render_template, redirect, url_for, abort, flash
from app.forms import CreatePostForm, CommentForm, UpdatePostForm
from app.database import db, crud_post, crud_comment
from flask_login import current_user
from functools import wraps
import logging
post_routes = Blueprint('post_routes', __name__)


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


@post_routes.route('/')
def get_all_posts():
    posts = crud_post.get_all_posts(db=db)
    return render_template("index.html", all_posts=posts, current_user=current_user)


@post_routes.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = crud_post.get_post_by_id(db=db, post_id=post_id)
    comment_form = CommentForm()
    try:
        if comment_form.validate_on_submit():
            if not current_user.is_authenticated:
                return redirect(url_for("user_routes.login"))

            result = crud_comment.get_comment_by_text(db=db, comment_form=comment_form)
            if not result:
                crud_comment.create_comment(db=db, comment_form=comment_form, requested_post=requested_post)
                comment_form.comment_text.data = ""
            elif result.comment_author != current_user:
                crud_comment.create_comment(db=db, comment_form=comment_form, requested_post=requested_post)
                comment_form.comment_text.data = ""

    except Exception as e:
        logging.error(f"Showing post error for post_id: {post_id}, error: {e}")
    return render_template("post.html", post=requested_post, current_user=current_user, form=comment_form)


@post_routes.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    try:
        if form.validate_on_submit():
            post_title = form.title.data
            is_post_exists = crud_post.get_post_by_title(db=db, title=post_title)
            if not is_post_exists:
                new_post = crud_post.create_new_post(db=db, create_post_form=form)
                logging.info(f"New post {form.title.data} created by {current_user.email}")
                return redirect(url_for("post_routes.show_post", post_id=new_post.id))
            else:
                flash("There is already a post with that title", 'error')
                logging.warning(f"Post title {form.title.data} already exists.")
                form.title.data = ""
                # Instead of redirecting, re-render the same page with the form containing the existing data
                return render_template("make-post.html", form=form, type='create')
    except Exception as e:
        logging.error(f"Post creation failed: {e}")

    return render_template("make-post.html", form=form, type='create')


@post_routes.route("/edit/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    blog_post = crud_post.get_post_by_id(db=db, post_id=post_id)
    post_to_edit_form = UpdatePostForm(
        title=blog_post.title,
        subtitle=blog_post.subtitle,
        author=blog_post.author,
        img_url=blog_post.img_url,
        body=blog_post.body
    )
    try:
        if post_to_edit_form.validate_on_submit():
            updated_blog_post = crud_post.update_post(db=db, update_form=post_to_edit_form, post_to_update=blog_post)
            if updated_blog_post:
                return redirect(url_for("post_routes.show_post", post_id=blog_post.id))

    except Exception as e:
        logging.error(f"Post update failed: {e}")
    return render_template("make-post.html", form=post_to_edit_form, type='edit')


@post_routes.route('/delete/<int:post_id>')
@admin_only
def delete_post(post_id):
    try:
        crud_post.delete_post(db=db, post_id=post_id)
    except Exception as e:
        logging.error(f"Post deletion failed: {e}")
    return redirect(url_for("post_routes.get_all_posts"))
