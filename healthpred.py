#!/usr/bin/env python3

import pandas as pd
import io
from flask import Flask, render_template, request, Response
app = Flask(__name__, template_folder = "./HTML", static_folder="./Static")

@app.route("/")
def mainpage():
    return render_template('main.html')
    
@app.route("/diab_intro")
def diab_intro():
    return render_template('diab_intro.html')

@app.route("/cardio_intro")
def cardio_intro():
    return render_template('cardio_intro.html')

@app.route("/diab_form")
def diab_form():
    return render_template('diab_form.html')

@app.route("/cardio_form")
def cardio_form():
    return render_template('cardio_form.html')

@app.route("/proc_cardio", methods=["GET","POST"])
def proc_cardio():
    #Sequence of features: age, height, weight, ap_hi, ap_lo, cholesterol
    error  = None
    if request.method == 'POST':
        #get all form values
        age = int(float(request.form['age'])*365.25)  #age in days.
        #age is entered in years but is required in days.
        height = int(request.form['height'])
        weight = int(request.form['weight'])
        ap_hi = int(request.form['sbp'])
        ap_lo = int(request.form['dbp'])
        '''
        Total cholesterol range(in mg/dL):
        <=19 Yrs.: <170 Normal; >=170 & <=199 Borderline; >199 High
        >19 Yrs. : >=125 & <=200 Normal; >200 & <239 Borderline; >=239 High
        Value of variable chol is set 1, 2, or 3 based corresponding to
        Normal, Borderline and High.
        '''        
        chol_tmp = int(request.form['chol']) #value in mg/dL
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
        testdf = pd.DataFrame([[age, height, weight, ap_hi, ap_lo, chol]])
        testdf.columns = ['age','height','weight','ap_hi','ap_lo','cholesterol']
        #Now predict the probability based on these values.
        result = round(clf_cardio.predict_proba(testdf)[0][1],2)*100 # heirarchical list
        result = int(result)  #remove the decimal point

    
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
        testdf = pd.DataFrame([[glucose, age, systolic_bp, chol_hdl_ratio, bmi, cholesterol,waist, weight]])
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
    

