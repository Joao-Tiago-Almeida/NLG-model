import os
import glob
import pandas
import re
import numpy as np
from sklearn import model_selection
from sklearn import linear_model
from sklearn import svm
from sklearn.metrics import explained_variance_score
import matplotlib.pyplot as plt
import seaborn as sns
import json
from NER import detect_ner_classes
#from Server import nlp # not used
from googletrans import Translator
from NLGML import write_text
import pickle
import datetime
from statistics import mean
import time
report = {}
'''
Outros tableaus:
https://public.tableau.com/views/DashboardExample_14/DashboardExample?:embed=y&:display_count=yes&:showTabs=y&:showVizHome=no
https://public.tableau.com/views/money1_13/CashInstruments?%3Aembed=y&%3AshowVizHome=no&%3Adisplay_count=y&%3Adisplay_static_image=y&%3AbootstrapWhenNotified=true
https://public.tableau.com/views/money_0/Growth?%3Aembed=y&%3AshowVizHome=no&%3Adisplay_count=y&%3Adisplay_static_image=y&%3AbootstrapWhenNotified=true
https://public.tableau.com/views/RegisteredVehiclesOpenDataProject/BrandBenchmark?:showVizHome=n&amp;:embed=t
https://public.tableau.com/views/ThePulpFictionConnection/PulpFictionConnection?:showVizHome=n&amp;:embed=t
https://public.tableau.com/views/CashlessSociety/CashlessSociety?:showVizHome=n&amp;:embed=t
https://public.tableau.com/views/EuropeanParliamentElection2019/Dashboard1?:showVizHome=n&amp;:embed=t
https://public.tableau.com/shared/2YKXPSN27?:showVizHome=n&amp;:embed=t
https://public.tableau.com/en-us/gallery/costs-using-car?tab=viz-of-the-day&type=viz-of-the-day
https://public.tableau.com/views/Womensrepresentationinpoliticsvizforsocialgood/WomeninPolitics?:showVizHome=n&amp;:embed=t
https://public.tableau.com/views/TopLinkedInSkillsfor20142015and2016/LinkedInDashboard?:showVizHome=n&amp;:embed=t
https://public.tableau.com/views/BigBookofLineCharts/BBLC1?:showVizHome=n&amp;:embed=t
https://public.tableau.com/views/TheMeatMap/meat-dash?:showVizHome=n&amp;:embed=t
https://public.tableau.com/views/Banksy/Home?:showVizHome=n&amp;:embed=t
https://public.tableau.com/views/500womenscientistsdesktop/Dashboard1?:showVizHome=n&amp;:embed=t
https://public.tableau.com/views/2018W27NewYorkRatSightings/NewYorkRatSightings?:showVizHome=n&amp;:embed=t                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        5/Titanic?:showVizHome=n&amp;:embed=t"
'''
#Global variable that has the NER classes.
ner_classes = ["time","entity","location","litter"]

'''Returns to the report data the number of columns and rows of the dataset, or sub datasets.'''
def basic_char(dataset):
    tmp = {}
    tmp["n_rows"] = dataset.shape[0]
    tmp["n_col"] = dataset.shape[1]
    return tmp

'''-------------------------------------
Drops columns with standard deviation 0
-------------------------------------'''
def drop_col_no_std(dataset):
    corr_dataset = dataset

    for h in dataset.columns.values.tolist():
        if dataset[h].dtype.kind == "i" or dataset[h].dtype.kind == "f":
            if dataset.std()[h] == 0:
                corr_dataset = corr_dataset.drop(columns=h)
        # Drop columns with no numeric values
        else:
            corr_dataset = corr_dataset.drop(columns=h)
    return corr_dataset

'''-------------------------------------------------------------------------------------------------------------
The flag represents two cases. The first one where no supergroup is detected and so the value for this variable
will be None. The second one, where the flag will hold a string, for example "Domain" or "Water" 
that represents the subdataframe (Supergroup value).
------------------------------------------------------------------------------------------------------------"'''
def calc_corr(corr,flag:bool):
    #init

    correlations = set()
    #it only makes sense to calculate a correlation if there are more than 2 numeric columns.
    if(len(corr.columns) > 1):
        
        #There is no supergroup.
        # correlation heatmap
        try: 
            annot = len(report['sub_dfs'].keys()) <= 10 # avoid overlap of values
            plt.clf()
            ax = sns.heatmap(
                corr, 
                xticklabels=corr.columns.values,
                yticklabels=corr.columns.values,
                annot=annot,
                square=True,
                cmap='viridis',
                mask = np.eye(corr.columns.size, dtype=bool),
                vmin=-1,
                vmax=1,
                cbar_kws={'label': "Correlation's Colour Scale"})
            name = f"hmx-{time.strftime('%e-%b-%Y_%H:%M:%S')}.png"
            ax.figure.savefig(os.path.join('images', name), bbox_inches='tight')
            if report["tipo"] == "json":
                report['hmx'] = f"<p><style>img {{max-width: 100%;height: auto;}}</style><img src='{os.getcwd()}/images/{name}'></p>"
            else:
                report['hmx'] = f"<p><style>img {{max-width: 100%;height: auto;}}</style><img src='http://localhost:5000/images/{name}'></p>"

            
        except:
            report['hmx'] = ""
            
        for h in corr.columns.values.tolist():
            corr_column = corr.drop(h)

            #For each column gets the greatest modular correlation
            best_value = corr_column.apply(lambda x: max(x.min(), x.max(), key=abs))[h]
            row_id = corr_column[h].idxmin() if best_value < 0 else corr_column[h].idxmax()

            # If correlation is strongly negative or positive
            if best_value >= 0.75 or best_value <= -0.75:
                correlations.add(frozenset([h,row_id, best_value]))

        correlations = [list(x) for x in correlations]

        
        #Remember, if the flag is != None, that means it is a value of the supergroup.
        if(flag == None):
            report["corr"] = correlations
        else:
            if(correlations != []):
                report["corr"][flag] = correlations

    return correlations

'''--------------------------------------------------------------------
Returns correlations for a given excel. It treats two different cases.
When a supergroup is or not detected.
---------------------------------------------------------------------'''
def excel_correlation(dataset,report_data,dataset_dic):

    #Supergroup exists.
    if(report_data["super_group"] != None):
        res = []
        
        #Iterates each dataframe(There is a dataframe for each Supergroup value)
        for key in dataset_dic:    
            dataset = dataset_dic[key]
            res.append(pre_correlation(dataset,report_data,key))
        return res 
    
    else: #Supergroup does not exist
        return pre_correlation(dataset,report_data)

'''----------------------------------------------------------------------
Adds to report the tableau correlations. Has in consideration the two cases:
Where there is, isn´t a supergroup.
-----------------------------------------------------------------------'''
def tableau_correlation(dataset,report_data,dataset_dic:dict):
    sg = report_data["super_group"]

    #Caso nao existam supergrupos no tableau.
    if(sg == None):
        pre_correlation(dataset,report_data)
    else:
        #Stores the correlations.

        # Analysis only the column with the most changes, because it is the most likely to have notorious correlations and it keeps the program quick
        col_name = report_data['global_analysis']['std_max']['category']

        #Iterates Supergroup values.
        tmp = pandas.DataFrame()
        for key in dataset_dic.keys():
            tmp[key] = dataset_dic[key][col_name].reset_index(drop=True)

        calc_corr(tmp.corr(),None)
        
'''Prepares the dataframe before extracting correlations.'''
def pre_correlation(dataset,report_data,key = None):
    corr_dataset = drop_col_no_std(dataset)
    
    #Removes NER columns from the correlation.
    for classe in ner_classes:
        if report_data[classe] != None:
            
            if report_data[classe] in list(corr_dataset.columns.values):
                corr_dataset = corr_dataset.drop([report_data[classe]],axis = 1)
    calc_corr(corr_dataset.corr(),key)

def common_member(a, b): 
    a_set = set(a) 
    b_set = set(b) 
    # check length  
    if len(a_set.intersection(b_set)) > 0: 
        return(a_set.intersection(b_set))   
    else: 
        return [] 

def drop_empty_columns(dataset):
    #Drop columns with no values
    for h in dataset.columns.values.tolist():
        if dataset[h].isnull().sum() == dataset.shape[0]:
            dataset = dataset.drop(columns=h)
    return dataset

'''--------------------------------------------------------------------
Returns a dictionary with 2 keys. Each key value is an array 
containing the name of the columns that are either numeric or categoric.
--------------------------------------------------------------------'''
def get_column_types(dataset):
    col_labels = dataset.columns.values.tolist()
    col_types = {"numeric" : [] , "categoric" : []}
    for label in col_labels:

        #numeric cols
        if dataset[label].dtypes == "float64" or dataset[label].dtypes == "int64":
            col_types["numeric"].append(label)
        else:
            try:   #numeric cols
                dataset[label] = pandas.to_numeric(dataset[label])
                col_types["numeric"].append(label)

            except: #categoric cols
                col_types["categoric"].append(label)
    
    report["numeric"] = col_types["numeric"]
    report["categoric"]= col_types["categoric"]
    return col_types

'''-----------------------------------------------------------------------------
For each numeric column of the dataset registers the NER values for the maximum
and the minimum of entity,location or time. Receive as arguments:
dataset,
numeric column being iterated in the dataset.
supergroup value in the dataset.
returns a dictionary with 3 keys(entity,time location) with the column as values.
------------------------------------------------------------------------------'''
def init_report_ner():
    for ner in ner_classes:
        report[ner] = None

'''--------------------------------------------------------------------------
For each ner class(location, entity and time) it is stored the column with the
highest probability if the column is not the supergroup column.
---------------------------------------------------------------------------'''
def get_ner():
    ner = {}
    init_report_ner()
    for n_c in ner_classes:
        ner[n_c] = {}

    #For any column in the dataset.
    for col in report["cols_info"]:
        if(report["cols_info"][col] != None):
            prev_val = 0

            #Gets the class and the probability.
            classe = report["cols_info"][col]["ner"][0]
            val = report["cols_info"][col]["ner"][1]

            if (classe != "NULL" and val > prev_val and col != report["super_group"] ):
                ner[classe] = col #If it is a requirement to return the probability in the future, it is easy.
                prev_val = val
                report[classe] = col
    return ner  

'''---------------------------------------------------------------
This function adds to the report for each numeric column
the NER class values with respect to the maximum and minimum.
df - dataframe.
actual_col - numeric column being iterated.
cat_col - categoric column that gave positive to NER.
super_group_val - super group value being iterated now.
class_type - categoric column class
----------------------------------------------------------------'''
def add_max_min(df,actual_col,cat_col,super_group_val,class_type):
    if df[actual_col].dtype.name != "object":
        maxim = report["sub_dfs"][super_group_val][actual_col]["max"]
        minim = report["sub_dfs"][super_group_val][actual_col]["min"]

        if(len(df.loc[df[actual_col] == maxim][cat_col].values) > 0):
            
            max_categoric = df.loc[df[actual_col] == maxim][cat_col].values
            min_categoric = df.loc[df[actual_col] == minim][cat_col].values

            report["sub_dfs"][super_group_val][actual_col]["max_"+str(class_type)] = max_categoric
            report["sub_dfs"][super_group_val][actual_col]["min_"+str(class_type)] = min_categoric

'''---------------------------------------------------------------------
Adds to each max and min of a numeric columns
the values of the categoric cells considered as entity,
time and location.
---------------------------------------------------------------------'''
def add_ner(dataset,actual_col,super_group_val,ner):
    #for entity,time or location.
    for key in ner.keys():
        if ner[key] != actual_col and ner[key] != {}:
            add_max_min(dataset,actual_col,ner[key],super_group_val,key)

'''--------------------------------------------------------------------
dataset - Sub-dataset from the original fragmented in the values of the
supergroup - (super_group_val)
super_group_val - Value of the Supergroup.
---------------------------------------------------------------------'''
def basic_numeric_analysis(dataset,super_group_val = None):
    info = {}    
    col_types = get_column_types(dataset)
    num_dataset = dataset[col_types["numeric"]].copy()
    for column in list(num_dataset.columns):
        preInfo = num_dataset[column].describe()
        info[column] = preInfo

    # allows general analyse
    if super_group_val is None:
        return advanced_numeric_analysis(info,dataset)

    #Adds info of all columns to the report.
    report["sub_dfs"][super_group_val] = info

    ner = get_ner()
    for column in dataset.columns:
        add_ner(dataset,column,super_group_val,ner)

'''---------------------------------------
General analysis
----------------------------------------'''
def advanced_numeric_analysis(info_columns:dict,dataset):

    # struct example
    report['global_analysis'] = {
        'global_min': {
            'value': '',
            'category':'',
            'sg': None
        },
        'global_max': {
            'value': '',
            'category':'',
            'sg': None
        },
        'std_min': {
            'value': '',
            'category':''
        },
        'std_max': {
            'value': '',
            'category':''
        }
    }
    # Global values
    list_max_aux = []
    list_min_aux = []
    list_group_aux = []
    # Columns values
    list_std_aux = []

    for i in info_columns.keys():

        if i == report['time']:  # doesn´t analysis time variation
            continue

        list_max_aux.append(info_columns[i]['max'])
        list_min_aux.append(info_columns[i]['min'])
        list_group_aux.append(i)
        list_std_aux.append(info_columns[i]['std'])

    # organize values
    global_values = (max(list_max_aux),min(list_min_aux))
    global_values_index = (list_max_aux.index(max(list_max_aux)), list_min_aux.index(min(list_min_aux)))
    
    std_values = (max(list_std_aux),min(list_std_aux))
    std_values_index = (list_std_aux.index(max(list_std_aux)), list_std_aux.index(min(list_std_aux)))

    cat = ('max','min')
    for ind, m in enumerate(cat):  # index of 'm' in cat

        # Max and min global
        report['global_analysis']['global_'+m]['value'] = global_values[ind]
        category = list_group_aux[global_values_index[ind]]
        report['global_analysis']['global_'+m]['category'] = category
        index_sg = list(dataset[category]).index(global_values[ind])
        try:
            report['global_analysis']['global_'+m]['sg'] = dataset[report['super_group']][index_sg].capitalize()
        except:
            pass # there is no super_group

        # std
        report['global_analysis']['std_'+m]['value'] = std_values[ind]
        category = list_group_aux[std_values_index[ind]]
        report['global_analysis']['std_'+m]['category'] = category

'''---------------------------------------
Convert object column to int column.
----------------------------------------'''
def convert_object_int(df):
    cols = df.columns.values     
    for col in cols:
        try:
            tmp = df[col].replace(r'[,\"\']','', regex=True).replace(r'\s*([^\s]+)\s*', r'\1', regex=True)
            df[col] = pandas.to_numeric(tmp)
        except:
            #print(Couldn´t convert given column to int)
            pass
    return df

def translate_columns(df):
	translator = Translator()
	for col in df.columns.values:
		translated = translator.translate(col)
		if(translated.src != "en"):
			df = df.rename(columns={col: translated.text})
	return df

'''-------------------------------------------------------------------------------------
Returns a dictionary where each key is a column and the value is a dictionary
where the keys are the values for that column and the value the number of occurrences.
-------------------------------------------------------------------------------------'''
def values_distribution(df):
	dist_values = {}
	cols = df.columns.values
	for col in cols:

		#Only the categoric columns are relevant here.
		if(np.issubdtype(df[col].dtype, np.number) == False):

            #Each column starts as an empty dictionary.
			dist_values[col] = {}

			#iterates each cell in column
			for ind in range(0,len(df)):

				#gets cell
				val = df[col][ind]

                #Obtains the values stored until now in the dictionary.
				values = dist_values[col].keys()

                #If the value is not present in the dictionary list.
				if val not in values:
					dist_values[col][val] = 1
				else:
					dist_values[col][val] += 1
		else:
			pass
	return dist_values

'''----------------------------------------------------------
Returns a list with the columns considered groups.
----------------------------------------------------------'''
def kick_fake_groups(df,dist):
    new_df = df
    n_rows = df.shape[0]

    '''For each column in the dataframe it confirms if it appears in the dataframe.
    If not then it is removed from the new dataframe.'''
    for col in df.columns.values:
        if col not in dist.keys():
            new_df = new_df.drop([col], axis=1)

    for key in dist:
        n_key_vals = len(dist[key].keys())
		
        #If a column has too many values then it is definitely not a group column.
        if(n_key_vals > 0.60 * n_rows):
                new_df = new_df.drop([key], axis=1)
    return new_df.columns.values

'''----------------------------------------------------
Kick groups without variantion in any super group value
----------------------------------------------------'''
def kick_useless_numeric_groups(dataset):

    report_aux = report.copy()  # avoid changes list during iteraration
    
    for i in report_aux['numeric']:
        for j in report_aux['sub_dfs']:
            if report_aux['sub_dfs'][j][i]['std'] != 0:
                break
        else:
            for jj in report_aux['sub_dfs']:
                report['sub_dfs'][jj].pop(i)

            report['numeric'].remove(i)
            report['cols_info'].pop(i)
            report['basic_char']['n_col'] -= 1 # doesn´t specify for each value
            dataset = dataset.drop(columns=i)

    return dataset

'''--------------------------------------------------------------------------------------------------
Select supergroup if given in the table. For example in  https://public.tableau.com/views/IncomeStatement_10/IncomeStatementYTD?:embed=y&:display_count=y&:origin=viz_share_link, the sg should be "ACCOUNT LEVEL 0 NAME", but it is "Measure Names", because it is identify through "Account Type Sequence"
--------------------------------------------------------------------------------------------------'''
def given_super_group(dataset):

    array_names = dataset.columns.values.tolist()
    array_bool_2 = [False]*dataset.shape[1]
    array_bool_1 = [None]*dataset.shape[1]

    for idt in array_names:   # column 1 

        if len(set(dataset[idt])) == 1:   # avoids constant column
            continue

        array_bool_1 = [None]*dataset.shape[1]  

        for sg in array_names:   # column 2 - possible super_group

            # The super group have to be string and needs at least 2 values
            if len(set(dataset[idt])) <= 1 or not isinstance(list(dataset[idt])[0],str):
                array_bool_1[array_names.index(sg)] = False

            elif idt == sg:  # same columns
                continue

            for y in set(dataset[idt]):   # row to compare

                aux10 = dataset.loc[dataset[idt]==y].shape[0] # height of the group in column 1
                aux21 = list(dataset.loc[dataset[idt]==y][sg])[0]  # row value in column 2 (idt) that match with column 1 (sg) and row y
                aux20 = dataset.loc[dataset[sg] == aux21, idt].shape[0]    # height of the group in column 2
                
                if len(set(dataset.loc[dataset[idt]==y][sg])) != 1:  # a group in a column have to be constant
                    array_bool_1[array_names.index(sg)] = False

                elif aux10 != aux20 or aux10 < 2:    # for being an identifier, both height must match and more than one
                    array_bool_1[array_names.index(sg)] = False

                elif not isinstance(aux21,str): # checks if the column 2 may be a super_group based on its type, usually turns the identifier (number) to False
                     array_bool_1[array_names.index(sg)] = False
                else:
                    array_bool_1[array_names.index(sg)] = True

        if any(array_bool_1): # found a sg for identifier idt
            for i in range(len(array_bool_1)):
                if array_bool_1[i]:
                    array_bool_2[i] = True


    report["super_group_bonus"] = [array_names[z] for z in range(len(array_names)) if array_bool_2[z]] if any(array_bool_2) else []

'''----------------------------------------------------------------------------------------------------------
Adds the supergroup col(commonly refered as 'sg' in the code) to the report and returns it if there is one.
sg -> gives as possability to choose sg
-----------------------------------------------------------------------------------------------------------'''
def find_super_group(dist,group):

    super_group_col = None
    for column in dist:
        if column in group:
            if super_group_col == None and len(list(dist[column].keys())) > 1:
                super_group_col = column
            if super_group_col != None and len(list(dist[column].keys())) < len(list(dist[super_group_col].keys())) and \
            len(list(dist[column].keys())) > 1:
                super_group_col = column
    if super_group_col != None:
        report['super_group_bonus'].append(super_group_col)
    
    if len(report['super_group_bonus']) > 0:
        report['super_group'] = report['super_group_bonus'].pop()
    else:
        report['super_group'] = None

'''-----------------------------------------------------------
Classifies columns.
0 - Column is supergroup.
1 - Column is the value of a supergroup.
2 - Column is a features.

In this case the report considers a main column(0), where
other columns are dependant(1). The other columns are features.
------------------------------------------------------------'''
def add_group_columns(df,sub_groups):
    cols_info = {}
    sub_groups = [] if sub_groups is None else sub_groups
    for col in df.columns.values:
        cols_info[col] = {}
        if col == report["super_group"]:
            cols_info[col]["group"] = 0
        elif col in sub_groups:
            cols_info[col]["group"] = 1
        else:
            cols_info[col]["group"] = 2
    return cols_info
    
'''----------------------------------------------------------------------------
Receives as arguments sg(supergroup column, which is the name of the column considered 
a super group) and ogs (other groups) which is an array containing other groups."
Returns an array of subgroups.
----------------------------------------------------------------------------'''
def get_sub_groups(ogs):

	if report['super_group'] in ogs:
	    return np.delete(ogs, np.where(ogs == report['super_group']))

def check_unique_vals(df,cols_info):
	for col in df.columns.values:
		if len(df[col].unique()) == 1:
			cols_info[col]["unique_val"] = True
		else:
			cols_info[col]["unique_val"] = False
	return cols_info

'''-------------------------------------------------
Adds time span if detected a ner_time_class
-------------------------------------------------'''
def add_timespan(df,col):
    res = check_time_format(df[col])
    if(res != None):
        report["timespan"] = res
    else:
        startTime = df[col][0]
        endTime = df[col][df[col].count() -1]
        report["timespan"] = {"begin": startTime , "end": endTime}
    return

'''Checks if a given column as a certain data format'''
def check_time_format(col):
    minim = None
    min_string = None
    maxim = None
    max_string = None

    '''------------------------------------------------------------------------------------------------------------------------------------
    The first regex is a simple one to extract the date, the second one is a regex to be sure what kind of temporal format is being analyzed
	Because there might be dates like mm/dd/yyyy and dates like dd/mm/yyyy. The rarest regexes should appear first on the list called regexes
	The first index of the array corresponds to the Storms tableau case. Index 2 is just a common case.
    -------------------------------------------------------------------------------------------------------------------------------------'''

    regexes = [['[0-1]*[0-9]/[0-3]*[0-9]/\\d{4}[ ][0-9]+:\\d{2}:\\d{2}[ ](PM|AM)','^[0-3]?[0-9]/[0-3]?[0-9]/(?:[0-9]{2})?[0-9]{2}','%m/%d/%Y'], \
    		   ['(\\d|\\d{2})/\\d{2}/\\d{4}','(\\d|\\d{2})/\\d{2}/\\d{4}','%d/%m/%Y'], \
               ['\\d{4}','\\d{4}','%Y']]

    for reg in regexes:
        for cell in col:
            match = re.search(reg[0],str(cell))
            if(match != None):
                match = re.search(reg[1],str(cell))
                format_str = reg[2]
                datetime_obj = datetime.datetime.strptime(match.group(), format_str)
                #Init
                if(minim == None and len(match.group()) > 0):
                    minim = datetime_obj
                    min_string = match.group()
                else:
                    datetimes = [minim,datetime_obj]
                    new_min = min(datetimes)
                    if(new_min != minim and len(match.group()) > 0):
                        minim = new_min
                        min_string = match.group()

                if(maxim == None):
                    maxim = datetime_obj
                    max_string = match.group()
                else:
                    datetimes = [maxim,datetime_obj]
                    new_max = max(datetimes)
                    if(new_max != maxim):
                        maxim = new_max
                        max_string = match.group()
            else:
                minim = None
                maxim = None
                break
        if(minim != None and maxim != None):
            return {"begin": min_string  , "end": max_string}
    return None

def add_ner_columns(df,cols_info):
    res = detect_ner_classes(df)
    
    for col in cols_info.keys():
        #iterates keys: entity,time,location.
        for key in res.keys():
            if col in res[key]:
                if(key == "time"):
                    add_timespan(df,col)
                cols_info[col]["ner"] = (key,res[key][col])
                break
            else:
                cols_info[col]["ner"] = ("NULL",0)
    return cols_info

def gen_columns_info(df):

    if report['super_group'] is None: # if there is no super_group

        dist_values = values_distribution(df)
        all_groups = kick_fake_groups(df,dist_values)
        given_super_group(df)
        find_super_group(dist_values,all_groups)
        #find_super_group(dist_values,all_groups) #Normal search for super_group

    else:
        all_groups = report['categoric']

    #Returns array of subgroups.
    sub_groups = get_sub_groups(all_groups)
    cols_info = add_group_columns(df,sub_groups)
    cols_info = add_ner_columns(df,cols_info)
    cols_info = check_unique_vals(df,cols_info)
    return cols_info

'''--------------------------------------------------------------------------
If there is a supergroup splits the dataframe in the values of that 
supergroup. Returns a dictionary where the KEYS are the values of the 
supergroup and the VALUES are a dataset with the same number of columns.
---------------------------------------------------------------------------'''
def split_df(cols_info,df):
    dfs_list = {}
    found_super_group = False
    for col in cols_info:
    
        #0 refers to a supergroup.
        if cols_info[col] != None and cols_info[col]["group"] == 0:  
            found_super_group = True
            for col_val, df in df.groupby(col):
                dfs_list[col_val.capitalize()] = df
    
    #Case where there are no super_groups.
    if found_super_group == False:
        return {"UNIQUE_DF" : df }
    return dfs_list

def generate_text_data(dataset,tipo,sg:str=None):
    try:
        dataset = translate_columns(dataset)
    except:
        pass
    dataset = convert_object_int(dataset)

    '''Stores whether it is processing a excel or a tableau'''
    report["tipo"] = tipo
    report["super_group"] = sg
    report["timespan"] = None

    cols_info = gen_columns_info(dataset)
    
    '''If there is a supergroup in the dataframe, generates one subdataframe
    per subgroup value. Ex: For the mammals excels if "Domain" is picked as the super_group 
    then the will be sub dataframe for Earth and Water. '''
    df_dic = split_df(cols_info,dataset)

    #Stores info relative to each sub_df (there is a sub_df for each super_group value)
    report["sub_dfs"] = {}
    report["cols_info"] = cols_info
    report["corr"] = {}
    report["basic_char"] = basic_char(dataset)

    #For each super group value.
    for sg_val in df_dic.keys():
        df = df_dic[sg_val]

        #Drops the rows with null values.
        df = df.dropna(how='any') 
        report["basic_char"][sg_val] = basic_char(df)
        basic_numeric_analysis(df,sg_val)
    else:
        dataset = kick_useless_numeric_groups(dataset)
        basic_numeric_analysis(dataset)
    
    excel_correlation(dataset,report,df_dic) if(tipo == "excel") else tableau_correlation(dataset,report,df_dic)

    return write_text(report,ner_classes, dataset)

#Replace Null values from data set
def replace_null_values(dataset):
    null_values = ['Nulo', '%null%', '']
    dataset = dataset.replace(regex=null_values, value=np.nan)
    return dataset

def default_text_gen(data,tipo):

    files = glob.glob(os.path.join('images', '*'))
    for f in files:
        os.remove(f)

    dataset = format_labels(data)
    dataset = pandas.DataFrame(dataset)
    dataset = replace_null_values(dataset)

    result = []
    sg = None   # super group inital
    nr = 0 # number of reports wrote
    while True:
        result.insert(0,generate_text_data(dataset,tipo,sg))
        nr+=1
        if report['super_group_bonus'] == []:
            break
        sg = report['super_group_bonus'].pop()

    if nr>1:  # there is more than 1 report
        result.insert(1,f"<p>It was also wrote {nr-1} other relevant Report{'' if nr==2 else 's'}: </p>")

    return '\n'.join(result)

'''----------------------------------
Format all Labels to be in title case
----------------------------------'''
def format_labels(data :json):
    data_aux = []
    for x in data:
        l = list(x.keys())
        for y in l:
            x[y.title()] = x.pop(y)

        data_aux.append(x)

    return data_aux