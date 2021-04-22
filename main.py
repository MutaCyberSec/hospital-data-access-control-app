from flask import Flask, render_template, url_for, request, redirect,flash
from flask_pymongo import PyMongo
import passlib
from passlib.context import CryptContext
from passlib.hash import argon2, bcrypt_sha256,argon2,ldap_salted_md5,md5_crypt


import time

import smtplib


import socket



app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'main_db'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/main_db'

mongo = PyMongo(app)

#HASH sCHEMES

Hash_passcode = CryptContext(schemes="sha256_crypt",sha256_crypt__min_rounds=131072)

 

username_hash = CryptContext(schemes=["sha256_crypt","argon2"])



#databases
users = mongo.db.emplyee
doctor_db = mongo.db.doctors
patient_db = mongo.db.patients
drug_db = mongo.db.drugs
nurse_db = mongo.db.nurses
patient_backup = mongo.db.patient_backup

@app.route('/patient', methods=['POST','GET'])
def patient():
    if request.method == 'POST':
        namein = request.form['patname']

        issued_patient = patient_backup.find_one({ 'name':namein})
        if issued_patient is not None:
            flash("Patient Found")

            
            drugs = issued_patient['Drugs_Prescribed']
            infecs = issued_patient['infections']
            timez = issued_patient['Time']
            id_no = issued_patient['id_no']

            return render_template('patient.html',ti = timez,d = drugs,name = namein,
            infects = infecs,ide = id_no,h1 = "   PATIENT NAME : ",h2 = "DRUGS ISSUED",
            h3 = "FORMER INFECTIONS",h4 ="TIME : " )

    
    return render_template('patient.html')

@app.route('/doctor', methods=['POST','GET'])
def doctor():

    
    if request.method == 'POST':

        name = request.form['name']
        id_no = request.form['id']
        infec1 = request.form['infec1']
        infec2 = request.form['infec2']
        infec3 = request.form['infec3']
        drug_presc1 = request.form['drug_presc1']
        drug_presc2 = request.form['drug_presc2']
        drug_presc3 = request.form['drug_presc3']
        drug_presc4 = request.form['drug_presc4']

        patient_db.insert_one({'name':name,'id_no':id_no,'infections':[infec1,infec2,infec3],'Drug_Prescribed':[drug_presc1,drug_presc2,drug_presc3,drug_presc4]})
        time.sleep(5)
        flash("user added")
        if patient_db.find_one({'name':name}):
            flash('Patient Information Updated')

            drug_db.insert_one({'name':name,'Drugs_Prescribed':[drug_presc1,drug_presc2,drug_presc3,drug_presc4]})
            login_time = time.asctime( time.localtime(time.time()) )
            patient_backup.insert_one({ 'Time':login_time,'name':name,'Drugs_Prescribed':[drug_presc1,drug_presc2,drug_presc3,drug_presc4], 'id_no':id_no,'infections':[infec1,infec2,infec3] })
            
    
    return render_template('PatientInfo.html')
    
@app.route('/searchPatient' ,methods = ['POST','GET'])
def searchPatient():
    if request.method == "POST":

        name_in = request.form['search']


        in_serach = patient_db.find_one({'name':name_in})

        drug_arr= in_serach['Drug_prescribed']

        infe_arr= in_serach['infections']

    return render_template('searchPatient.html', )



@app.route('/chemist', methods=['POST','GET'])
def chemist():
    if request.method == 'POST':
        namein = request.form['patname']

        issued_patient = drug_db.find_one({ 'name':namein})
        if issued_patient is not None:
            flash("Patient Found")

            
            drugs = issued_patient['Drugs_Prescribed']

            return render_template('chemist.html',d = drugs,name = namein,h1 = "   PATIENT NAME : ",h2 = "DRUGS ISSUED")





    return render_template('chemist.html')



def send_mail(email,recipient):


    from_ = "jacksonmuta123@gmail.com"

    mail_info  = ""
    
    sender = "From : jacksonmuta123@gmail.com"
    subject = "Subject : Change Password"
    messo = "message : " + email
    to_ = recipient

    
    
    try:
        smtpObj = smtplib.SMTP(socket.gethostbyname(socket.gethostname()))
        #smtpObj = smtplib.SMTP("smtp.gmail.com" , 999)
        smtpObj.sendmail(from_,recipient,mail_info)
        flash("Mail Sent,Await Rensponse Please")
    except smtplib.SMTPException:
        flash("Error Sending E-mail,Please Retry Or Fix Any Warning From A Browser")
    



@app.route('/',methods=['POST','GET'])
def index():
    if request.method == 'POST':
        login_user = users.find_one({'name' : request.form['username']})
        
        if login_user['dep'] == 'doctor':
            
            return  redirect(url_for('doctor'))
        if login_user['dep'] == 'patient':
            
            return  redirect(url_for('patient'))
        if login_user['dep'] == 'chemist':
                
                return  redirect(url_for('chemist'))

    return render_template('index.html')

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        users = mongo.db.emplyee
    
        
        login_user = users.find_one({'name' : request.form['username']})
        dep = request.form['dep']
        if dep == "doctor":
            return redirect(url_for('doctor'))
        if dep ==  'patient':
            return redirect(url_for('patient'))
        if dep == 'chemist':
            return redirect(url_for('chemist'))
        if login_user:
            form_pass = request.form['pass'].encode('utf-8')
            hashed_pass = login_user['password']
                
            if Hash_passcode.verify(form_pass,login_user['password']):
                
                if login_user['dep'] == 'doctor':
                    return redirect(url_for('doctor'))
                if login_user['dep'] == 'patient':
                    return redirect(url_for('patient'))
                if login_user['dep'] == 'chemist':
                    return redirect(url_for('chemist'))

    return render_template('error.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.emplyee
        existing_user = users.find_one({'name' : request.form['username']})

        if existing_user is None:
            passcode = request.form['pass']
            dep = request.form['dep']
            email = request.form['email']
            hashpass = Hash_passcode.hash(passcode)
            users.insert_one({'name' : request.form['username'], 'password' : hashpass,'dep':dep,'email':email})
            return redirect(url_for('index'))
        
        return 'That username already exists!'

    return render_template('register.html')







if __name__ == '__main__':
    app.secret_key = 'private_tings'
    app.run(debug=True,port=5004)