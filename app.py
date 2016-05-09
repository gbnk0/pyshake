#!/usr/bin/env python
# -*- coding: utf-8 -*-

from models import jobs
from flask import Flask, render_template, request, redirect
import subprocess
import glob
import os
from config import app, db, s
from config import pyrit_path, cap_path
from threading import Thread


#DICTIONNARY FILE 
class dictobj():

    def __init__(self):
        self.path = ''
        self.name = ''


#ESSID (Access point) 
class essidobj():

    def __init__(self):
    	self.name = ''
        self.percent = 0.00
    	self.capath = ''
    	self.bssid = ''
        self.isprocessing = False


    #PROCESS ALL PASSWORDS WITH CURRENT ESSID
    def process(self):
        try:
            cmd = [pyrit_path, '-e', self.name, 'batch']
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      universal_newlines=True)

            job_id = jobize('BATCH', 'Processing ' + self.name + '...', 0, 10, 0)

            while p.poll() is None:
                line = p.stdout.readline()
                if 'workunits' and 'far' in line:
                    print "*** DEBUG ***"

                    totalWU = line.split(' ')[1].split('/')[1]
                    currentWU = line.split(' ')[1].split('/')[0]
                    jobize('BATCH', 'Processing ' + self.name + '...', get_percent(currentWU, totalWU), 10, job_id)
                    
                    print job_id
            try:
                p.terminate()
                p.communicate()

            except:
                pass

            jobize('BATCH', 'Finished processing ' + self.name, 100, 10, job_id)
            return True
        except:
            raise


    #CREATE ESSID 
    def delete(self):
        cmd = [pyrit_path, '-e', self.name, 'delete_essid']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  stdin=subprocess.PIPE,
                                  universal_newlines=True)
        p.stdin.write("y\n")
        while p.poll() is None:
            line = p.stdout.readline()
            if 'Deleted' in line:
                job_id = jobize('ESSID', 'ESSID ' + str(self.name) + ' Deleted successfully.', 100, 3, 0)
                return True


#CAPTURE FILE (containing the handshakes) 
class capfileobj():

    def __init__(self):
    	self.path = ''
    	self.name = ''
    
    #RETURN ALL HANDSHAKES CONAINED ON THE SPECIFIED CAPTURE FILE
    def cap_get_essids(self):
        cmd = [pyrit_path, '-r', self.path ,'analyze']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  universal_newlines=True)
        
        results = []
        while p.poll() is None:
            line = p.stdout.readline()
            if 'AccessPoint' in line:
                curessid = essidobj()
                curessid.name = line.split("'")[1]
                curessid.bssid = line.split(" ")[2]
                results.append(curessid)

        return results


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
    
    results = []
    while p.poll() is None:
        line = p.stdout.readline()
        if 'ESSID' in line:
            cur_essid = essidobj()
            cur_essid.name = line.split("'")[1]
            cur_essid.percent = line.split("(")[1].replace("%)\n","")
            results.append(cur_essid)
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
    joblist = s.query(jobs).filter(jobs.jobarchived == 0).all()
    return joblist


#RETURN PERCENT VALUE FORM TWO NUMBERS
def get_percent(current, total):
    result = int(current) * 100 / int(total)
    return result


def divide_millions(number):
    number = 1.0 * number / 1000000
    return str(number) + 'M'


#CREATE JOBS 
def jobize(jobname, msg, percent, job_type, jobid):
    try:
        job_id = 0
        job_exists = jobs.query.filter_by(jobid=jobid).filter_by(jobarchived=0).first()
        
        if job_type == 3:
            job_exists = False

        if not job_exists:
            j = jobs(jobname, msg, percent, job_type, 0)
            s.add(j)

            #ONLY FOR RETREIVING THE JOB ID BEFORE COMMITING TO THE DB
            s.flush()
            s.refresh(j)
            job_id = j.jobid

            s.commit()

        else:
            s.query(jobs).filter(jobs.jobid == jobid).update({'jobstate': percent})
            s.commit()

        if jobid == 0:
            return job_id
    except:
        raise


#CREATE ESSID 
def create_essid(essid_name):
    cmd = [pyrit_path, '-e', essid_name, 'create_essid']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              universal_newlines=True)
    while p.poll() is None:
        line = p.stdout.readline()
        if 'Created' in line:
            job_id = jobize('ESSID', 'ESSID ' + str(essid_name) + ' Created successfully.', 100, 3, 0)
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
def c_essid():
    if request.method == 'POST':
        essid_name = request.form['essid-name']
        if create_essid(essid_name):
            return redirect('/')


#ROUTE FOR batch process ESSID
@app.route('/process_essid/<essid_name>', methods = ['GET'])
def pr_essid(essid_name):
    if request.method == 'GET':
        ce = essidobj()
        ce.name = essid_name
        t = Thread(target=ce.process)
        t.start()
        return redirect('/')


#ROUTE FOR batch process ESSID
@app.route('/delete_essid/<essid_name>', methods = ['GET'])
def del_essid(essid_name):
    if request.method == 'GET':
        ce = essidobj()
        ce.name = essid_name
        ce.delete()
        return redirect('/')


#ROUTE FOR ARCHIVING JOB
@app.route('/archive_job/<job_id>', methods = ['GET'])
def archive_job(job_id):
    if request.method == 'GET':
        try:
            s.query(jobs).filter(jobs.jobid == job_id).filter(jobs.jobstate == 100).update({'jobarchived': 1})
            s.commit()
        except:
            raise
        return redirect('/')


#ROUTE FOR UPLOADING CAP FILES
@app.route('/upload_cap', methods=['POST'])
def upload():
    try:
        uploaded_files = request.files.getlist("capfiles[]")
        filenames = []
        for file in uploaded_files:
            if file:
                file.save(os.path.join(app.config['CAPFILES_DEST'], file.filename))
                filenames.append(file.filename)
        # return render_template('upload.html', filenames=filenames)
        jobize('FILES', str(len(filenames)) + ' file(s) uploaded sucessfully', 100, 5)
        return redirect('/')
    except:
        raise

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
