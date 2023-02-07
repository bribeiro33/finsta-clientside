"""
Insta485 posts view.

URLs include:
/posts/
/posts/<postid_url_slug>/
"""
import os
import flask
from flask import (session, redirect, url_for, render_template, request, abort)
import insta485


@insta485.app.route('/posts/<postid_url_slug>/', methods=['GET'])
def post_page(postid_url_slug):
    """Get singular post page, redirect to login if not logged in."""
    if "user" not in session:
        return redirect(url_for("login_page"))

    user = session["user"]
    connection = insta485.model.get_db()

    # abort if post doesnt exist
    cur_post = connection.execute(
        "SELECT postid "
        "FROM posts "
        "WHERE postid = ?",
        (postid_url_slug, )
    )
    dawg = cur_post.fetchone()
    if not dawg:
        abort(404)

    cur_post = connection.execute(
        "SELECT filename, owner, created "
        "FROM posts "
        "WHERE postid = ?",
        (postid_url_slug, )
    )

    post = cur_post.fetchone()
    post['postid'] = postid_url_slug

    insta485.model.get_post(user, post, connection)
    # Slug = postid

    post['logname'] = user
    return render_template("post.html", **post)


def post_create():
    """Post a new post."""
    # Abort (backup) if user not logged in
    if "user" not in session:
        abort(403)

    connection = insta485.model.get_db()
    file_obj = flask.request.files["file"]
    # Abort if no file was submitted
    if not file_obj:
        abort(400)

    # Store new post pic on disk
    uuid_basename = insta485.model.store_pic(file_obj)

    # Insert into database
    connection.execute(
        "INSERT INTO "
        "posts(filename, owner) "
        "VALUES (?,?)",
        (uuid_basename, session['user'], )
    )


def post_delete():
    """Post a post deletion."""
    # Abort (backup) if user not logged in
    if "user" not in session:
        abort(403)

    # Get postid of desired post from form
    postid = flask.request.form['postid']
    connection = insta485.model.get_db()
    # abort if post doesnt exist
    cur_post = connection.execute(
        "SELECT filename "
        "FROM posts "
        "WHERE postid = ?",
        (postid, )
    )
    dawg = cur_post.fetchone()
    if not dawg:
        abort(404)

    # Get post owner and filename from db
    cur_file = connection.execute(
        "SELECT owner, filename "
        "FROM posts "
        "WHERE postid = ?",
        (postid, )
    )
    post = cur_file.fetchone()

    # Verify that user logged in is the post's owner
    if session['user'] != post['owner']:
        abort(403)

    # Delete post_img's file
    filename = post['filename']
    filepath = insta485.app.config["UPLOAD_FOLDER"]/filename
    os.remove(filepath)

    # Remove post from database
    connection.execute(
        "DELETE "
        "FROM posts "
        "WHERE postid = ?",
        (postid, )
    )


@insta485.app.route('/posts/', methods=['POST'])
def post_action():
    """Post possible post actions - create, delete."""
    operation = request.values.get('operation')
    if operation == 'create':
        post_create()
    elif operation == 'delete':
        post_delete()

    # Redirect to what target arg equals in from's action URL
    target_url = request.args.get('target')

    # If target not set, redirect to /users/<logname>/
    if not target_url:
        target_url = url_for('user_page', user_url_slug=session['user'])
    return redirect(target_url)
