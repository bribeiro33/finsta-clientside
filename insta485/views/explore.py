"""
Insta485 explore view.

URLs include:
/explore/
"""
import flask
from flask import (session, redirect, url_for)
import insta485


@insta485.app.route('/explore/', methods=["GET"])
def explore():
    """Display explore route."""
    # Connect to database
    connection = insta485.model.get_db()
    # Check if user's logged in, go to log in page if not
    if "user" not in session:
        return redirect(url_for("login_page"))
    user = session["user"]
    # get the usernames of NONFOLLOWED people, so you have to check that they
    # arent in the user's follows list
    cur = connection.execute(
        "SELECT username "
        "FROM users "
        "WHERE username!=?"
        "AND username NOT IN ( "
        "SELECT username2 "
        "FROM following "
        "WHERE username1=?)",
        (user, user, )
    )
    all_users = cur.fetchall()
    for u_s in all_users:
        # Get icon
        cur_icon = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username=?",
            (u_s['username'], )
        )
        icon = cur_icon.fetchone()['filename']
        u_s['user_img_url'] = flask.url_for("file_url", filename=icon)
    # Add database info to context
    context = {"users": all_users, "logname": user}
    return flask.render_template("explore.html", **context)
