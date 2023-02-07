"""
Insta485 like button view.

URLs include:
/likes/
"""
from flask import (session, redirect, request, abort)
import insta485


@insta485.app.route('/likes/', methods=['POST'])
def like_action():
    """POST all /likes/?target= requests - like and dislike."""
    # Get type of operation from form depending on button pressed
    operation = request.values.get('operation')
    # Get postid from form
    postid = request.form['postid']

    # Use db to get logged in user's like or lack thereof for this post
    connection = insta485.model.get_db()
    cur_likes = connection.execute(
        "SELECT owner "
        "FROM likes "
        "WHERE owner = ? AND postid = ?",
        (session['user'], postid, )
    )
    does_like = cur_likes.fetchone()

    if operation == 'like':
        # Abort if user already liked this post
        if does_like:
            abort(409)
        # If user hasn't already liked post, create a like for postid by user
        connection.execute(
            "INSERT INTO "
            "likes(owner, postid) "
            "VALUES (?, ?)",
            (session['user'], postid, )
        )

    elif operation == 'unlike':
        # Abort if user already disliked this post
        if not does_like:
            abort(409)
        # If user hasn't already disliked post, delete like for postid by user
        connection.execute(
            "DELETE FROM likes "
            "WHERE owner = ? AND postid = ?",
            (session['user'], postid, )
        )

    # Redirect to what target arg equals in from's action URL
    target_url = request.args.get('target')
    # For whatever reason, when ?target=/, target evaluates to None
    if not target_url:
        target_url = "/"
    return redirect(target_url)
