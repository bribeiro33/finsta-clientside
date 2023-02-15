"""REST API for comments."""
from flask import jsonify, request
import insta485

@insta485.app.route('/api/v1/comments/', methods=["POST"])
def post_comment():
    """Posts a new comment with the given text and id."""
    username = insta485.api.posts.access_control()
    # if access_control returns a tuple, that means an error occured
    if type(username) is tuple:
        return username
    connection = insta485.model.get_db()

    text = request.json.get("text")
    postid = request.args.get("postid", default=-1, type=int)

    # Error if post_id is a negative number or wasn't specified
    if postid < 0:
        return insta485.api.posts.error_handler(400)
    
    # Make sure post exists in db, error if not found
    cur_post = connection.execute(
        "SELECT * "
        "FROM posts "
        "WHERE postid = ?", 
        (postid, )
    )
    post_request = cur_post.fetchone()
    if not post_request:
        return insta485.api.posts.error_handler(404)

    # Insert new comment in db with values from request
    connection.execute(
        "INSERT INTO comments(owner, postid, text) "
        "VALUES (?, ?, ?)", 
        (username, postid, text, )
    )

    # Retrieve the ID of the most recently inserted item to show in response
    new_commentid = connection.execute(
        "SELECT last_insert_rowid() AS commentid"
    ).fetchone()

    comment_context = {
        "commentid": new_commentid['commentid'],
        "lognameOwnsThis": True,
        "owner": username,
        "ownerShowUrl": "/users/" + username + "/",
        "text": text,
        "url": request.path + str(new_commentid['commentid']) + "/"
    }
    return jsonify(**comment_context), 201

@insta485.app.route('/api/v1/comments/<int:cmtid_slug>/', methods=["DELETE"])
def delete_comment(cmtid_slug):
    """Delete a comment given a commentid."""
    username = insta485.api.posts.access_control()
    # if access_control returns a tuple, that means an error occured
    if type(username) is tuple:
        return username

    connection = insta485.model.get_db()

    # Make sure commentid exists, if not, error 404 not found
    cur_comment = connection.execute(
        "SELECT commentid, owner "
        "FROM comments "
        "WHERE commentid = ?",
        (cmtid_slug, )
    )
    comment_request = cur_comment.fetchone()
    if not comment_request:
        return insta485.api.posts.error_handler(404)

    # If comment's owner isn't the loggedin user, error 403 forbidden
    if comment_request['owner'] != username:
        return insta485.api.posts.error_handler(403)

    # Delete comment by its id
    connection.execute(
        "DELETE FROM comments "
        "WHERE commentid = ?",
        (cmtid_slug, )
    )
    return '', 204