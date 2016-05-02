from flask import Flask, render_template, request
import subprocess
import glob
import os
from flask.ext.uploads import UploadSet, configure_uploads, patch_request_class, ALL
from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import db, jobs

# Base = declarative_base()
app = Flask(__name__)

pyritpath = '/usr/bin/pyrit'
capdir = 'data/cap/*'

app.config['UPLOADED_FILES_DEST'] = 'data/cap/'
# engine = create_engine('sqlite:///db/database.db')

# session = sessionmaker()
# session.configure(bind=engine)
# Base.metadata.create_all(engine)

s = db.session()


# class jobs(Base):
# 	__tablename__ = 'jobs'
# 	jobid = Column(Integer, autoincrement = True, primary_key=True)
# 	jobname = Column(String)
# 	jobmsg = Column(String)
# 	jobstate = Column(Integer)
# 	jobtype = Column(Integer)

class dictobj():
	def __init__(self):
		self.path = ''
		self.name = ''

class essidobj():
	def __init__(self):
		self.path = ''
		self.name = ''
		self.capath = ''
		self.bssid = ''

class capfileobj():
	def __init__(self):
		self.path = ''
		self.name = ''


def import_dict(dictpath):
	cmd = [pyritpath, '-i', dictpath, 'import_passwords']
	p = subprocess.Popen(cmd,		stdout=subprocess.PIPE,
									stderr=subprocess.PIPE,
									universal_newlines=True)
	while p.poll() is None:
	    line = p.stdout.readline()
	    if 'read' in line:
	    	print line.split(' ')[0]


def get_dics():
	dicos = glob.glob("data/dicts/*")
	diclist = []
	for dico in dicos:
		curdict = dictobj()
		curdict.name = os.path.basename(dico)
		curdict.path = dico
		diclist.append(curdict)
	return diclist


def get_essids():
	cmd = [pyritpath, 'eval']
	p = subprocess.Popen(cmd,		stdout=subprocess.PIPE,
									stderr=subprocess.PIPE,
									universal_newlines=True)

	results = {}
	while p.poll() is None:
	    line = p.stdout.readline()
	    if 'ESSID' in line:
	    	essid = line.split("'")[1]
	    	percent = line.split("(")[1]
	    	results[essid] = percent.replace("%)\n","")

	return results


def get_handshakes(capfile):
	cmd = [pyritpath, '-r', capfile.path ,'analyze']
	p = subprocess.Popen(cmd,		stdout=subprocess.PIPE,
									stderr=subprocess.PIPE,
									universal_newlines=True)

	results = {}
	while p.poll() is None:
	    line = p.stdout.readline()
	    if 'AccessPoint' in line:
	    	essid = line.split("'")[1]
	    	mac = line.split(" ")[2]
	    	results[essid] = percent.replace("%)\n","")

	return results


def get_capfiles():
	files = glob.glob(capdir)
	results = []
	for file in files:
		curfile = capfileobj()
		curfile.name = os.path.basename(file)
		curfile.path = file
		results.append(curfile)

	return results


def get_jobs():
	joblist = s.query(jobs).all()
	return joblist

def get_percent(current, total):
	result = int(current) * 100 / int(total)
	return result

def divide_millions(number):
	number = 1.0 * number / 1000000
	return str(number) + 'M'


def update_job(job_type, msg, percent):
	jobi = s.query(jobs).filter_by(jobtype=job_type).first()
	if not jobi:
		j = jobs(jobname = 'Batch Processing',
				 jobmsg = msg, jobstate = percent,
				 jobtype=10)
		s.add(j)
	else:
		s.query().\
		       filter(jobs.jobtype == job_type).\
		       update({"jobmsg": (msg)})
		s.query().\
		       filter(jobs.jobtype == job_type).\
		       update({"jobstate": (percent)})
	s.commit()
	return 0


def start_processing():
	try:
		cmd = [pyritpath, 'batch']
		p = subprocess.Popen(cmd,		stdout=subprocess.PIPE,
										stderr=subprocess.PIPE,
										universal_newlines=True)
		while p.poll() is None:
		    line = p.stdout.readline()
		    if 'workunits' in line:
		    	totalWU = line.split(' ')[1].split('/')[1]
		    	currentWU = line.split(' ')[1].split('/')[0]
		    	update_job(10, 'Running...', get_percent(currentWU, totalWU))
	except:
		raise

@app.route("/")
def main():
    return render_template('home.html', dicos=get_dics(), essids=get_essids(), capfiles=get_capfiles(), joblist=get_jobs())


# @app.route('/upload', methods=['GET', 'POST'])
# def upload():
# 	if request.method == 'POST':
# 		file = request.files['capfile']
# 		if file:
# 			filename = file.filename
# 			file.save(os.path.join(app.config['UPLOADED_FILES_DEST'], filename))
# 	return render_template('upload.html')


if __name__ == "__main__":
    app.run(debug=True)
