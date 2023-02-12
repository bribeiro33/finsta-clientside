"""REST API for posts."""
import hashlib
import flask
from flask import jsonify
import insta485

def error_handler(status):
    """Error handler for client errors."""
    if status == 403:
        message = "Forbidden"
    error = {
        "message": message,
        "status_code": status
    }

def access_control(username, password):
    """Make sure user is autheticated."""
    # If there's no Authorization header in the request, abort
    if not flask.request.authorization and not flask.session:
        return error_handler(403)
    
    # If session hasn't been initialized, verfiy user info in author header
    if not flask.session:
        username = flask.request.authorization["username"]
        submitted_password = flask.request.authorization["password"]
        
        # Abort if either field is empty
        if not username or not password:
            return error_handler(403)
        
        # Authenticate user information by checking db
        connection = insta485.model.get_db()
        cur_users = connection.execute(
            "SELECT password "
            "FROM users "
            "WHERE username = ?",
            (username, )
        )
        correct_pass = cur_users.fetchone()

        # If username doesn't have a password, abort
        if not correct_pass:
            return error_handler(403)

        # Verify password by computing hashed pass w/ SHA512 of submitted password
        #   and comparing it against the db password
        algorithm, salt, db_password = correct_pass['password'].split('$')

        # Slightly modified from spec
        hash_obj = hashlib.new(algorithm)
        password_salted = salt + submitted_password
        hash_obj.update(password_salted.encode('utf-8'))
        submitted_password_hash = hash_obj.hexdigest()

        if submitted_password_hash != db_password:
            return error_handler(403)

    else: 
        # Abort if no cookies
        if "user" not in flask.session:
            return error_handler(403)
        

@insta485.app.route('/api/v1/', methods=["GET"])
def get_index():
    """Return a list of services avaliable."""
    # Doesn't require user authentication per spec
    context = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url": "/api/v1/"
    }
    return jsonify(**context)


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/')
def get_post(postid_url_slug):
    """Return post on postid.


    Example:
    {
        "created": "2017-09-28 04:33:28",
        "imgUrl": "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg",
        "owner": "awdeorio",
        "ownerImgUrl": "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
        "ownerShowUrl": "/users/awdeorio/",
        "postShowUrl": "/posts/1/",
        "url": "/api/v1/posts/1/"
    }
    """
    context = {
        "created": "2017-09-28 04:33:28",
        "imgUrl": "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg",
        "owner": "awdeorio",
        "ownerImgUrl": "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
        "ownerShowUrl": "/users/awdeorio/",
        "postid": "/posts/{}/".format(postid_url_slug),
        "url": flask.request.path,
    }
    return flask.jsonify(**context)
