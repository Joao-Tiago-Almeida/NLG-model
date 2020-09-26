#https://www2.le.ac.uk/offices/ld/all-resources/writing/writing-resources/reports

from random import choice as rnd
from random import randrange as rdr
from random import getrandbits
import ReportWriter as rw
from Templates import temps as temps
from Templates import dictionary as dictionary
import datetime
import uuid
import random

'''------------------------------------------------------------------------
Report strucure build in 2020 SummerInternship - João Almeida
---------------------------------------------------------------------------'''
class report():
    
    def __init__(self, title:str = 'Miss Subject'):

        self.title = title if title is not None else 'Miss Subject'
        self.text = ''
        self.hyperlinks = {}
        self.unique_sequence = uniqueid()
        
    def __str__(self):
        return self.text

    def generate_title(self):

        today = datetime.datetime.today()

        tmp = '<h1 style="color:PowderBlue; text-align:center;">' + self.title.upper() + '</h1>'
        tmp += '<h3 style=" text-align:center;">' + 'SySummerInternshipNLG' + '</h3>'
        tmp += '<h4 style=" text-align:center;">' + str(today.strftime("%e %b %Y")) + '</h4>'
        self.text += tmp

    def generate_terms_of_reference(self, date: dict = None):
        # example: https://unilearning.uow.edu.au/report/4biii1.html

        tmp = '<p>' + dictionary['TOF_1'] + rnd(dictionary['preposition_about']) + self.title.lower() 

        if date is None:
            tmp += '. '
        elif date['begin'] == date['end']:
            tmp += str(dictionary['timespan'][0]).format(date['begin'])
        else:
            tmp += str(dictionary['timespan'][1]).format(date['begin'], date['end'])

        tmp += dictionary['TOF_2']
        self.text += tmp + '</p>'

    def generate_introduction(self, data: dict = None, sg: list = []):
        tmp = '<p>'

        tmp += str(dictionary['Introduction_1']).format(data['n_cols'], rw.s_or_p(data["n_cols"]), data["n_rows"], rw.s_or_p(data["n_rows"]))

        super_group = '<li>{} <- <b>Super Group</b> -> values: ' + hyperlink(sg) + '</li>'

        aux1 = '<ol>'+' '.join(['<li>'+w+'</li>' if w != self.title else super_group.format(w) for w in data['categoric'] ])+'</ol>'
        aux2 = '<ul>'+' '.join(['<li>'+w+'</li>' for w in data['numeric']])+'</ul>'

        tmp += str(dictionary['Introduction_2']).format(len(data['categoric']), rw.s_or_p(data["categoric"]), aux1, len(data['numeric']), rw.s_or_p(data["numeric"]), aux2)

        tmp += dictionary['Introduction_3']

        self.text += tmp + '</p>'

    def generate_super_group_body(self, data: dict = None):

        self.text += global_values(data)
        self.text += write_by_std(data)
        self.text += write_conclusion(data)

    def generate_general_body(self, data: dict = None):

        self.text += write_general_std(data)
        self.text += max_min_global(data)

    def generate_draft(self):

        if not any(self.hyperlinks):
            return ''

        tmp = '<hr><h2 style="text-align:center;">Detail Analysis</h2><p>'
        tmp += '</p><p>'.join(
            [value[0] + collapse(key, value[1], 'Data', self.unique_sequence) + value[2] for key,value in self.hyperlinks.items()]
            )
        tmp += '</p></hr>'

        self.text += tmp

    def generate_correlation(self, data: dict = None):

        self.text += write_correlation(data)

        #True if code is runned by main (local) -> display collapse and image
        self.text += collapse(
            'Correlation',
            data['hmx'],
            'Heatmap',
            self.unique_sequence,
            True if data['tipo'] == 'json' and len(data['super_group_bonus']) == 0 else False)

    def add_text(self, string:str):
        self.text += f'<p>{string}</p>'
        
'''------------------------------------------------------------------------
Describes which supergroup changes the most and the least for each category
---------------------------------------------------------------------------'''
def write_by_std(data: dict) -> str:
    tmp = '<p style="color:RoyalBlue;">'

    # Biggest change for super group
    tmp += rnd(dictionary['STD_max/min_fe_sg_1']).format(data['super_group']['name'])
    tmp += rnd(dictionary['STD_max/min_fe_sg_2']) + rnd(dictionary['STD_max/min_fe_sg_3'])
    tmp += dictionary['noun_singular'] if len(data['by_super_group']['columns']['max']) == 1 else dictionary['noun_plural']
    # enumeration
    for g in data['by_super_group']['columns']['max'].keys():
        tmp += str(dictionary['class_str']).format(hyperlink(g))
        tmp += single_or_plural_in_array(data['by_super_group']['columns']['max'][g])
    else:
        tmp = f'{tmp[:-6]}. ' #remove: ", and "

    # mínimo
    tmp += rnd(dictionary['preposition_contrast'])
    #tmp += rnd(dictionary['STD_max/min_fe_sg_2'])
    tmp += rnd(dictionary['STD_max/min_fe_sg_4'])
    tmp += dictionary['noun_singular'] if len(data['by_super_group']['columns']['max']) == 1 else dictionary['noun_plural']
     # enumeration
    for g in data['by_super_group']['columns']['min'].keys():
        tmp += str(dictionary['class_str']).format(hyperlink(g))
        tmp += single_or_plural_in_array(data['by_super_group']['columns']['min'][g])
    else:
        tmp = f'{tmp[:-6]}. ' #remove: ", and "
    
    return tmp + '</p>'

'''-------------------------------------------------------------------------------
Describes which category by super_group which has the least and the most variation
--------------------------------------------------------------------------------'''
def write_conclusion(data: dict) -> str:
    tmp = '<p style="color:DeepPink;">'
   
    l=data['by_super_group']['all']

    tmp += rnd(dictionary['conclusion'])
    tmp += rnd(dictionary['STD_max/min_fe_sg_4']) + dictionary['noun_singular']
    tmp += f'in {hyperlink(l[0][0])} '
    tmp += rnd(dictionary['total_std_average'])
    tmp += f' {str(round(l[0][1],2))}'
    tmp += f". {rnd(dictionary['preposition_contrast'])}"
    tmp += rnd(dictionary['STD_max/min_fe_sg_3']) + dictionary['noun_singular']
    tmp += f'in { hyperlink(l[len(l)-1][0])} '
    tmp += rnd(dictionary['total_std_average'])
    tmp += f' {str(round(l[len(l)-1][1],2))}.'

    return tmp + '</p>'

'''-------------------------------------------------------------------------------
Describes which category which has the least and the most variation
--------------------------------------------------------------------------------'''
def write_general_std(data: dict) -> str:
    tmp = '<p style="color:LightSeaGreen;">'

    aux = data["global"]['std']

    tmp += rnd(dictionary['STD_max/min_fe_sg_2']).capitalize()
    tmp += rnd(dictionary['STD_max/min_fe_sg_3']) + dictionary['noun_singular']
    tmp += f'in {str(aux["max"]["category"])}, '
    tmp += f'with a std of {str(round(aux["max"]["value"],2))}. '
    tmp += rnd(dictionary['preposition_contrast'])
    tmp += rnd(dictionary['STD_max/min_fe_sg_4']) + dictionary['noun_singular']
    tmp += f'in {str(aux["min"]["category"])}, '
    tmp += f'with a std of {str(round(aux["min"]["value"],2))}. '

    return tmp + '</p>'

'''-------------------------------------------------------------------------------
Auxiliar function to write an array, according the amount of values
--------------------------------------------------------------------------------'''
def single_or_plural_in_array(array: dict) -> str:

    # only one element
    if len(array.keys()) == 1:
        (k,v) = array.popitem()
        return f'{k} with {str(round(v,2))}%, and '
    
    i = 0
    tmp = ''
    aux = ''
    # multiple elements
    for k,v in array.items():
        
        #last element
        if i == len(array.items())-1:
            tmp = tmp[:-2] # removes comma
            tmp += ' and ' + k + ' with {}, respectively, and '
        else:
            tmp += k + ', '

        aux+= str(round(v,2)) + '%; '

        i+=1
    
    return tmp.format(aux[:-2]) # removes last semicolon

'''--------------------------
Write max, min, mean, bounds
--------------------------'''
def global_values(data: dict) -> str:
    tmp = '<p style="color:Coral;">'
    average = {}
    max_val = {}
    min_val = {}
    sg_vals = list(data["super_group"]["vals"].keys())
    
    for sg_val in sg_vals:
        sg_val_keys = list(data["super_group"]["vals"][sg_val].keys())

        #For each category in a supergroup value
        for cat_ind in range(0,len(sg_val_keys)):
            cat = sg_val_keys[cat_ind]  

            if cat not in average:
                average[cat] = {}
                max_val[cat] = {}
                min_val[cat] = {}

            average[cat][sg_val] = data["super_group"]["vals"][sg_val][cat]["mean"]
            max_val[cat][sg_val] = data["super_group"]["vals"][sg_val][cat]["max"]["value"]
            min_val[cat][sg_val] = data["super_group"]["vals"][sg_val][cat]["min"]["value"]
        
    for key in average:
        tmp += rw.mean_max_min("average", average, key, True)
        tmp += rw.mean_max_min("max", max_val, key, False)
        tmp += rw.mean_max_min("min", min_val, key, False)

    return tmp + '</p>'

'''--------------------------------
Describes max and min global values
--------------------------------'''
def max_min_global(data: dict) -> str:

    tmp = '<p style="color:ForestGreen;">'
    minimo_global = data["global"]['values']['min']['value']
    maximo_global = data["global"]['values']['max']['value']

    str1 = ''
    str2 = ''

    if data['super_group']['name']:
        str1 += f"{hyperlink(data['global']['values']['max']['sg'])}'s "
        str2 += f"{hyperlink(data['global']['values']['min']['sg'])}'s "

    str1 += str(data["global"]['values']['max']['category'])
    str2 += str(data["global"]['values']['min']['category'])


    tmp += str(temps["global_extremes"]).format(maximo_global,str1,minimo_global,str2)
    tmp += rw.end_sentence()
    return tmp + '</p>'

'''------------------------------------
Format sg's values to have an hyperlink
-------------------------------------'''
def hyperlink(l: list) -> str:

    if not any(l):
        return ''

    if isinstance(l, str):
        return f'<a href="#{l}">{l}</a>'

    aux = [f'<a href="#{s}">{s}</a>; ' for s in l]
    #aux = ['<a href="https://www.google.pt" target="_blank">' + s + '</a>; ' for s in l]
    return ''.join(aux)

'''----------------------------------------------------------------
Organize correlation's text with base text, commun group and pairs
------------------------------------------------------------------'''
def write_correlation(data_: list) -> str:
    '''
    https://support.minitab.com/en-us/minitab-express/1/help-and-how-to/modeling-statistics/regression/how-to/correlation/interpret-the-results/
    Strength: The larger the absolute value of the coefficient, the stronger the relationship between the variables.
    Direction: If both variables tend to increase or decrease together, the coefficient is positive, and the line that represents the correlation slopes upward. If one variable tends to increase as the other decreases, the coefficient is negative, and the line that represents the correlation slopes downward.
    '''
    data = data_['group_corrs']
    
    topic = 'numeric features' if data_['super_group']['name'] is None else data_['global']['std']['max']['category']

    tmp = '<p style="color:purple;">'
    tmp += dictionary['Correlation_1']

    nr_corr = sum([len(x[1]) for x in data]) # number of correlations found

    try:
        len(data[0][1]) # random access to guarantee thats it is OK so far
    except:
        return "I had some problems computing Correlation: Fix me :'("

    if len(data[0][1])>1:   # whereas exist commun value

        tmp += dictionary['Correlation_2_1'].format(
            nr_corr,
            '' if nr_corr == 1 else 's',
            f'{rnd(dictionary["preposition_about"])} {topic}',
            hyperlink(data[0][0]),
            len(data[0][1]),
            '' if len(data[0][1]) == 1 else 's',
        )

        # when a value has a more than one connection
        tmp += '<br>' + ' '.join([multiple_main_value(a) for a in data if len(a[1])>1]).replace(f'<a href="#{data[0][0]}">{data[0][0]}</a>', f'<a href="#{data[0][0]}">it</a>')

    else: 
        tmp += dictionary['Correlation_2_0'].format(
            nr_corr,
            '' if nr_corr == 1 else 's',
            f'{rnd(dictionary["preposition_about"])} {topic}'
        )
    
    tmp += f"<br> {pair_values([a for a in data if len(a[1])==1])}" # when a value only connects to one other 

    return f"{tmp} <br>{dictionary['Correlation_8']}</p>"

'''------------------------------------------------
Separate whereas the pair increase or decrease
-------------------------------------------------'''
def increase_or_decrease(l: list) -> list:

    aux = [[],[]]
    for x in l:

        y = (list(x.keys())[0],list(x.values())[0])

        if y[1] < 0:
            aux[0].append(y)
        else:
            aux[1].append(y)

    return aux

'''------------------------------
Write text according commun value
------------------------------'''
def multiple_main_value(data: list) -> str:

    direction = rdr(len(dictionary['Correlation_3']))   # random word
    oposite_direction = 0 if direction == 1 else 1  # random word oposite

    tmp = rnd(dictionary['Correlation_4']).format(
        hyperlink(data[0]),
        dictionary['Correlation_3'][direction],
        rnd(dictionary['Correlation_5'])
    )

    aux = increase_or_decrease(data[1])  # separete regarding the direction
    # at least one flag is True
    flag_0 = True if aux[0] != [] else False
    flag_1 = True if aux[1] != [] else False

    if not (flag_0 and flag_1): # only one direction

        dir_opcional = oposite_direction if len(aux[0]) > 0 else direction  # relate with main variable
        col = 0 if len(aux[0]) > 0 else 1

        tmp += rnd(dictionary['Correlation_6']).format(
            array_names = hyperlink([x[0] for x in aux[col]]),
            dir = dictionary['Correlation_3'][dir_opcional],
            singular_ = 's' if len(aux[col]) == 1 else '',
            array_values = f"({'; '.join([str(round(x[1],2)) for x in aux[col]])})"
        )
    else: # both directions were found

        tmp += dictionary['Correlation_6'][1].format(
            array_names = hyperlink([x[0] for x in aux[1]]),
            dir = dictionary['Correlation_3'][direction],
            singular_ = 's' if len(aux[1]) == 1 else '',
            array_values = f"({'; '.join([str(round(x[1],2)) for x in aux[1]])})"
        )
        tmp += rnd(dictionary['preposition_contrast'])

        tmp += dictionary['Correlation_6'][0].format(
            array_names = hyperlink([x[0] for x in aux[0]]),
            dir = dictionary['Correlation_3'][oposite_direction],
            singular_ = 's' if len(aux[0]) == 1 else '',
            array_values = f"({'; '.join([str(round(x[1],2)) for x in aux[0]])})"
        )

    return tmp

'''------------------------------
Write pair(s) correlation text
------------------------------'''
def pair_values(data: list) -> str:  
    l=['','']
    for a in data:
        corr_value = list(a[1][0].values())[0]

        if corr_value < 0:
            l[0] += f'{hyperlink(a[0])} & {hyperlink(list(a[1][0].keys())[0])} w/ {round(corr_value,2)}; '
        else: 
            l[1] += f'{hyperlink(a[0])} & {hyperlink(list(a[1][0].keys())[0])} w/ {round(corr_value,2)}; '



    corr_7_1 = dictionary['Correlation_7_1'].format(
        '' if len(l[0]) == 0 else 'is' if l[0].count("&") == 1 else 'are',
        l[0][:-2] if len(l[0]) > 0  else ''
    )
    corr_7_2 = dictionary['Correlation_7_2'].format(
        '' if len(l[1]) == 0 else 'is' if l[1].count("&") == 1 else 'are',
        l[1][:-2] if len(l[1]) > 0  else ''
    )

    flag_1 = corr_7_1 != dictionary['Correlation_7_1'].format('','')
    flag_2 = corr_7_2 != dictionary['Correlation_7_2'].format('','')

    if not (flag_1 or flag_2):
        return ''

    return dictionary['Correlation_7'].format(
        s_p = 's' if len(data) > 1 else '',
        corr_7_1 = corr_7_1 if flag_1 else '',
        corr_7_2 = corr_7_2 if flag_2 else '',
        both = ', and ' if flag_1 and flag_2 else '' # when there are two different directions
    )        

'''-------------------------------------------------
Generates unique id, the server doesn´t take numbers
-------------------------------------------------'''
def uniqueid() -> str:
    seed = 65
    id = chr(seed)
    while True:
        yield id

        if seed > 122:
           seed = 65
           id += chr(seed)
        else:
            seed += 1
            id = chr(seed)
'''------------------------------------------------
Makes Collapsible Text, e.g. Tables, images, text
------------------------------------------------'''
def collapse(name: str, code: str, _type: str, unique_sequence, html: bool = False) -> str:
    #https://www.w3schools.com/bootstrap/bootstrap_collapse.asp
    '''
            EXAMPLES
    name: <sg_value>; correlation;
    code: report text; url; html code;
    type: heatmap; data; Report
    html: represents if it head has to be introduced
    '''
    head = '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">\
            <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>\
            <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js"></script>'\
            if html else ''

    id = next(unique_sequence).replace("\'","") # remove ''
    id = f'{name}{id}'.replace(" ","") # remove ' ' and be carefull, for each report the sequence is the same, so it is needed own name

    return  f'{head}<div class="toggle-container" style="margin-top:10px">\
                <button type="button" class="btn btn-info" data-toggle="collapse" data-target="#{id}">Click Here to Toggle View regarding {name}\'s {_type}</button>\
                <div id="{id}" class="collapse">\
                    {code}\
                </div>\
            </div>'