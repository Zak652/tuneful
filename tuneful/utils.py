import os.path

from . import app

def upload_path(name=""):
    return os.path.join(app.root_path, app.config["UPLOAD_FOLDER"], name)
