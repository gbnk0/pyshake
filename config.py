#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ConfigParser import SafeConfigParser
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


parser = SafeConfigParser()
parser.read('pyshake.conf')

try:
    db_path = parser.get('General', 'db_path')
    db_file = parser.get('General', 'db_file')
    pyrit_path = parser.get('General', 'pyrit_path')
    cap_path = parser.get('General', 'cap_path')
    debug = parser.getboolean('General', 'debug')
except:
    raise
    

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path + db_file

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['CAPFILES_DEST'] = cap_path

db = SQLAlchemy(app)

s = db.session


# import logging

# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)