from flask import Blueprint, render_template, redirect, url_for, abort
from app.forms import CreatePostForm, CommentForm
from app.models import BlogPost, Comment, db
from flask_login import current_user
from functools import wraps
from datetime import date

post_routes = Blueprint('post_routes', __name__)


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


@post_routes.route('/')
def get_all_posts():
    posts = db.session.execute(db.select(BlogPost)).scalars().all()
    return render_template("index.html", all_posts=posts, current_user=current_user)


@post_routes.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalar()
    comment_form = CommentForm()

    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            return redirect(url_for("user_routes.login"))

        result = db.session.execute(db.select(Comment).where(Comment.text == comment_form.comment_text.data)).scalar()
        if not result:
            new_comment = Comment(
                text=comment_form.comment_text.data,
                comment_author=current_user,
                parent_post=requested_post
            )

            db.session.add(new_comment)
            db.session.commit()

        elif result.comment_author != current_user:
            new_comment = Comment(
                text=comment_form.comment_text.data,
                comment_author=current_user,
                parent_post=requested_post
            )

            db.session.add(new_comment)
            db.session.commit()

    return render_template("post.html", post=requested_post, current_user=current_user, form=comment_form)


@post_routes.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()

    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("post_routes.show_post", post_id=new_post.id))

    return render_template("make-post.html", form=form, type='create')


@post_routes.route("/edit/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    blog_post = db.get_or_404(BlogPost, post_id)

    post_to_edit_form = CreatePostForm(
        title=blog_post.title,
        subtitle=blog_post.subtitle,
        author=blog_post.author,
        img_url=blog_post.img_url,
        body=blog_post.body
    )

    if post_to_edit_form.validate_on_submit():
        blog_post.title = post_to_edit_form.title.data
        blog_post.subtitle = post_to_edit_form.subtitle.data
        blog_post.author = current_user
        blog_post.img_url = post_to_edit_form.img_url.data
        blog_post.body = post_to_edit_form.body.data
        db.session.commit()
        return redirect(url_for("post_routes.show_post", post_id=blog_post.id))

    return render_template("make-post.html", form=post_to_edit_form, type='edit')


@post_routes.route('/delete/<int:post_id>')
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for("post_routes.get_all_posts"))
