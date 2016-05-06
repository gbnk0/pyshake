from config import app, db
from models import jobs
from flask import Flask, render_template, request, redirect
import subprocess
import glob
import os
from config import pyrit_path, cap_path



#DICTIONNARY FILE 
class dictobj():

    def __init__(self):
        self.path = ''
        self.name = ''


#ESSID (Access point) 
class essidobj():

    def __init__(self):
	self.path = ''
	self.name = ''
	self.capath = ''
	self.bssid = ''

    def start_processing(self):
        try:
            cmd = [pyrit_path, '-e', self.name, 'batch']
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      universal_newlines=True)
            while p.poll() is None:
                line = p.stdout.readline()
                if 'workunits' in line:
                    print "*** DEBUG ***"
                    totalWU = line.split(' ')[1].split('/')[1]
                    currentWU = line.split(' ')[1].split('/')[0]
                    jobize('Running...', get_percent(currentWU, totalWU), 10)
                else :
                    jobize('Finished', 100, 10)
        except:
            raise


#CAPTURE FILE (containing the handshake) 
class capfileobj():

    def __init__(self):
    	self.path = ''
    	self.name = ''



#DICTIONNARY IMPORTATION FUNCTION
def import_dict(dictpath):
    cmd = [pyrit_path, '-i', dictpath, 'import_passwords']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              universal_newlines=True)
    while p.poll() is None:
        line = p.stdout.readline()
        if 'read' in line:
            print line.split(' ')[0]


#LIST ALL DICTIONNARY FILES IN DATA/DICTS/ AND RETURN A LIST
def get_dics():
    dicos = glob.glob("data/dicts/*")
    diclist = []
    for dico in dicos:
    	curdict = dictobj()
    	curdict.name = os.path.basename(dico)
    	curdict.path = dico
    	diclist.append(curdict)
    return diclist


#LIST ALL ESSID CREATED IN PYRIT BY EXECUTING "pyrit eval"
def get_essids():
    cmd = [pyrit_path, 'eval']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
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


#RETURN ALL HANDSHAKES CONAINED ON THE SPECIFIED CAPTURE FILE
def get_handshakes(capfile):
    cmd = [pyrit_path, '-r', capfile.path ,'analyze']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
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


#LIST ALL CAPTURE FILES IN THE CAP FOLDER
def get_capfiles():
    files = glob.glob(cap_path + '*')
    results = []
    for file in files:
        curfile = capfileobj()
        curfile.name = os.path.basename(file)
        curfile.path = file
        results.append(curfile)
    
    return results


#LIST ALL JOBS IN THE SQLITE DB
def get_jobs():
    joblist = db.session.query(jobs).all()
    return joblist


#RETURN PERCENT VALUE FORM TWO NUMBERS
def get_percent(current, total):
    result = int(current) * 100 / int(total)
    return result


def divide_millions(number):
    number = 1.0 * number / 1000000
    return str(number) + 'M'


#CREATE JOBS
def jobize(msg, percent, job_type):
    try:
        # job_exists = jobs.query.filter_by(jobtype='').first()
        # if not job_exists:
        j = jobs('Test', msg, percent, job_type, 0)
        db.session.add(j)
        db.session.commit()
        
        return 0
    except:
        raise


#PROCESS ALL PASSWORDS IMPORTED WITH ALL ESSID CREATED
def start_processing():
    try:
    	cmd = [pyrit_path, 'batch']
    	p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  universal_newlines=True)
    	while p.poll() is None:
    	    line = p.stdout.readline()
    	    if 'workunits' in line:
                print "*** DEBUG ***"
    	    	totalWU = line.split(' ')[1].split('/')[1]
    	    	currentWU = line.split(' ')[1].split('/')[0]
    	    	jobize('Running...', get_percent(currentWU, totalWU), 10)
            else :
    	        jobize('Finished', 100, 10)
    except:
    	raise


#CREATE ESSID FUNCTION
def create_essid(essid_name):
    cmd = [pyrit_path, '-e', essid_name, 'create_essid']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              universal_newlines=True)
    while p.poll() is None:
        line = p.stdout.readline()
        if 'Created' in line:
            jobize('ESSID ' + str(essid_name) + ' Created.', 100, 3)
            return True


#ROUTE FOR HOME
@app.route("/")
def main():
    return render_template('home.html', dicos=get_dics(),
                                        essids=get_essids(),
                                        capfiles=get_capfiles(),
                                        joblist=get_jobs())


#ROUTE FOR CREATING A NEW ESSID
@app.route('/create_essid', methods = ['POST'])
def signup():
    if request.method == 'POST':
        essid_name = request.form['essid-name']
        if create_essid(essid_name):
            return redirect('/')


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
