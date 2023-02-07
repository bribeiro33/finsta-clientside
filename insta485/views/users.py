
"""
Insta485 users view.

URLs include:
/users/<user_url_slug>/
"""
from flask import (session, redirect, url_for, render_template, abort)
import insta485


@insta485.app.route('/users/<user_url_slug>/', methods=['GET'])
def user_page(user_url_slug):
    """GET the user's page given the url slug."""
    # Check if user's logged in, go to log in page if not
    if "user" not in session:
        return redirect(url_for("login_page"))

    # Check that user_url_slug exists in db, Abort if not
    connection = insta485.model.get_db()
    cur_slug = connection.execute(
        "SELECT username "
        "FROM users "
        "WHERE username = ? ",
        (user_url_slug, )
    )
    if not cur_slug.fetchall():
        abort(404)

    # Set var using for context and initialize ready keys
    user = {}
    user['logname'] = session['user']
    user['username'] = user_url_slug

    # Figure out if session user follows user_slug
    cur_relation = connection.execute(
        "SELECT username2 "
        "FROM following "
        "WHERE username1 = ? AND username2 = ?",
        (user['logname'], user_url_slug, )
    )

    # If logname follows slug, set var true, false otherwise
    if cur_relation.fetchone():
        user['logname_follows_username'] = True
    else:
        user['logname_follows_username'] = False

    # Query db for all the slug's posts
    cur = connection.execute(
        "SELECT postid, filename "
        "FROM posts "
        "WHERE owner = ?",
        (user_url_slug, )
    )
    user['posts'] = cur.fetchall()

    # Correctly find all the post paths
    for post in user['posts']:
        post['img_url'] = url_for("file_url", filename=post['filename'])

    # Calc total number of posts
    user['total_posts'] = len(user['posts'])

    # Query db for all followers to find the count
    # username1 follows username2, so username1 is a follower of username2
    cur = connection.execute(
        "SELECT COUNT(*) "
        "AS follower_count "
        "FROM following "
        "WHERE username2 = ?",
        (user_url_slug, )
    )
    user['followers'] = cur.fetchone()['follower_count']

    # Query db for all following to find the count
    # username1 follows username2, so username1 is following username2
    cur = connection.execute(
        "SELECT COUNT(*) "
        "AS following_count "
        "FROM following "
        "WHERE username1 = ?",
        (user_url_slug, )
    )
    user['following'] = cur.fetchone()['following_count']

    # Get fullname from db
    cur = connection.execute(
        "SELECT fullname "
        "FROM users "
        "WHERE username = ?",
        (user_url_slug, )
    )
    user['fullname'] = cur.fetchone()['fullname']

    return render_template("user.html", **user)
