"""
Insta485 accounts view.

URLs include:
/accounts/login/
/accounts/logout/
/accounts/create/
/accounts/delete/
/accounts/edit/
/accounts/password/
"""
import uuid
import pathlib
import hashlib
import os
import flask
from flask import (session, redirect, url_for, render_template, request, abort)
import insta485


# ============================ Login/out ===================================
@insta485.app.route('/accounts/login/', methods=["GET"])
def login_page():
    """GET if user logged in and login page."""
    # If user is logged in, redirect to home/index
    if "user" in session:
        return redirect(url_for("show_index"))

    # If user is not logged in, render login page
    return render_template("login.html")


def login():
    """POST user's login info."""
    # Recieve user info from form in login.html
    username = request.values.get('username')
    submitted_password = request.values.get('password')

    # If either field is empty, abort
    if not username or not submitted_password:
        abort(400)

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
        abort(403)

    # Verify password by computing hashed pass w/ SHA512 of submitted password
    #   and comparing it against the db password
    algorithm, salt, db_password = correct_pass['password'].split('$')

    # Slightly modified from spec
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + submitted_password
    hash_obj.update(password_salted.encode('utf-8'))
    submitted_password_hash = hash_obj.hexdigest()

    if submitted_password_hash != db_password:
        abort(403)

    # Set session cookie w/ username
    session['user'] = username

    target_url = request.args.get('target')
    type(target_url)


# Can't be in post_accounts because no target arg
@insta485.app.route('/accounts/logout/', methods=["POST"])
def logout():
    """POST logout of account request."""
    user = session.get('user')

    # Error somehwere if user is not logged in here, safety
    # Clears cookies
    if user:
        session.clear()

    return redirect(url_for('login_page'))

# ============================ Create =====================================


# Renders the create an account page, redirect to edit if logged in
@insta485.app.route('/accounts/create/', methods=['GET'])
def create_page():
    """GET create account page."""
    if "user" in session:
        redirect(url_for('edit.html'))
    return render_template('create.html')


def create_account():
    """POST created account."""
    # Get information from form on create page
    username = request.form['username']
    password = request.form['password']
    full_name = request.form['fullname']
    email = request.form['email']
    file_obj = request.files['file']

    # If something hasn't been filled out, abort
    if not (username and password and full_name and email and file_obj):
        abort(400)

    # If username already exists, abort
    connection = insta485.model.get_db()
    cur_users = connection.execute(
        "SELECT username "
        "FROM users "
        "WHERE username == ?",
        (username, )
    )
    if cur_users.fetchone():
        abort(409)

    # Hash password to store securley
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])

    # Convert file into appropriate format
    # Unpack flask obj
    # filename = file_obj.filename

    # Compute base name
    # stem = uuid.uuid4().hex
    # suffix = pathlib.Path(file_obj.filename).suffix.lower()
    # uuid_basename = f"{stem}{suffix}"
    # uuid_basename is now called u_b
    u_b = f"{uuid.uuid4().hex}{pathlib.Path(file_obj.filename).suffix.lower()}"

    # Save to disk
    path = insta485.app.config["UPLOAD_FOLDER"]/u_b
    file_obj.save(path)

    # Insert into database
    connection.execute(
        "INSERT INTO "
        "users(username, fullname, email, filename, password) "
        " VALUES (?,?,?,?,?)",
        (username, full_name, email, file_obj.filename, password_db_string, )
    )

    # Log new user in, set session cookie
    session['user'] = username

# ============================ Edit =====================================


# Renders the edit your account page, redirect to edit if logged in
@insta485.app.route('/accounts/edit/', methods=['GET'])
def edit_page():
    """GET edit account page."""
    # Query db for logged in user's current info
    connection = insta485.model.get_db()
    cur_user = connection.execute(
        "SELECT username, fullname, email, filename "
        "FROM users "
        "WHERE username == ?",
        (session['user'], )
    )
    user_profile = cur_user.fetchone()
    if not user_profile:
        abort(403)

    # Fix file path to work w/ flask
    file_prof = user_profile['filename']
    user_profile['filename'] = flask.url_for("file_url", filename=file_prof)

    context = {"user": user_profile, "logname": session['user'], }
    return render_template('edit.html', **context)


def edit_account():
    """POST edits to user's account."""
    # Check that user is logged in
    if "user" not in session:
        abort(403)

    # Get data from form
    # Can't change username, and can't change password on this page
    full_name = request.form['fullname']
    email = request.form['email']
    file_obj = request.files['file']

    # Abort if required fields are empty
    if not (full_name and email):
        abort(400)

    # Update full_name and email fields
    connection = insta485.model.get_db()
    connection.execute(
        "UPDATE users "
        "SET fullname = ?, email = ? "
        "WHERE username = ?",
        (full_name, email, session['user'], )
    )

    # Update profile pic if submitted
    if file_obj:
        # Delete old profile pic
        cur_oldfile = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username = ?",
            (session['user'], )
        )
        oldfile = cur_oldfile.fetchone()['filename']
        oldpath = insta485.app.config["UPLOAD_FOLDER"]/oldfile
        # HERE check if works
        os.remove(oldpath)

        # Format new profile pic
        uuid_basename = insta485.model.store_pic(file_obj)

        # Insert into database
        connection.execute(
            "UPDATE users "
            "SET filename = ? "
            "WHERE username = ?",
            (uuid_basename, session['user'])
        )

# ============================ Delete =====================================


@insta485.app.route('/accounts/delete/', methods=['GET'])
def delete_page():
    """GET delete account page, redirects to login if no cookies."""
    user = session['user']
    if not user:
        return redirect(url_for("login_page"))
    context = {"logname": user}
    return render_template('delete.html', **context)


def delete_account():
    """POST delete user account request."""
    # Abort if user not logged in
    if "user" not in session:
        abort(403)

    # Delete all files assoc w/ user
    # Query profile pic
    connection = insta485.model.get_db()
    cur_profilepic = connection.execute(
        "SELECT filename "
        "FROM users "
        "WHERE username = ?",
        (session['user'], )
    )

    # Delete profile pic path
    prof_file = cur_profilepic.fetchone()['filename']
    # If other is wrong, so is this one
    prof_path = insta485.app.config["UPLOAD_FOLDER"]/prof_file
    os.remove(prof_path)

    # Query all post paths
    cur_posts = connection.execute(
        "SELECT filename "
        "FROM posts "
        "WHERE owner = ?",
        (session['user'], )
    )
    post_files = cur_posts.fetchall()
    # Delete all post paths
    for post_file in post_files:
        post_path = insta485.app.config["UPLOAD_FOLDER"]/post_file['filename']
        os.remove(post_path)

    # Delete all assoc entries by deleting 'user' entry,
    #   should work if db set up correctly
    connection.execute(
        "DELETE FROM users "
        "WHERE username = ?",
        (session['user'], )
    )

    # clear session cookies
    session.clear()

# ======================== Change Password ================================


@insta485.app.route('/accounts/password/', methods=['GET'])
def password_page():
    """GET edit password page, redirects to login if no cookies."""
    if "user" not in session:
        return redirect(url_for("login_page"))
    context = {'logname': session['user'], }
    return render_template('password.html', **context)


def edit_password_account():
    """POST password change after user verification and formatting new pass."""
    # Abort forbidden if user not logged in
    if "user" not in session:
        abort(403)

    # Get passwords from form on page
    old_password = request.form['password']
    new_pass1 = request.form['new_password1']
    new_pass2 = request.form['new_password2']

    # Abort if any field is empty
    if not (old_password and new_pass1 and new_pass2):
        abort(400)

    # Verfiy submitted old password by hashing it and comparing
    #   with hashed one in db
    connection = insta485.model.get_db()
    cur_pass = connection.execute(
        "SELECT password "
        "FROM users "
        "WHERE username = ?",
        (session['user'], )
    )
    hashed_db_pass = cur_pass.fetchone()['password']
    # Abort if password doesn't exist in db
    if not hashed_db_pass:
        abort(403)

    # Verify password by computing hashed pass w/ SHA512 of submitted password
    #   and comparing it against the db password
    algorithm, salt, db_pass = hashed_db_pass.split('$')

    # Slightly modified from spec
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + old_password
    hash_obj.update(password_salted.encode('utf-8'))
    hashed_sub_pass = hash_obj.hexdigest()

    # Abort if submitted old pass doesn't match db pass
    if db_pass != hashed_sub_pass:
        abort(403)

    # Abort if new passwords don't match
    if new_pass1 != new_pass2:
        abort(401)

    # Hash new password before storing in db
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + new_pass1
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    hashed_new_pass = "$".join([algorithm, salt, password_hash])

    # Update db with new password
    connection.execute(
        "UPDATE users "
        "SET password = ? "
        "WHERE username = ?",
        (hashed_new_pass, session['user'], )
    )

# ======================== POST Operations ================================


# Various post requests from accounts with operation values
@insta485.app.route('/accounts/', methods=['POST'])
def post_accounts():
    """All /accounts/?target= POST requests."""
    operation = request.values.get('operation')
    if operation == "login":
        login()
    elif operation == "create":
        create_account()
    elif operation == "edit_account":
        edit_account()
    elif operation == "delete":
        delete_account()
    elif operation == "update_password":
        edit_password_account()
    else:
        return redirect(url_for('show_index'))

    # Redirect to what target arg equals in from's action URL
    target_url = request.args.get('target')

    # For whatever reason, when ?target=/, target evaluates to None
    if not target_url:
        target_url = "/"
    return redirect(target_url)
