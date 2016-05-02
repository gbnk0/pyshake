from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)


class jobs(db.Model):
    jobid = db.Column(db.Integer, autoincrement = True, primary_key=True)
    jobname = db.Column(db.String)
    jobmsg = db.Column(db.String)
    jobstate = db.Column(db.Integer)
    jobtype = db.Column(db.Integer)

    def __init__(self, jobid, jobtype):
        self.id = jobid
        self.type = jobtype