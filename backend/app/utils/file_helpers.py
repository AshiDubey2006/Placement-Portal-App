from flask import request
from werkzeug.utils import secure_filename
import os

def allowed_file(filename, allowed_extensions):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_file(file, upload_folder, allowed_extensions):
    """Save uploaded file to upload folder"""
    if file and allowed_file(file.filename, allowed_extensions):
        filename = secure_filename(file.filename)
        # Add timestamp to filename to make it unique
        import time
        timestamp = str(int(time.time()))
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        return filename
    return None
