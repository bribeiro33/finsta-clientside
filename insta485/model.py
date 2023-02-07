"""Insta485 model (database) API."""
import uuid
import pathlib
import sqlite3
import flask
import arrow
import insta485


def dict_factory(cursor, row):
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def get_db():
    """Open a new database connection.

    Flask docs:
    https://flask.palletsprojects.com/en/1.0.x/appcontext/#storing-data
    """
    if 'sqlite_db' not in flask.g:
        db_filename = insta485.app.config['DATABASE_FILENAME']
        flask.g.sqlite_db = sqlite3.connect(str(db_filename))
        flask.g.sqlite_db.row_factory = dict_factory

        # Foreign keys have to be enabled per-connection.  This is an sqlite3
        # backwards compatibility thing.
        flask.g.sqlite_db.execute("PRAGMA foreign_keys = ON")
    return flask.g.sqlite_db


@insta485.app.teardown_appcontext
def close_db(error):
    """Close the database at the end of a request.

    Flask docs:
    https://flask.palletsprojects.com/en/1.0.x/appcontext/#storing-data
    """
    assert error or not error  # Needed to avoid superfluous style error
    sqlite_db = flask.g.pop('sqlite_db', None)
    if sqlite_db is not None:
        sqlite_db.commit()
        sqlite_db.close()


def get_post(user, post, connection):
    """Set up post dictionary with its proper values."""
    # Correct post's img url
    post['img_url'] = flask.url_for("file_url", filename=post['filename'])

    # Correct timestamp format
    post['timestamp'] = arrow.get(post['created']).humanize()

    # Query post's owner's icon url
    cur_owner = connection.execute(
        "SELECT filename "
        "FROM users "
        "WHERE username = ?",
        (post['owner'], )
    )
    icon = cur_owner.fetchone()['filename']
    post['owner_img_url'] = flask.url_for("file_url", filename=icon)

    # Query comments
    cur_comments = connection.execute(
        "SELECT commentid, owner, postid, text "
        "FROM comments "
        "WHERE postid = ? "
        "ORDER BY commentid ASC",
        (post['postid'], )
    )
    post['comments'] = cur_comments.fetchall()

    # Query likes
    cur_likes = connection.execute(
        "SELECT COUNT(owner) AS num_likes "
        "FROM likes "
        "WHERE postid = ?",
        (post['postid'], )
    )

    post['likes'] = cur_likes.fetchone()['num_likes']

    # Query if user likes the post
    cur_user_likes = connection.execute(
        "SELECT owner "
        "FROM likes "
        "WHERE owner=? AND postid=?",
        [user, post['postid']]
    )

    # Will return an entry if user likes the post
    if cur_user_likes.fetchone():
        post['user_likes_it'] = True
    else:
        post['user_likes_it'] = False


def check_follower_get_icon(user, fol, connection):
    """Find follower relationship and get follower/followee icon."""
    # Check if user is following the people in the following list
    cur = connection.execute(
        "SELECT username2 "
        "FROM following "
        "WHERE username1=? AND username2=?",
        (user, fol['username'], )
    )

    name = cur.fetchone()
    if name:
        fol['logname_follows_username'] = True
    else:
        fol['logname_follows_username'] = False

    # Get icon
    cur_icon = connection.execute(
        "SELECT filename "
        "FROM users "
        "WHERE username=?",
        (fol['username'], )
    )
    icon = cur_icon.fetchone()['filename']
    fol['user_img_url'] = flask.url_for("file_url", filename=icon)


def store_pic(file_obj):
    """Store new image on disk after formatting filename."""
    # Unpack flask obj
    filename = file_obj.filename

    # Compute base name
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix.lower()
    uuid_basename = f"{stem}{suffix}"

    # Save to disk
    path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    file_obj.save(path)

    return uuid_basename
