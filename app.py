#draft
from models import db, jobs
from flask import Flask, render_template, request, redirect
import subprocess
import glob
import os
# from flask.ext.uploads import UploadSet, configure_uploads, patch_request_class, ALL

app = Flask(__name__)

pyritpath = '/usr/bin/pyrit'
capdir = 'data/cap/*'

app.config['UPLOADED_FILES_DEST'] = 'data/cap/'



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
	joblist = db.session.query(jobs).all()
	return joblist

def get_percent(current, total):
	result = int(current) * 100 / int(total)
	return result

def divide_millions(number):
	number = 1.0 * number / 1000000
	return str(number) + 'M'


def jobize(msg, percent, job_type):
	try:
		#need a worker!!!
		# job_exists = jobs.query.filter_by(jobtype='').first()
		# if not job_exists:
		j = jobs('', 'Test', msg, percent, job_type)
		db.session.add(j)
		db.session.commit()

		# return 0
	except:
		raise

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
		    	update_job('Running...', get_percent(currentWU, totalWU), 10)
	except:
		raise


@app.route("/")
def main():
    return render_template('home.html', dicos=get_dics(), essids=get_essids(), capfiles=get_capfiles(), joblist=get_jobs())


@app.route('/create_essid', methods = ['POST'])
def signup():
	if request.method == 'POST':
	    essid_name = request.form['essid-name']
	    jobize('ESSID ' + str(essid_name) + ' Created.', 100, 3)
	    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
