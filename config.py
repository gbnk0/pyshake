from ConfigParser import SafeConfigParser
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

parser = SafeConfigParser()
parser.read('pyshake.conf')

db_path = parser.get('General', 'db_path')
db_file = parser.get('General', 'db_file')
pyrit_path = parser.get('General', 'pyrit_path')
cap_path = parser.get('General', 'cap_path')


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path + db_file

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['UPLOADED_FILES_DEST'] = cap_path

db = SQLAlchemy(app)

s = db.session