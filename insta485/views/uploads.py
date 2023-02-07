"""
Insta485 uploads path view.

URLs include:
/uploads/<path:filename>
"""
import flask
import insta485


@insta485.app.route('/uploads/<path:filename>')
def file_url(filename):
    """Return correct picture filepath."""
    # Abort if unautheticated user tries to access file
    if "user" not in flask.session:
        flask.abort(403)

    file_ur = flask.send_from_directory(insta485.app.config['UPLOAD_FOLDER'],
                                        filename, as_attachment=True)
    # Abort if user tries to access file that doesn't exist
    if not file_ur:
        flask.abort(404)

    return file_ur
