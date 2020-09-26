import random
from ReportWriter import write_final_text
from typing import List, Dict, Union
import numpy as np

text_structure = {}

#If a subgroup value only has 1 row then it is excluded.
def remove_invalid_keys(keys,report):
    for key in keys:
        if(report["basic_char"][key]["n_rows"] == 1):
            keys.remove(key)
    return keys

def write_super_group(report_data,ner_classes):
    sg_values = list(report_data["sub_dfs"].keys())
    sg_values = remove_invalid_keys(sg_values,report_data)

    #Adiciona ao init_structure
    text_structure["super_group"]["name"] = report_data["super_group"]
    
    #the supergroup has always more than 1 value.
    write_super_group_value(sg_values,report_data,ner_classes)

def write_text(report_data,ner_classes,df):

    init_text_structure(report_data)
    
    if(report_data["timespan"] != None):
        text_structure["timespan"] = report_data["timespan"]

    #ALL REPORTS HAVE INTRO.
    write_intro_text_structure(report_data)

    #IF REPORT HAS SUPERGROUP
    if (report_data["super_group"] != None):
        write_super_group(report_data,ner_classes)
        std_analysis(report_data)
        sort_correlation_pairs(report_data["corr"])

    else: #IF REPORT DOES NOT HAVE SUPERGROUP
        get_num_vars(report_data,None,ner_classes)
        sort_correlation_pairs(report_data["corr"])

    "Adds ner_classes to final text"
    text_structure["ner_classes"] = ner_classes

    final_text = write_final_text(text_structure, df)
    return final_text

def init_num_var(col_info,ner_classes):
    tmp = {}
    tmp["mean"] = col_info["mean"]
    tmp["std"] = col_info["std"]
    tmp["max"] = {}
    tmp["min"] = {}

    for n_c in ner_classes:
        tmp[n_c] = {}
        tmp["max"][n_c] = None
        tmp["min"][n_c] = None

    tmp["max"]["value"] = col_info["max"]
    tmp["min"]["value"] = col_info["min"]
    return tmp

'''-----------------------------------------------------------------
For each value of the super group, other columns are going to be 
iterated and analyzed. The keys are the name of the supergroup values.
If there is no supergroup then we still want info about numeric vars. 
-------------------------------------------------------------------'''
def get_num_vars(report_data,key,ner_classes):
    text_structure["super_group"]["vals"][key] = {} 
    ner = list(map(report_data.__getitem__, ner_classes))
    
    #IF THERE IS SUPERGROUP.
    if report_data["super_group"] != None:
        sub_val_cols = list(report_data["sub_dfs"][key].keys()) 
        for col in sub_val_cols:

            #The columns considered as NER are not analyzed unless there is only 1 column.
            if col not in ner or len(sub_val_cols) == 1 :

                col_info = report_data["sub_dfs"][key][col]
            
                #Initializes the column.
                text_structure["super_group"]["vals"][key][col] = init_num_var(col_info,ner_classes)

                for ner_class in ner_classes:
                    if(ner_class_exists(col_info,report_data,ner_class)):
                        text_structure["super_group"]["vals"][key][col][ner_class] = report_data[ner_class]
                        text_structure["super_group"]["vals"][key][col]["max"][ner_class] = col_info["max_" + str(ner_class)]
                        text_structure["super_group"]["vals"][key][col]["min"][ner_class] = col_info["min_" + str(ner_class)]

    
    else: #IF THERE IS NO SUPERGROUP.
        for col in report_data["sub_dfs"]["UNIQUE_DF"]:

            #The columns considered as NER are not analyzed unless there is only 1 column.
            if col not in ner or len(report_data["sub_dfs"]["UNIQUE_DF"]) == 1 :

                col_info = report_data["sub_dfs"]["UNIQUE_DF"][col]

                text_structure["free_vars"][col] = init_num_var(col_info,ner_classes)

                for ner_class in ner_classes:
                    if(ner_class_exists(col_info,report_data,ner_class)):
                        text_structure["free_vars"][col][ner_class] = report_data[ner_class]
                        text_structure["free_vars"][col]["max"][ner_class] = col_info["max_" + str(ner_class)]
                        text_structure["free_vars"][col]["min"][ner_class] = col_info["min_" + str(ner_class)]

def write_super_group_value(keys,report_data,ner_classes):
    #Each key is a supergroup value.
    for ind in range(0,len(keys)):
        text_structure["super_group"]["vals"][keys[ind]] = {} 
    for key in keys:
        get_num_vars(report_data,key,ner_classes)

#Initializes the text structure with the main fields of the report.
def init_text_structure(report):
    text_structure["intro"] = {}
    text_structure["intro"]["numeric"] = []
    text_structure["intro"]["categoric"] = []
    text_structure["intro"]["n_rows"] = None
    text_structure["intro"]["n_cols"] = None
    text_structure["super_group"] = {}
    text_structure["super_group"]["vals"] = {}
    text_structure["super_group"]["name"] = None
    text_structure["super_group_bonus"] = report["super_group_bonus"]
    text_structure["free_vars"] = {}
    text_structure["corrs"] = {}
    text_structure["group_corrs"] = {}
    text_structure["tipo"] = report["tipo"]
    text_structure["timespan"] = None
    text_structure['hmx'] = report['hmx']

    ## from global analysis
    text_structure["global"] = {}
    # save global values
    text_structure["global"]['values'] = {}
    text_structure["global"]['values']['max'] = report['global_analysis']['global_max']  # global max
    text_structure["global"]['values']['min'] = report['global_analysis']['global_min']  # global min
    # std from each column
    text_structure["global"]['std'] = {}
    text_structure["global"]['std']['max'] = report['global_analysis']['std_max']    # std max
    text_structure["global"]['std']['min'] = report['global_analysis']['std_min']    # std min

    ## from parcial analysis
    text_structure["by_super_group"] = {}
    text_structure["by_super_group"]['columns'] = {}    # sg that has std max for each column
    text_structure["by_super_group"]['all'] = {}        # std mean for each sg

def write_intro_text_structure(report):        
    text_structure["intro"]["n_rows"] = report["basic_char"]["n_rows"]
    text_structure["intro"]["n_cols"] = report["basic_char"]["n_col"]
    write_var_type_intro("categoric",report)
    write_var_type_intro("numeric",report)

def get_cats(report,var_type):
    for v in range(0,len(report[var_type])):
        text_structure["intro"][str(var_type)].append(report[var_type][v])

#var_type is either numeric or categoric.
def write_var_type_intro(var_type,report):
    if(len(report[var_type]) > 0):
        get_cats(report,var_type)

#Tells if the algoritm was able to detect entities,locations or time.
def ner_class_exists(col,report,ner_class):
    return (report[ner_class] != None) and (("max_"+str(ner_class)) in col.keys())

'''-----------------------------------------
Sort group correlations by the most influence
-----------------------------------------'''
def sort_correlation_pairs(corrs:List[Union[int, str, str]] = []):

    s = {}
    for pair in corrs:  # get most apperance
        for x in pair:
            try:
                int(x)
            except:
                if x in s.keys():   # first time 
                    s[x]+=1
                else:
                    s.update({x:1})
        
    s = sorted(s.items(), key=lambda kv: kv[1], reverse=True)
    l = [x[0] for x in s]   #   sorted list by the most influnce

    corr_ord = {}

    # sort pairs
    for pair in corrs:
        aux = []
        num = None
        for x in pair:
            try:
                int(x)
                num = x
            except:
                aux.append(x)
                
        aux.sort(key=lambda y: l.index(y))  # sort by the most commun
        aux.append(num)

        try:
            corr_ord[aux[0]].append({aux[1]:aux[2]})

        except: # new element
            corr_ord[aux[0]] = [{aux[1]:aux[2]}]

    # sort correspondent pair in unsorted main list
    for x in corr_ord:
        corr_ord[x].sort(key = lambda y: l.index(list(y.keys())[0]))

    # sort main list
    corr_ord = sorted(corr_ord.items(), key=lambda y: l.index(y[0]))

    text_structure["group_corrs"] = corr_ord

'''--------------------------------------------------------------------------------------
From std criterion, finds the maximum and minimum column for each sg
Only valid when sg exits
--------------------------------------------------------------------------------------'''
def std_mean_column(sg_names: List[str], cat4sg: Dict, report_data: List[Dict]) -> dict:

    temp_dict = {'max':{},'min':{}}

    for cat in cat4sg[0].keys():

        if cat == report_data['time']:  # doesn´t analysis time variation
            continue

        data = [abs(cat4sg[i][cat]['std']/cat4sg[i][cat]['mean']) for i in range(len(cat4sg))]  #standart derivation

        # name of supergroup that is a extreme
        temp_dict['max'][cat] = sg_names[data.index(np.nanmax(data))]
        temp_dict['min'][cat] = sg_names[data.index(np.nanmin(list(reversed(data))))] # avoid same column name if values are equal

    # rearange from easier text generation
    temp_dict['max'] = std_reorganize(temp_dict['max'])
    temp_dict['min'] = std_reorganize(temp_dict['min'])

    temp_dict['max'] = variation_p(temp_dict['max'],report_data)
    temp_dict['min'] = variation_p(temp_dict['min'],report_data)

    return temp_dict

'''--------------------------------------------------------------------------------------
Changes Key with Item
Insert in a list when there are multiple categories with the same super-group
--------------------------------------------------------------------------------------'''
def std_reorganize(var: Dict[str,Dict[str,List[str]]]) -> Dict[str,List[str]]:
    
    dict_aux: Dict[str,List[str]]= {}

    for k,i in var.items():
        try:
            dict_aux[i].append(k)   # multiple numeric values for the super group's value
        except:
            dict_aux[i] = [k]   # new super group

    return dict_aux

'''------------------------------------------------------
Compute the standard variation average for each super group
--------------------------------------------------------'''
def std_variation(sg_names: List[str], cat4sg: Dict):

    cumsum = 0   # cummulative sim
    lists = []  # lists

    # for all values in super group
    for f1 in cat4sg:
        # mean by super group
        for f2 in cat4sg[0].keys():
            cumsum += f1[f2]['std']
        lists.append(cumsum/len(cat4sg[0].keys()))
        cumsum = 0
    
    lists = list(zip(sg_names,lists))
    lists = [x for x in lists if not np.isnan(x[1])]
    lists.sort(key = lambda x: x[1]) 

    return lists

'''------------------------------------
Compute analysis according std and mean
------------------------------------'''
def std_analysis(report_data: List[Dict]) -> Dict[str,Dict[str,List[str]]]:

    sg_names = list(report_data['sub_dfs'].keys())  #list of supergroup names
    cat4sg = list(map(report_data['sub_dfs'].__getitem__, sg_names))    #data from each sg

    text_structure["by_super_group"]['columns'] = std_mean_column(sg_names, cat4sg, report_data)
    text_structure["by_super_group"]['all'] = std_variation(sg_names, cat4sg)

'''-------------------------------------------------
Compute the range in percentage for extreme columns
-------------------------------------------------'''
def variation_p(struct: Dict[str,str], report_data: List[Dict]) -> Dict[str,Dict[str,str]]:

    struct_aux = {}
    
    for f1 in struct:
        struct_aux[f1] = {}
        for f2 in struct[f1]:
            
            std = report_data['sub_dfs'][f1][f2]['std']
            mean = report_data['sub_dfs'][f1][f2]['mean']

            struct_aux[f1][f2] = 100 * abs(std/mean)

    return struct_aux