"""
Insta485 followers view.

URLs include:
/users/<user_url_slug>/followers/
"""
from flask import (session, redirect, url_for, render_template, abort)
import insta485


@insta485.app.route('/users/<user_url_slug>/followers/', methods=["GET"])
def show_followers(user_url_slug):
    """Display followers route."""
    # Check if user's logged in, go to log in page if not
    if "user" not in session:
        return redirect(url_for("login_page"))

    # Connect to database
    connection = insta485.model.get_db()
    user = session["user"]

    # Abort if user_slug is not in db
    cur_user = connection.execute(
        "SELECT username "
        "FROM users "
        "WHERE username = ?",
        (user_url_slug, )
    )
    dawg = cur_user.fetchone()
    if not dawg:
        abort(404)

    # get the followers of user_url_slug
    cur = connection.execute(
        "SELECT username1 "
        "FROM following "
        "WHERE username2=?",
        (user_url_slug, )
    )
    # username1 follows username2
    # the above gets all the rows of column 'username1' where username1
    # follows the user

    # loop through all followers
    # [{username1: golpari, username2: bdreyer},
    # {username1:bdreyer. username2: golpari}]
    f_c = cur.fetchall()
    for fol in f_c:
        # Formatting to fit into template name
        fol['username'] = fol['username1']

        # Check if user follows the people in the followers list
        # Get icon
        insta485.model.check_follower_get_icon(user, fol, connection)

    context = {'followers': f_c, "logname": user}
    return render_template("followers.html", **context)
