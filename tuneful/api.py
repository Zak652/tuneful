import os.path
import json

from flask import request, Response, url_for, send_from_directory
from werkzeug.utils import secure_filename
from jsonschema import validate, ValidationError

from . import models
from . import decorators
from . import app
from .database import session
from .utils import upload_path


@app.route("/api/songs", methods=["GET"])
@decorators.accept("application/json")
def get_songs():
    """ Get a list of songs """

    # Get songs from the database
    songs = session.query(models.Song).order_by(models.Song.id).all()

    # Convert the songs list to JSON and return a response
    data = json.dumps([song.as_dictionary() for song in songs])
    print(data)
    return Response(data, 200, mimetype="application/json")


@app.route("/api/songs", methods=["POST"])
@decorators.require("application/json")
def post_songs():
	""" Upload new Songs """
	file_data = request.json
	print(file_data)

	#accepted format
	valid_format = {"type": "file", "properties": {"id": {"type": "integer"}}}

	song_id = file_data["file"]["id"]
	file = models.File(id = file_data["file"]["id"], name = file_data["file"]["filename"])

	#Verify received JSON
	if validate(file_data, valid_format):
		new_song = models.Song(id=song_id, song_file=file.id)
		session.add(new_song)
		session.commit()

		message = "Successfully added song with id {}.".format(song_id)
		data = json.dumps("message", message)
		return Response(data, 200, mimetype="application/json")

	ValidationError("Request must contain {} data".format(mimetype))
	data = json.dumps("message", ValidationError)
	return Response (data, 415, mimetype="application/json")


@app.route("/uploads/<filename>", methods=["GET"])
def uploaded_file(filename):
    return send_from_directory(upload_path(), filename)


@app.route("/api/files", methods=["POST"])
@decorators.require("multipart/form-data")
@decorators.accept("application/json")
def file_post():
    file = request.files.get("file")
    if not file:
        data = {"message": "Could not find file data"}
        return Response(json.dumps(data), 422, mimetype="application/json")

    filename = secure_filename(file.name)
    db_file = models.File(name=filename)
    session.add(db_file)
    session.commit()
    file.save(upload_path(filename))

    data = db_file.as_dictionary()
    print(data)
    return Response(json.dumps(data), 201, mimetype="application/json")


