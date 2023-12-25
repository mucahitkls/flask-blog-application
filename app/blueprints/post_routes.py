from flask import Blueprint, render_template, redirect, url_for, abort
from app.forms import CreatePostForm, CommentForm, UpdatePostForm
from app.database import db, crud_post, crud_comment
from flask_login import current_user
from functools import wraps

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
    return render_template("post.html", post=requested_post, current_user=current_user, form=comment_form)


@post_routes.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()

    if form.validate_on_submit():
        new_post = crud_post.create_new_post(db=db, create_post_form=form)
        return redirect(url_for("post_routes.show_post", post_id=new_post.id))

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
    if post_to_edit_form.validate_on_submit():
        updated_blog_post = crud_post.update_post(db=db, update_form=post_to_edit_form, post_to_update=blog_post)
        if updated_blog_post:
            return redirect(url_for("post_routes.show_post", post_id=blog_post.id))
    return render_template("make-post.html", form=post_to_edit_form, type='edit')


@post_routes.route('/delete/<int:post_id>')
@admin_only
def delete_post(post_id):
    crud_post.delete_post(db=db, post_id=post_id)
    return redirect(url_for("post_routes.get_all_posts"))
