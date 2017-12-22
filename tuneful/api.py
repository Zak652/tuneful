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
    return Response(data, 200, mimetype="application/json")

@app.route("/api/songs", methods=["POST"])
@decorators.require("application/json")
def post_songs():
	""" Upload new Songs """
	new_song = json.loads(request.json)

	#accepted format
	valid_format = {"type": "file", "properties": {"id": {"type": "integer"}}}

	song_id = new_song["id"]
	file_id = session.query(models.Files).order_by(models.Files.id)

	#Verify received JSON
	if validate(new_song, valid_format):
		if song_id == file_id:
			new_song = models.Song(id=song_id,file=file_id)
			session.add(new_song)
			session.commit()

			message = "Successfully added song with id {}.".format(song_id)
			data = json.dumps("message", message)
			return Response(data, 200, mimetype="application/json")

	ValidationError("Request must contain {} data".format(mimetype))
	data = json.dumps("message", ValidationError)
	return Response (data, 415, mimetype="application/json")
