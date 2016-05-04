from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import db_path

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

class jobs(db.Model):
    jobid = db.Column(db.Integer, autoincrement = True, primary_key=True)
    jobname = db.Column(db.String)
    jobmsg = db.Column(db.String)
    jobstate = db.Column(db.Integer)
    jobtype = db.Column(db.Integer)

    def __init__(self, jobid, jobname, jobmsg, jobstate, jobtype):
    	#self.jobid = jobid
        self.jobname = jobname
        self.jobmsg = jobmsg
        self.jobstate = jobstate
        self.jobtype = jobtype

        print "DEBUG : jobname: %s jobmsg: %s jobstate: %d jobtype: %d" % (jobname, jobmsg, jobstate, jobtype) 
