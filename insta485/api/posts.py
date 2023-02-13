"""REST API for posts."""
import hashlib
import flask
from flask import jsonify
import insta485

def error_handler(status):
    """Error handler for client errors."""
    if status == 400:
        message = "Bad Request"
    if status == 403:
        message = "Forbidden"
    if status == 404:
        message = "Not Found"
    error = {
        "message": message,
        "status_code": status
    }

def access_control():
    """Make sure user is autheticated."""
    # If there's no Authorization header in the request, abort
    if not flask.request.authorization and not flask.session:
        return error_handler(403)

    # If session hasn't been initialized, verfiy user info in author header
    # HTTP Basic Authentication
    if not flask.session:
        username = flask.request.authorization["username"]
        submitted_password = flask.request.authorization["password"]
        
        # Abort if either field is empty
        if not username or not submitted_password:
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

    # Cookie authentication
    else: 
        # Abort if no cookies
        if "user" not in flask.session:
            return error_handler(403)
        username = flask.session["user"]

    # Different username setting depending on http or cookie
    return username


def comments_json(cur, connection):
    """Returns json representation of comments."""
    # Query db for all comment info on given post
    cur_comments = connection.execute(
        "SELECT commentid, owner, text "
        "FROM comments "
        "WHERE postid = ?", 
        (cur["postid"], )
    )
    comments_response = cur_comments.fetchall()

    # if comment owner and logged in user are the same, logname owns it
    for comment in comments_response:
        comment["lognameOwnsThis"] = (
            True if comment["owner"] == flask.session['user']
            else False
        )
        comment["ownerShowUrl"] = "/users/" + comment["owner"] + '/'
        comment["url"] = "/api/v1/comments/" + comment["commentid"] + '/'

    return comments_response


def likes_json(cur, connection):
    """Return json representation of likes."""
    # Get number of likes on the post from db
    cur_likes = connection.execute(
        "SELECT likeid, owner "
        "FROM likes "
        "WHERE postid = ?"
        (cur['postid'], )
    )
    likes_response = cur_likes.fecthall()
    
    # if the like's owner is the loggedin user, get the likeid
    likeid = None
    for like in likes_response:
        if like['owner'] == flask.session['user']:
            likeid = like['likeid']
            break
    # If the loggedin user doesn't like the post, like url is null
    likeurl = None
    if likeid:
        likeurl = "/api/v1/likes/" + likeid + "/"

    # If url exists, lognameLikesThis is true
    # The number of likes is the number of entries in likes_response
    likes = {
        "lognameLikesThis": bool(likeurl),
        "numLikes": len(likes_response),
        "url": likeurl
    }
    return likes

def posts_json(postid_lte, size, page, cur):
    """Returns the JSON representation of paginated posts."""
    # cur here is all the relevant posts in the db
    # TODO: check url result when empty, unsure
    if not cur: 
        next = ""
        results = []
    else:
        results = []
        for post in cur:
            post_json = {
                "postid": post['postid'],
                "url": "/api/v1/posts/" + cur['postid'] + "/"
            }
            results.append(post_json)
        
        # postid_lte is default if = -1, set to most recent post
        if postid_lte == -1:
            postid_lte = cur[0]['postid']

        # next is "" if number of posts < size of page
        if len(cur) < size:
            next = ""
        else: 
            next = "/api/v1/posts/" + (
                    f"?size={size}&page={page+1}&postid_lte={postid_lte}"
                )

    # url is the full url of the request, path + query
    posts_context = {
        "next": next, 
        "results": results,
        "url": flask.request.url
    }
    return posts_context


def post_json(cur, connection):
    """Return the JSON representation of one post."""
    comments = comments_json(cur, connection)
    likes = likes_json(cur, connection)
    post = {
        "comments": comments,
        "comments_url": "/api/v1/comments/?postid=" + cur['postid'],
        "created": cur['created'],
        "imgURL": "/uploads/" + cur['post_filename'], 
        "likes": likes,
        "owner": cur['owner'],
        "ownerImgUrl": "/uploads/" + cur['user_filename'],
        "ownerShowUrl": "/users/" + cur['owner'] + "/",
        "postShowUrl": "/posts/" + cur['postid'] + "/",
        "postid": cur['postid'],
        "url": flask.request.path
    }
    return post

@insta485.app.route('/api/v1/', methods=["GET"])
def get_services():
    """Return a list of services avaliable."""
    # Doesn't require user authentication per spec
    context = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url": "/api/v1/"
    }
    return jsonify(**context)

@insta485.app.route("/api/v1/posts/", methods=["GET"])
def get_posts():
    """Return the 10 newest posts."""
    username = access_control()

    # Get postid, size, and page from http request args
    size = flask.request.args.get("size", default=10, type=int)
    page = flask.request.args.get("page", default=0, type=int)
    # default should be to most recent postid, need to change once have posts
    postid_lte = flask.request.args.get("postid_lte", default=-1, type=int)
    # size and page need to be non-neg ints, flask coerced to int
    if size < 0 or page < 0:
        return error_handler(400)

    # offset specifies the number of rows to skip before starting to return rows
    # TODO: check if offset is correct
    offset = 10 * (page - 1)
    # Query db for all user posts and user following posts
    # limit specifies the number of rows to return (default 10)
    connection = insta485.model.get_db()
    cur_post = connection.execute(
        "SELECT posts.postid, posts.owner "
        "FROM posts "
        "WHERE owner = ? "
        "UNION "
        "SELECT posts.postid "
        "FROM following "
        "JOIN posts "
        "ON following.username2 = posts.owner "
        "WHERE following.username1 == ? "
        "ORDER BY postid DESC "
        "LIMIT ? OFFSET ?",
        (username, username, page, offset, )
    )   
    posts_response = cur_post.fetchall()

    posts_json = posts_json(postid_lte, size, page, posts_response)
    return jsonify(**posts_json)



@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/')
def get_post(postid_url_slug):
    """Return post on postid."""
    username = access_control()
    
    # Query db for post info given postid and owner info
    # User info isn't in posts page
    connection = insta485.model.get_db()
    cur_post = connection.execute(
        "SELECT posts.owner, posts.filename AS post_filename, "
        "posts.created, posts.postid, users.filename as user_filename"
        "FROM posts "
        "JOIN users "
        "ON posts.owner = users.username "
        "WHERE postid = ?",
        (postid_url_slug, )
    )
    # Should only be one bc 1 post and 1 owner joined
    post_info = cur_post.fetchone()

    # Abort if there is no post, not found
    if not post_info:
        return error_handler(404)
    
    post_json = post_json(post_info, connection)
    return jsonify(**post_json)
