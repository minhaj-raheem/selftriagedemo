import flask
from flask import Flask, render_template, request, redirect, jsonify,url_for,session

import random
import string
import logging
import json
import httplib2
import requests
from flask import make_response
import json
import pickle
from infermedica_caller import get_symptomids,ifm_template_builder,get_symptom_names
import infermedica_api
import decimal

app = Flask(__name__)

global age,gender,symptom_names;
global api 

api = infermedica_api.API(app_id='244d1371', app_key='d38856ca38926ed251d7d49615faa3b9')

def process_question(response):
    '''This function processes the response and returns the possible
        questions as a dictionary
    '''
   
    qs = [response['question']]
   
    questions = [q for q in qs]
   
    return questions


def process_conditions(response):
    '''This function processes the response and returns the possible
        conditions as a dictionary
    '''
    from operator import itemgetter
    
    conditions = response['conditions']

    best_match = [i for i in conditions if i['probability']>=0.5]
    best_match_sorted = sorted(best_match, key=itemgetter('probability'),reverse=True)
    has_conditions = False
    top_2 =[]
    if len(best_match_sorted )>=1:
        print("Condtidions Obtained")
        has_conditions = True
        top_2 = best_match_sorted[:2]
        print(top_2[0])
        
    condition_list = []
    
    for tags in top_2:
        id = tags['id']
        prob = tags['probability']
        with open('static/data/conditions.json') as cond:
            c_detail = json.loads(cond.read())

        c_detail = [x for x in c_detail if x['id']==id][0]
        c_detail['perc'] = round(decimal.Decimal(prob * 100.00),2)
        condition_list.append(c_detail)
    if has_conditions == True and len(condition_list)>1:
        if(condition_list[0]['triage_level']=='self_care' or condition_list[0]['triage_level']=='consultation' ) and \
                condition_list[1]['triage_level']=='emergency':
                temp = condition_list[0]
                condition_list[0] = condition_list[1]
                condition_list[1] = temp
    return condition_list,has_conditions


@app.route('/search_symptoms', methods=['GET', 'POST'])
def search_symptoms():
	if request.method == 'POST':
		print("POST request")
	else:
		print("GET request")

	with open('static/data/male_minified.json', encoding='utf-8') as data_file:
               data = json.loads(data_file.read())
	resource_list = data
	return jsonify(resource_list=resource_list)

# ** Example 4 ** 

# Route to home page
@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def show_home():
    if request.method == 'GET':
        auth_status = False # On load since dob is null set auth_status to False
        age = ""
        gender = ""
    else :
        auth_status = True
        gender = request.form['rbgender']
        age = request.form['txtage']
        
    #commented for testing
    return render_template('index.html',auth_status=auth_status,age=age,gender=gender)
    #return redirect(url_for('results'))


@app.route('/results', methods=['POST','GET'])
def results(): 
    
    req = flask.g
    
    if request.method == 'POST':

        print("First Request")
        age = request.form['age']
        gender = request.form['gender']
        symptom_names = request.form['txtsymptoms']
        
        s_ids = get_symptomids(symptom_names,gender)
        req = infermedica_api.Diagnosis(sex=None,age=None)

        #print("setting up session parameters")
        req.patient_age = age
        req.patient_sex = gender
        for symptom in s_ids:
            
            req.add_symptom(symptom,'present')
           
        flask.g = req
        req = api.diagnosis(req)
        response = req
        #with open("static/data/testresponse.json",encoding='utf-8') as input_file:
        #    response = json.loads(input_file.read())
       
        
    else:
        #print("SECOND Request")
        req = flask.g
        req = api.diagnosis(req)
        flask.g = req
        
    
       
    ###Test Values
    #req.patient_age = 20
    #req.patient_sex = 'male'
    response = json.loads(req.to_json())
    #with open("static/data/testresponse.json",encoding='utf-8') as input_file:
    #  response = json.loads(input_file.read())
  
    q_tags = ifm_template_builder(response,'questions') #process_question(response)
    
    condition_tags,has_condition = process_conditions(response)
    print("possbile Conditions")
    print(condition_tags)
    cond1 = ""
    cond2 = ""
    patient_advice = ""
    if has_condition:
        if(len(condition_tags)>=2):
            cond1 = condition_tags[0]
            cond2 = condition_tags[1]
        else :
            cond1 = condition_tags[0]
        print(cond1)
        patient_advice =  cond1['extras']['hint']
    print(patient_advice)
    all_sids = [s['id'] for s in response['symptoms']]
 
    
    #symptom_names = get_symptom_names(all_sids,req.patient_sex )
    info_collected = True
    auth_status = True
    
    
    return render_template('index.html',age=req.patient_age,gender=req.patient_sex,auth_status=auth_status,info_collected=info_collected,\
                           questions=q_tags,cond1=cond1,cond2=cond2,has_conditions=has_condition,advice = patient_advice )
    

@app.route('/qsubmit', methods=['POST'])
def qsubmit(): 
    
    n_options = int(request.form['optioncount'])
    
    question_type = request.form['questiontype']
    
    req = flask.g
    
    
    if question_type == 'single' :
        
        symptom_id = request.form['symptom_id']
        
       
        value = request.form['rb_sing']
        
        req.add_symptom(symptom_id,value)
        
    elif question_type=='group_single':
        
        symptom_id = request.form['rb_mul']
        
        
        req.add_symptom(symptom_id,'present')

    elif question_type == 'group_multiple':
        for i in range(1,n_options+1):
            rb_name = 'rb'+str(i)
            txt_name = 'txt'+str(i)
            print("Recieved Request is : ")
            print(request.form)
            print(rb_name)
            try :
                value = request.form[rb_name]
            except :
                value = "absent"
                pass
            symptom_id = request.form[txt_name]

            
            req.add_symptom(symptom_id,value)
        print("group multiple request is :")
        print(req)
    flask.g = req
  
    return redirect(url_for('results'))


# Main Method
#if __name__ == '__main__':
app.secret_key = 'super_secret_key'
    #app.debug = True
    #app.run(host='127.0.0.1', port=5000)
