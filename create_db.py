import os
from models import db
from config import db_path

if not os.path.isdir(db_path):
    os.makedirs(db_path)
    db.create_all()