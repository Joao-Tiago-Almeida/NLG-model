from random import randrange
import random
import string
import re
import inflect
from Templates import temps
from ReportTemplate import report, dictionary, hyperlink, collapse
import operator

TAG_RE = re.compile(r'<br>|</b>')
p = inflect.engine()

def count_placeholders(fmt):
     count = 0
     L = string.Formatter().parse(fmt)
     for x in L:
         if x[1] is not None:
             count += 1
     return count

#Returns the plural form of a given word.
def pluralize_noun(noun):
    if(noun[-1:] == "y"):
        noun = noun[:-1]
        return str(noun) + "ies"
    else:
        return " the " + str(p.plural(noun))

def end_sentence():
    return ". "

'''Returns a final conjunction such as "as finally", "as lastly"'''
def final_conjunction():
    ind = randrange(len(temps["final_conj_cop"])) 
    return str(temps["final_conj_cop"][ind]) 
    
#Optional: Adds supergroup to the text.'''
def add_sg(data):
    tmp = random.uniform(0, 1)
    return " the " + str(data["super_group"]["name"]) if (tmp > 0.50) else ""

def pick_verb_person(n_corrs):
    return ["was",""] if n_corrs == 1 else ["were","s"]

'''---------------------------------------------------------------------------
s_or_p(Singular or Plural) 
returns an "s" or "p" depending if the number of element is singular or plural.
----------------------------------------------------------------------------'''
def s_or_p(arr):
    if isinstance(arr, list):
        if len(arr) != 1:
            return "s"
        return ""
    else:
        if isinstance(arr, int):
            if arr != 1:
                return "s"
            return ""     
   
'''converts array to string'''
def array_to_string(arr):
    string  = ""
    if arr is None:
        return string
    elif len(arr) > 0:
        for x in range(0,len(arr)-1):
            string += str(arr[x]) + ", "
        string += str(arr[len(arr) - 1])
        return string
    elif (len(arr) > 1):
        return arr[0]

'''Performs minor corrections on the text.'''
def check_ponctuation(text):
    r = [[": .",":"],[":.",":"],[": \n.",":\n"],[" ,",","],[" .","."],["\n","#"],["..","."],[". .",""],[" ."," "],[".</b>.",".</b>"],["..","."],[" .","."],[" ,",","]]
    for pair in r:
        text = text.replace(pair[0],pair[1])
    tmp = text.rstrip()
    if(tmp[-1:] != "."):
        text = text + "."
    return text

'''-----------------------------------------------------------------
Writes the text for the report and performs after the text is 
written a ponctuation check to make sure there are no mistakes.
-----------------------------------------------------------------'''
def write_final_text(data, df):

    R = report(data['super_group']['name'])

    R.generate_title()
    R.generate_terms_of_reference(data['timespan'])
    R.generate_introduction(data['intro'], list(data['super_group']['vals'].keys()))
    try: 
        R.generate_super_group_body(data)
        write_body_sg(data,R,df)
    except:
        R.add_text(write_body_no_sg(data))

    R.generate_general_body(data)
    R.generate_correlation(data)
    R.generate_draft()

    text = collapse(
        data['super_group']['name'],
        str(R),
        "Report",
        R.unique_sequence
        ) if len(data['super_group_bonus']) else str(R)

    return check_ponctuation(text)

def remove_tags(text):
    return TAG_RE.sub('', text)

def upcase_first_letter(s):
    return s[0].upper() + s[1:] if len(s) > 0 else s

def lower_first_letter(s):
    return s[0].lower() + s[1:] if len(s) > 0 else s
'''------------------------------------------------------------------------------
Performs ponctuation fixes on the text fragment that it is to be added.
text - Previous text until now.
new_text - New fragment to be added.
caps - Binary Flag. If True indicates that new_text should be altered
in order to start as the beginning of the sentence, if false, it should considered
as part of the last sentence from new_test.
------------------------------------------------------------------------------'''
def str_format(text,new_text,caps):
    if(caps):
        new_text = upcase_first_letter(new_text)
    else:
        new_text = lower_first_letter(new_text)

    pre_proc_text = remove_tags(text)
    processed_text = remove_tags(pre_proc_text).rstrip()

    if(len(new_text) > 0 and len(processed_text) > 0):
        if caps == True:
            new_text = upcase_first_letter(new_text.lstrip())
            pre_proc_text = pre_proc_text.lstrip()
            processed_text = processed_text.lstrip()
            if pre_proc_text[-1] not in [".",":",">"] and processed_text[-1] not in [".",":",">"]:
                return ". " + new_text
            else:
                return new_text
        else:    
            if(processed_text[-1] not in [".",":","\n"] and new_text[0] != "," ):
                return ", " + new_text
            elif(processed_text[-1] not in [".",":"]):
                return "." + new_text
            elif(processed_text[-1] == "."):
                return new_text.capitalize()
            elif(len(processed_text) == len(text) and text[-1] != " "):
                return " " + str(new_text)
    return new_text + ' '

'''--------------------------------------------------------------------
The goal of this function is to write better English. Cause although
the columns have already been classified, a better classification can
provide us more specific vocabulary for writting better words.
For example, if the NER "time" column is age and contains numbers:
it would be better to write "...which as 20 years..." instead of
"in 20 years...".

Receives the name of a column and a category. Categories are the NER cats:
->entity,time,location 
---------------------------------------------------------------------'''
def desambig_temp(name,cat,data):   
    if(cat == "time"):
        if ("age" in name.lower()):
            return "which has {} <b>{}</b>"

    #print("O valor que vou retornar do desambig_temp e: " + str(temps["maxmin_" + str(cat)][randrange(len(temps["maxmin_" + str(cat)]))]))
    if (str("maxmin_" +str(cat)) in temps.keys()):
        if(data["timespan"] != None):
            if(data["timespan"]["begin"] == data["timespan"]["end"]):
                return ""
            else:
                return temps["maxmin_" + str(cat)][randrange(len(temps["maxmin_" + str(cat)]))]
        else:
            return ""
    else:
        return ""

def add_maxmin(free_var,string,ner_classes,data):
    res = ""
    ind = randrange(len(temps[string]))  
    res += temps["maxmin_text"][0].format(temps[string][ind],free_var[string]["value"])

    #Adds entity,time,location max/min if it exists.
    for nc in ner_classes:
        if(free_var[nc] != {}):
            if(len(free_var[string][nc]) == 1):
                ner_vals = free_var[string][nc][0]
                cat = free_var[nc]
                
            else: #Case where there is more than 1 val for max/min
                ner_vals = ""
                for x in range(0,len(free_var[string][nc])):
                    ner_vals += add_copulative_conjunction(x,len(free_var[string][nc]))
                    ner_vals += str(free_var[string][nc][x])
                
                cat = pluralize_noun(free_var[nc])

            template = str_format(res,desambig_temp(cat,nc,data),False)
            res += template.format(cat,ner_vals)
    return res

def get_corr_word(val):
    val = float(val)
    if val > 0.90:
        return "very strong"
    elif val > 0.75:
        return "positive"
    elif val > -0.75:
        return "negative"    
    elif val > -2:              #Just to be safe... Although the value will never be lower than -1.
        return "very negative"

def add_no_corrs(text,corrs):
    ind = randrange(len(temps["no_corrs"])) 
    ind2 = randrange(len(temps["analysis"]))
    return '<h1 style="color:Fuchsia;">' + str_format(text,temps["no_corrs"][ind].format(temps["analysis"][ind2]),True) + '</h1>'
    
def add_corrs(text,corrs):
    new_text = ""
    if corrs == {}:
        return add_no_corrs(text,corrs)
    else:
        ind = randrange(len(temps["corrs_intro"])) 
        n_corrs = len(list(corrs.keys()))
        tmp = pick_verb_person(n_corrs)

        new_text += str_format(text,temps["corrs_intro"][ind].
        format(tmp[0],n_corrs,tmp[1]),True)

        for key in corrs.keys():
            val = corrs[key]["value"]
            word_val = get_corr_word(val)
            el1 = corrs[key]["1"]
            el2 = corrs[key]["2"]
            ind = randrange(len(temps["corr_val"])) 
            new_text += str(temps["corr_val"][ind].format(word_val,float(val),el1,el2)) 
        return new_text

def add_conjunction(text):
    text = text.lstrip()
    ind = randrange(len(temps["conj"]))  
    conj = temps["conj"][ind]
    return  conj.capitalize() if(text[:-1] == ".")  else conj

def add_copulative_conjunction(ind,length):
    if ind == 0:
        return ""
    elif ind != length -1:
        return ", "
    else:
        return " and "

'''------------------------------------------------------------------------
Returning example: 
"When it comes to the value Water" 
(for mammals.xlsx)
------------------------------------------------------------------------'''
def add_sg_val_intro(sg_val,old_text,sg):
    sg_ind = randrange(len(temps["sg"])) 
    word_intro = temps["sg_val_intro"][randrange(len(temps["sg_val_intro"]))] 
    if(count_placeholders(word_intro) == 1):
        word_intro = word_intro.format(sg)
    return str_format(old_text,temps["sg"][sg_ind].format(word_intro,sg_val),True)

def repeated_words(prev_tmp,actual_tmp):    
    prev_tmp = prev_tmp.split()
    actual_tmp = actual_tmp.split()
    
    for word1 in prev_tmp:
        for word2 in actual_tmp:
            if word1.lower() == word2.lower() and word1 in temps["sg_val_intro"]:
                return True
    return False

'''-----------------------------------------------------------------------------
Introduces new category. Ex: "Concerning  male maturity(d)"
data- Contains all info and relations.
text- Text until now.
cat- New category to be added to the text.
ind- Category Number (Is it the first, or second or third cat being written...)
------------------------------------------------------------------------------'''
def add_sg_cat(data,text,cat,ind):
    tmp = " "
    if(ind != 0):                    
        ind = randrange(len(temps["same_sg_val"]))
        verb = random.choice(temps["same_sg_verb"])
        str_tmp = temps["same_sg_val"][ind]

        n_phs = count_placeholders(str_tmp)
        if(n_phs == 2):
            tmp += str_format(tmp,temps["same_sg_val"][ind].format(verb,data["super_group"]["name"]),True)
        else:
            tmp += str_format(tmp,temps["same_sg_val"][ind].format(data["super_group"]["name"]),True)
        tmp += " but now "

    #Certain words like "to" or "for" do not work for fist category.
    word_intro = "to"
    while(word_intro == "to" or word_intro == "for"):
        i = randrange(len(temps["sg_val_var"]))
        word_intro = temps["sg_val_var"][i] 

    i = randrange(len(temps["sg_val"]))
    tmp += str_format(tmp,temps["sg_val"][i].format(word_intro,cat),False)
    return tmp
        

def intro_with_timespan(timespan):
    ind = randrange(len(temps["timespan"])) 
    return temps["timespan"][ind].format(timespan["begin"],timespan["end"])

'''----------------------------------------------
Writes body when there isnt a supergroup.
----------------------------------------------'''
def write_body_no_sg(data,text=''):
    tmp = ""

    for key in data["free_vars"]:
        free_var = data["free_vars"][key]           
        if(key == list(data["free_vars"].keys())[0]):
            tmp += temps["free_vars"].format(key, free_var["mean"],free_var["std"])
        else:
            tmp += str_format(text,temps["free_vars"].
            format(key, free_var["mean"],free_var["std"]),True)
        tmp += str_format(tmp,add_maxmin(free_var,"max",data["ner_classes"],data),False)
        tmp += str_format(tmp,add_conjunction(text),False)
        tmp += str_format(tmp,add_maxmin(free_var,"min",data["ner_classes"],data),False)
            
    return tmp

'''----------------------------------------------
Writes body when there is a supergroup.
----------------------------------------------'''
def write_body_sg(data,R,df):
    
    tmp = ''

    for sg_val in list(data["super_group"]["vals"].keys()):
        tmp2 = ''
        sg_val_keys = list(data["super_group"]["vals"][sg_val].keys())
        intro_temp = add_sg_val_intro(sg_val,tmp,data["super_group"]["name"])
        tmp2 += intro_temp 

        #For each category in a supergroup value
        for cat_ind in range(0,len(sg_val_keys)):
            repeated = True
            cat = sg_val_keys[cat_ind]  
            while repeated:
                recent_temp = add_sg_cat(data,'',cat,cat_ind)
                repeated = repeated_words(intro_temp,recent_temp)

            tmp2 += recent_temp
            mean = data["super_group"]["vals"][sg_val][cat]["mean"]
            std = data["super_group"]["vals"][sg_val][cat]["std"]
            
            ind = randrange(len(temps["sg_val_mean_std"]))  
            tmp2 += str_format(tmp2,temps["sg_val_mean_std"][ind].format(mean,std),False)
            
            tmp2 += str_format(tmp2,add_maxmin(data["super_group"]["vals"][sg_val][cat],"max",data["ner_classes"],data),False)    
            tmp2 += str_format(tmp2,add_conjunction(tmp),True)
            tmp2 += str_format(tmp2,add_maxmin(data["super_group"]["vals"][sg_val][cat],"min",data["ner_classes"],data),False)
            tmp2 += end_sentence()

        table = df.loc[df[data["super_group"]["name"]].str.capitalize() == sg_val].to_html(index = False, justify = 'center')
        R.hyperlinks[sg_val] = [f'<section id="{sg_val}">{tmp2}', table.replace('\n', ''),"</section>"]
    
def mean_max_min(tipo, val, key, condicao):
    tmp = ""

    maximo = max(val[key].values())
    super_max = hyperlink(max(val[key].items(), key=operator.itemgetter(1))[0])

    minimo = min(val[key].values())
    super_min = hyperlink(min(val[key].items(), key=operator.itemgetter(1))[0])

    i = randrange(len(temps["sg_val_col"]))
    if(condicao):
        tmp = f"{tmp} {temps['sg_val_col'][i]} {key}"

    i = randrange(len(temps["super_group_sub_intro"]))
    ind_val = randrange(len(temps[tipo]))

    if(maximo != minimo):

        if(condicao):
            tmp += str_format(tmp,temps["global_val"].format(temps["super_group_sub_intro"][i],temps[tipo][ind_val],minimo,maximo),False)
        else:
            tmp += temps["global_val"].format("",temps[tipo][ind_val],minimo,maximo)
        tmp += end_sentence()

        i = randrange(len(temps["max"]))
        indice = randrange(len(temps["min"])) 
        tmp += temps["supergroup_minmax_global"].format(temps["min"][indice],super_min,temps["max"][i],super_max)
        tmp += end_sentence()
    
    else:
        i = randrange(len(temps["super_group_sub_intro"]))
        if(condicao):
            tmp += str_format(tmp,temps["same_global_val"].format(temps["super_group_sub_intro"][i],temps[tipo][ind_val],maximo),False)
        else:
            tmp += temps["same_global_val"].format("",temps[tipo][ind_val],maximo)
        tmp += end_sentence()

    return tmp