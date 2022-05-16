#!/usr/bin/env python3

from pandas import DataFrame
import io, os
from flask import Flask, render_template, request, Response, flash,url_for,redirect
#local import
from qrfunc import decodeqr

app = Flask(__name__, template_folder = "./HTML", static_folder="./Static")


UPLOAD_FOLDER = './Uploads/'

app.secret_key = b"health_predictor"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


@app.route("/")
def mainpage():
    return render_template('main.html')
    
@app.route("/diab_intro")  #help before diab form
def diab_intro():
    return render_template('diab_intro.html')

@app.route("/cardio_intro")
def cardio_intro():
    return render_template('cardio_intro.html')
    #goes to route /cardio/<mode> where mode is form or qr.

@app.route("/diab_form")  #actual diab form
def diab_form():
    return render_template('diab_form.html')

#This route can take either a form or a qr upload
@app.route("/cardio/<mode>")  
def cardio_form(mode):
    if (mode == "form"):  #show entry form
        return render_template('cardio_form.html')
    elif (mode == "qr"): #show qr code upload form
        return render_template('qr_form.html', error_msg = "", 
        condition = 'cardiovascular', action = '/proc_cardio')

def predict_cardio(param_dict):
    #Process dict parameters and predict probability of disease using ML model
    #get all form values
    age = int(float(param_dict['age'])*365.25)  #age in days.
    #age is entered in years but is required in days.
    height = int(param_dict['height'])
    weight = int(param_dict['weight'])
    ap_hi = int(param_dict['sbp'])
    ap_lo = int(param_dict['dbp'])
    '''
    Total cholesterol range(in mg/dL):
    <=19 Yrs.: <170 Normal; >=170 & <=199 Borderline; >199 High
    >19 Yrs. : >=125 & <=200 Normal; >200 & <239 Borderline; >=239 High
    Value of variable chol is set 1, 2, or 3 based corresponding to
    Normal, Borderline and High.
    '''        
    chol_tmp = int(param_dict['chol']) #value in mg/dL
    if age <= 19:
        if chol_tmp < 170:
            chol = 1
        elif chol_tmp > 199:
            chol = 3
        else:
            chol = 2
    else:
        if chol_tmp <= 200:
            chol = 1
        elif chol_tmp >= 239:
            chol = 3
        else:
            chol = 2
    
    #Create a test df with this data.
    testdf = DataFrame([[age, height, weight, ap_hi, ap_lo, chol]])
    testdf.columns = ['age','height','weight','ap_hi','ap_lo','cholesterol']
    #Now predict the probability based on these values.
    result = round(clf_cardio.predict_proba(testdf)[0][1],2)*100 # heirarchical list
    result = int(result)  #remove the decimal point
    return result         #probability of incidence

@app.route("/proc_cardio", methods=["POST"])
def proc_cardio():
    #Sequence of features: age, height, weight, ap_hi, ap_lo, cholesterol
    error  = None

    if (request.form.get('mode','form') == 'qr'):  #request is from qrform upload
        f = request.files['qrfile']
        fqfn = os.path.join(UPLOAD_FOLDER+f.filename)
        f.save(fqfn)
        try:
            decoded_dict = decodeqr(fqfn)
        except:
            print("QR decode failed.")
            return render_template('qr_form.html', 
            error_msg = '''Unable to recognise QR code! <br/>Try again or use the 
            <a href="/cardio/form"><b>form</b></a>.''',
            condition = 'cardiovascular', action = '/proc_cardio')  # return the qr upload form again

        result = predict_cardio(decoded_dict)
    else: #request is from regular form
        result = predict_cardio(request.form)
        
    return render_template('result.html', disease = 'cardiovascular', prob = result)

@app.route("/proc_diab", methods=["GET","POST"])
def proc_diab():
    error = None
    if request.method == 'POST':
        #get all form values    
        frm_glucose = int(request.form['glucose'])
        frm_age = int(request.form['age'])
        frm_chol = int(request.form['chol'])
        frm_hdlchol = int(request.form['hdlchol'])
        frm_sbp = int(request.form['sbp'])
        frm_weight = int(request.form['weight'])
        frm_height = int(request.form['height'])
        frm_waist = int(request.form['waist'])
        
        #Process all form values e.g. cm to inches etc. 
        glucose = frm_glucose 
        age = frm_age
        systolic_bp = frm_sbp
        chol_hdl_ratio = frm_chol/frm_hdlchol
        bmi = frm_weight/(frm_height/100)**2
        cholesterol = frm_chol
        waist = frm_waist/2.54  #has to be in inches
        weight = frm_weight*2.2 #convert kg to pounds
        
        #Create a test df with this data.        
        testdf = DataFrame([[glucose, age, systolic_bp, chol_hdl_ratio, bmi, cholesterol,waist, weight]])
        testdf.columns = ['glucose', 'age', 'systolic_bp', 'chol_hdl_ratio', 'bmi', 'cholesterol','waist', 'weight']
        #Now predict the probability based on these values.
        result = round(clf_diab.predict_proba(testdf)[0][1],2)*100 # heirarchical list
        result = int(result)  #remove the decimal point
        
    return render_template('result.html', disease = 'diabetic', prob = result)


@app.route("/disclaimer")
def result():
    return render_template('disclaimer.html')    

if __name__ == "__main__":
    #Read the cardio prediction model
    import pickle
    global clf_cardio, clf_diab  #This model has to be accessible from the route function.
    #rehydrate the stored models.
    clf_cardio = pickle.load(open("./Models/cardio_model_rf.pkl","rb"))
    clf_diab = pickle.load(open("./Models/diab_model_rf.pkl","rb"))
    app.run(host = "0.0.0.0", port = 8080)
    exit() 
    

