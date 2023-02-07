"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
from flask import (session, redirect, url_for)
import insta485


@insta485.app.route('/')
def show_index():
    """Display / route."""
    # Check if user's logged in, go to log in page if not
    if "user" not in session:
        return redirect(url_for("login_page"))

    user = session["user"]
    # Connect to database
    connection = insta485.model.get_db()

    # Query posts
    cur = connection.execute(
        "SELECT postid, filename, owner, created "
        "FROM posts "
        "WHERE owner = ? "
        "UNION "
        "SELECT posts.postid, posts.filename, posts.owner, posts.created "
        "FROM following JOIN posts "
        "ON following.username2 = posts.owner "
        "WHERE following.username1 == ? "
        "ORDER BY postid DESC",
        (user, user, )
    )
    posts = cur.fetchall()
    for post in posts:
        insta485.model.get_post(user, post, connection)

    # Add database info to context
    context = {"posts": posts, "logname": user}
    return flask.render_template("index.html", **context)
