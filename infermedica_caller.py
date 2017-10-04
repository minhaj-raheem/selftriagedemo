import json

def get_symptomids(symptomnames,gender):
    s_list = symptomnames.split(",")
    s_ids = ''
    
    s_list = symptomnames.split(",")
    #print(s_list)
    s_ids = []

    if gender == 'male':
        filename = "static/data/symptoms_male.json"
    else :
        filename = "static/data/symptoms_female.json"

    json_data = open(filename).read()

    data = json.loads(json_data)

    for symptom in s_list:
        symptom = symptom.replace(" ~ ",",")
        symptom_id = [x['id'] for x in data if x['name'] == symptom]
        s_ids.append(symptom_id[0])
    
    return s_ids

def get_symptom_names(s_ids,gender):
   
    

    if gender == 'male':
        filename = "static/data/symptoms_male.json"
    else :
        filename = "static/data/symptoms_female.json"

    json_data = open(filename).read()

    data = json.loads(json_data)
    symptom_names = []
    for symptom_id in s_ids:
        symptom_name = [x['name'] for x in data if x['id'] == symptom_id]
      
        symptom_names.append(symptom_name[0])
        
    return symptom_names

def ifm_template_builder(response,type):
     import decimal
     import urllib 
     
     if(type == "conditions"):
        json_condition = response['conditions']
        #json_condition = [x for x in json_condition if json_condition['probability']>=0.5]
        html ='<div class="valign-wrapper" style="width:100%;height:100%;position: absolute;">'
        html+='<div class="valign" style="width:100%;">'
        html+='<div class="container">'
        html+='<div class="row">'
        html+='<div class="col s12 m6 offset-m3">'
        html+='<div class="card blue-grey darken-1">'
        html+='<div class="card-content white-text">'
        html+='<span class="card-title">Possible Conditions</span>'
        #html+='<div class="col s12">'
        for item in json_condition:
       
       
           diagnosis_id = item['id']
           diagnosis_name = item['name']
           probability = item['probability']
           percent_chance = round(decimal.Decimal(probability * 100.00),2)
           html+='<p>'+diagnosis_name+" ("+str(percent_chance)+" % chance)"+'</p>'
           #print(diagnosis_id)
           #print('  '+diagnosis_name+'  '+str(percent_chance)+' % chance')

        #html+='</div>'
        html+='</div>'
        html+='</div>'
        html+='</div>'
        html+='</div>'
        html+='</div>'
        html+='</div>'
        html+='</div>'
        #get daiagnosis
        return html
     elif(type=="questions"):
            html =''
            #html+='<div class="card card-1">'
            html+='<form action="\qsubmit" method="post">'
            html+='<card>'
            json_questions = response['question']

            question = json_questions['text']
            question_type = json_questions['type']

            #print('Q : ',question  )
           
            html+='<h5 class="cyan-text text-darken-4" style="font-weight:bold;display="inline-block">'+question+'</h5>'
            if question_type == 'single':
                items = json_questions['items']
                symptom_id = items[0]['id']
                #print(symptom_id , ": is the symtom related to question")
                choices = items[0]['choices']
                #print('radio')
                i=1
                for options in choices:
                    id = options['id']
                    label = options['label']
                   
                    html+= '<input class="teal-text text-darken-4" name="rb_sing" id="rb_'+str(i)+'" type="radio" value="'+id+'"/>'
                    html+='<label style="padding-right:10px;" class="with-gap teal-text text-darken-4" for="rb_'+str(i)+'">'+label+'</label>'
                    i+=1
                  
                html+='<input type="hidden" name="questiontype" value="'+question_type+'">'
                html+='<input type="hidden" name="optioncount" value="'+str(i)+'">'
                html+='<input type="hidden" name="symptom_id" value="'+symptom_id+'">'
            elif  question_type == 'group_single':
                items = json_questions['items']
                items = json_questions['items']
                i = 0
                html+='<div id="q">'
                for item in items:

                    symptom_id = item['id']
                    name = item['name']
                 
                    html+= '<input class="teal-text text-darken-4" name="rb_mul" id="rb_'+str(i)+'" type="radio" value="'+symptom_id+'"/>'
                    html+='<label class="with-gap teal-text text-darken-4" style="padding-right:10px;" for="rb_'+str(i)+'">'+name+'</label>'
                    i+=1
                html += '</div>'
                html+='<input type="hidden" name="questiontype" value="'+question_type+'">'
                html+='<input type="hidden" name="optioncount" value="'+str(i)+'">'
                html+='<input type="hidden" name="symptom_id" value="'+symptom_id+'">'
            elif question_type == 'group_multiple':
                items = json_questions['items']
                #print(items)
                j=1
                i=1
                question_count = 0
                for item in items:
                    
                    symptom_id = item['id']
                    name = item['name']
                    choices = item['choices']
                 
                    #print('radio')
                    #html+='<h5 class="teal-text text-darken-4">'+name+'</h5>'
                    html+='<input type="hidden" name="txt'+str(i)+'" value="'+symptom_id+'">'
                    html+= '<input name="rb'+str(i)+'" class="with-gap teal-text text-darken-4" id="rb_'+str(j)+'" type="checkbox" value="present"/>'
                    html+='<label class="with-gap teal-text text-darken-4" style="padding-right:10px;"  for="rb_'+str(j)+'">'+name+'</label>'
                    j+=1   
                    #for options in choices:
                    #    id = options['id']
                    #    label = options['label']
                      
                    #    html+= '<input name="rb'+str(i)+'" class="with-gap teal-text text-darken-4" id="rb_'+str(j)+'" type="checkbox" value="'+id+'"/>'
                    #    html+='<label class="with-gap teal-text text-darken-4" style="padding-right:10px;"  for="rb_'+str(j)+'">'+label+'</label>'
                    #    j+=1   
                    i+=1
                    question_count +=1
                html+='<input type="hidden" name="questiontype" value="'+question_type+'">'
                html+='<input type="hidden" name="optioncount" value="'+str(question_count)+'">'
                #html+='<input type="hidden" name="symptom_id" value="'+symptom_id+'">'
            html+='<div class="card-action" style="bottom:0px;position:unset"><br/>'
            html+='<input type="submit" class="btn" value="Next">'
            html+='</div>'
            html+='</card>'
            html+='</form>'
            #html+='</div>'
            #html+='</div>'
            
           
            return html


    

    