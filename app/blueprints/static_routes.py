from flask import Blueprint, render_template, request, redirect, url_for
import logging
static_routes = Blueprint("static_routes", __name__)


@static_routes.route("/about")
def about():
    logging.info("Visited about page.")
    return render_template("about.html")


@static_routes.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        logging.info("Contact form submitted.")
        return redirect(url_for("post_routes.get_all_posts"))

    return render_template("contact.html")
