from pathlib import Path
import hashlib
import os

from flask import current_app, g
from .models import db, files

def store(file_id, blob, store_path):
    Path(store_path).mkdir(parents=True, exist_ok=True) 
    store_id = hashlib.sha256().update(blob).hexdigest()
    
    db.session.add(files(field_id, store_id, store_path))
    
    with open(os.path.join(current_app.instance_path, store_path, store_id), "w") as file:
        file.write(blob)
       