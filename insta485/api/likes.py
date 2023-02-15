"""REST API for comments."""
from flask import jsonify, request
import insta485

@insta485.app.route('/api/v1/likes/', methods=["POST"])
def post_likes():
    """Posts a new like with the given id."""
    username = insta485.api.posts.access_control()
    # if access_control returns a tuple, that means an error occured
    if type(username) is tuple:
        return username
    connection = insta485.model.get_db()

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

    # Get all like owners for the given post
    cur_like = connection.execute(
        "SELECT owner "
        "FROM likes "
        "WHERE postid = ?", 
        (postid, )
    )
    owner_request = cur_like.fetchall()

    # if like by owner already exists, return object and 200 response
    ownerCheck = {'owner': username}
    if ownerCheck in owner_request:
        # Get the likeid of the username's like
        cur_like = connection.execute(
            "SELECT likeid "
            "FROM likes "
            "WHERE postid = ? AND owner = ?", 
            (postid, username, )
        )
        likeid_request = cur_like.fetchone()
        like_context = {
            "likeid": likeid_request['likeid'],
            "url": request.path + str(likeid_request['likeid']) + "/"
        }
        code = 200
    
    # otherwise, insert into db and return object and 201 response
    else:
        # Insert new like in db with like owner and postid
        connection.execute(
            "INSERT INTO likes(owner, postid) "
            "VALUES (?, ?)", 
            (username, postid, )
        )

        # Retrieve the ID of the most recently inserted item to show in response
        new_likeid = connection.execute(
            "SELECT last_insert_rowid() AS likeid"
        ).fetchone()

        like_context = {
            "likeid": new_likeid['likeid'],
            "url": request.path + str(new_likeid['likeid']) + "/"
        }
        code = 201
    
    return jsonify(**like_context), code


@insta485.app.route('/api/v1/likes/<int:likeid_slug>/', methods=["DELETE"])
def delete_likes(likeid_slug):
    """Delete a comment given a commentid."""
    username = insta485.api.posts.access_control()
    # if access_control returns a tuple, that means an error occured
    if type(username) is tuple:
        return username
    connection = insta485.model.get_db()

    # Make sure likeid exists, if not, error 404 not found
    cur_like = connection.execute(
        "SELECT likeid, owner "
        "FROM likes "
        "WHERE likeid = ?",
        (likeid_slug, )
    )
    like_request = cur_like.fetchone()
    if not like_request:
        return insta485.api.posts.error_handler(404)

    # If comment's owner isn't the loggedin user, error 403 forbidden
    if like_request['owner'] != username:
        return insta485.api.posts.error_handler(403)

    # Delete comment by its id
    connection.execute(
        "DELETE FROM likes "
        "WHERE likeid = ?",
        (likeid_slug, )
    )
    return '', 204