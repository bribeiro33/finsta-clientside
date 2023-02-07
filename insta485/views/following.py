"""
Insta485 following view.

URLs include:
/users/<user_url_slug>/following/
"""
from flask import (session, redirect, url_for, render_template, request, abort)
import insta485


# same as following.py
@insta485.app.route('/users/<user_url_slug>/following/', methods=["GET"])
def show_following(user_url_slug):
    """Display following route."""
    # Check if user's logged in, go to log in page if not
    if "user" not in session:
        return redirect(url_for("login_page"))

    user = session["user"]
    # Connect to database
    connection = insta485.model.get_db()

    # Abort if user_slug is not in db
    cur_user_slug = connection.execute(
        "SELECT username "
        "FROM users "
        "WHERE username = ?",
        (user_url_slug, )
    )
    user_slug = cur_user_slug.fetchone()
    if not user_slug:
        abort(404)

    # get the followings of username1 where username2
    # is a followedPerson by username1
    cur = connection.execute(
        "SELECT username2 "
        "FROM following "
        "WHERE username1=?",
        (user_url_slug, )
    )
    # username1 follows username2
    # the above gets all the rows of column 'username1'
    # where username1 follows the user

    # loop through all followers
    # [{username1: golpari, username2: bdreyer},
    # {username1:bdreyer. username2: golpari}]
    f_c = cur.fetchall()
    for fol in f_c:
        # Formatting to fit into template name
        fol['username'] = fol['username2']

        # Check if user is following the people in the following list
        # Get icon
        insta485.model.check_follower_get_icon(user, fol, connection)

    context = {'following': f_c, "logname": user}
    return render_template("following.html", **context)


# not from followers! the POST request!
@insta485.app.route('/following/', methods=["POST"])
def change_following():
    """Change following route: ALL /following/?target=URL POST requests."""
    # Check if user's logged in, go to log in page if not
    if "user" not in session:
        return redirect(url_for("login_page"))

    logname = session["user"]

    # Get username from form
    username = request.form["username"]
    # Connect to database
    connection = insta485.model.get_db()

    # Abort if user_slug is not in db
    cur_user = connection.execute(
        "SELECT username "
        "FROM users "
        "WHERE username = ?",
        (username, )
    )
    dawg = cur_user.fetchone()
    if not dawg:
        abort(404)

    operation = request.values.get('operation')

    # find when user follows otheruser, and get the entire row from the table
    cur = connection.execute(
        "SELECT * "
        "FROM following "
        "WHERE username1=? and username2=?",
        (logname, username)
    )
    folling = cur.fetchall()

    if operation == 'follow':
        # tries to follow a user that they already follow
        if folling:
            abort(409)

        # otherwise just follow the account!
        else:
            connection.execute(
                "INSERT INTO following(username1, username2) VALUES "
                "(?, ?)", (logname, username, )
            )

    if operation == 'unfollow':
        # tries to unfollow a user that they do not follow
        if not folling:
            abort(409)
        # otherwise just unfollow the account!
        else:
            # delete username1 from following username2
            connection.execute(
                "DELETE FROM following "
                "WHERE username1=? AND username2=?",
                (logname, username,)
            )

    targeturl = request.args.get("target")
    # redirect to target if it is set
    if targeturl:
        return redirect(targeturl)
    # redirect to index if no target specified
    return redirect(url_for('show_index'))
