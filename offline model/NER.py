from nltk import word_tokenize
from nltk.corpus import wordnet as wn
import re
from collections import defaultdict

ner_classes_tags = {
                    "entity" : { 
                            "tags" : [wn.synset("level.n.01"),wn.synset("product.n.01"),wn.synset("name.n.01"),wn.synset("customer.n.01"),wn.synset("department.n.01")],
                            "sws"  : [wn.synset("person.n.01"),wn.synset("president.n.01"),wn.synset("skill.n.01"),wn.synset("name.n.01"),wn.synset("person.n.01"),wn.synset("animal.n.01"),wn.synset("product.n.01"),wn.synset("feature.n.01")]
                        },    
                    "time" : { 
                         "tags" : [wn.synset("period.n.01"),wn.synset("quarter.n.01"),wn.synset("time.n.01"),wn.synset("day.n.01"),wn.synset("month.n.01"),wn.synset("year.n.01"),wn.synset("order.n.01"),wn.synset("date.n.01")],
                         "sws" : [wn.synset("period.n.01"),wn.synset("quarter.n.01"),wn.synset("week.n.01"),wn.synset("period.n.01"),wn.synset("time.n.01"),wn.synset("day.n.01"),wn.synset("month.n.01"),wn.synset("year.n.01"),wn.synset("date.n.01")]
                    },
                    "location": {
                        "tags" : [wn.synset("place.n.01"),wn.synset("local.n.01"),wn.synset("region.n.01"),wn.synset("zone.n.01")],
                        "sws" : [wn.synset("street.n.01"),wn.synset("place.n.01"),wn.synset("local.n.01"),wn.synset("region.n.01"),wn.synset("zone.n.01")]
                    },
                    "litter": {
                        "tags": [wn.synset("litter.n.01"),wn.synset("size.n.01")],
                        "sws": [wn.synset("litter.n.01")]
                    }
    }


'''---------------------------------------------------------------------------------------------
A multi-word is a word composed by 2 or more tokens. Example: "Order Date", "Customer Name".
Given a multi-word and an array of tags return a numeric value corresponding to the best
match corresponding to best similarity between the multi-word and an array of tags.
---------------------------------------------------------------------------------------------'''
def check_sub_word(word,tags):
    res = []
    for sub_word in word:
        contexts = wn.synsets(sub_word.lower())
        max_sim = 0
        for c in contexts:
            for tag in tags:
                try:
                    sim = c.path_similarity(tag)
                except:
                    sim = c.path_similarity(tag)
                if(sim!= None and sim > max_sim):
                    max_sim = sim
        res.append(max_sim)
    
    brute_res = sum(res)/len(res)  
    
    #0.05 is a random value to penalize multi-words with many elements.
    delta = len(word) * 0.05       
    res = brute_res - delta
    if res < 0:
        return 0
    else:
        return res


def tokenize(word):
    word = word.replace('(', ' ')
    word = word.replace(')', ' ')
    return re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', word)).split()


'''-------------------------------------------------------------------------------------------------
cols = columns of the dataset.
word = The columns with just one word are going to be compared with this
tags = Words that the multiword is going to be compared against with.
cols_sim = Dictionary that for each array of columns stores the most probable of being an entity
local or region.
------------------------------------------------------------------------------------------------'''
def detect_class(cols,word,tags,cols_sim):
    best_col = []

    #Iterates each column.
    for c in cols:
        if isinstance(c,int) == False:
            sim_atual = 0

            #In case the column is a multiword (Ex: "customer name or in camel case. Ex : orderDate")
            if len(tokenize(c)) > 1:
                sim_atual = check_sub_word(tokenize(c),tags)
                best_col.append([c,sim_atual])

            #In case the column is a single word.              
            else:
                col = c.lower()
                contexts = wn.synsets(col)
                sim_atual = 0
                for cont in contexts:
                    if (cont.path_similarity(word) != None and cont.path_similarity(word) > sim_atual):
                        sim_atual = cont.path_similarity(word)

            #threshold(arbitrarily value)
            if sim_atual > 0.05:
                cols_sim[c].append(sim_atual)
    return cols_sim

'''--------------------------------------------------------------------------
Returns a list with the columns belonging to a certain class.
dataset
tags (multiwords)
sws  (single words)
--------------------------------------------------------------------------'''
def ner(dataset,tags,sws):

    #Creates the dictionary. "key : []" where the similarity between words is going to be registed
    cols_sim = defaultdict(list)
 
    #Extract columns to compare with words.
    cols = dataset.columns.values
        
    for s_w in sws:
        cols_sim = detect_class(cols,s_w,tags,cols_sim)

    #Dicionary with just one value for the key.
    final_dict = {}
    
    #Extracts the best value(probability) and inserts in new dictionary.
    for key in cols_sim.keys():
        final_dict[key] = max(cols_sim[key])
     
    res = {}
    for key in final_dict.keys():
    	#If the probability is bigger than the threshold then a class is assigned.
    	if final_dict[key] > 0.2:
    		res[key] = final_dict[key]
    return res

'''---------------------------------------------------------------------------------------
Returns a dictionary where the keys are "entity","time" and "location" and the values are 
dictionaries where the keys are the column names and the values are probabilities.
One column can only belong to one class.
Example of return: {'entity': {}, 'time': {'Date': 1.0}, 'location': {}}
---------------------------------------------------------------------------------------'''
def detect_ner_classes(dataset):
    res = {}

    for ner_class in list(ner_classes_tags.keys()):
        res[ner_class] = ner(dataset,ner_classes_tags[ner_class]["tags"],ner_classes_tags[ner_class]["sws"])

    new_res = get_final_ner(dataset,res)
    return new_res

'''------------------------------------------------------------------------------------------
The ner class is a dictionary of dictionaries, where 
the keys are the ner_classes and the values are dictionaries where
the key is the name of a column and the value a probability. This function
picks for each ner_class the one with the highest probability and in case the same
column is choosen for two ner_classes, pick the one with highest probability.
------------------------------------------------------------------------------------------'''
def get_final_ner(dataset,ner_classes):

    res = {}
    ner_names = list(ner_classes.keys())

    for key in ner_names:
        res[key] = None

    '''iterates NER names: entity,location,time. '''
    for name in ner_names:
        ner_pairs = ner_classes[name]
        max_col_val = 0
        max_col = None

        #Cada key e o nome de uma coluna.
        for key in ner_pairs.keys():
            if ner_pairs[key] > max_col_val:
                max_col_val = ner_pairs[key]
                max_col = key 
        if max_col_val > 0:
            res[name] = [ max_col,max_col_val]
    tmp = double_class(res,ner_classes)
    
    '''Drops class with lower prob if double class '''
    if(tmp != False):
        del ner_classes[tmp[0]][tmp[1]]
        res = get_final_ner(dataset,ner_classes)

    '''Answer formatting in the shape of a dictionary'''
    answ = {}
    for key in res.keys():
        if res[key] == None:
            answ[key] = {}
        else:
            if isinstance(res[key], dict) == False:
                answ[key] = {}
                answ[key] = {res[key][0] :  res[key][1]}
            else:
                answ[key] = res[key]    
    return answ

'''-----------------------------------------------------------------------------------------------
Returns False in case there is no double class or an array of 2 elements
where the first element is the name of the ner_class and the second the name of the column.

Example: If a given column, for example "Age" is considered as the NER class for "time" with
probability 0.3 and for "entity" with probability 0.26, then we want to eliminate 
the column "Age" from ner_class "time" and if possible attribute it to other column.
------------------------------------------------------------------------------------------------'''
def double_class(res,ner_classes):    
    max_class = None
    max_val = 0
    max_col = None

    #Each key is a ner_class: entity, time or location.
    for key in list(res.keys()):
        
        #Only enters in this if if finds repeated column
        if res[key] != None and res[key][0] == max_col:
            if res[key][1] > max_val:
                return [max_class,max_col]
            else:
                return [key,max_col]
                        
        if res[key] != None and res[key][1] > max_val: 
            max_val = res[key][1]
            max_col = res[key][0]
            max_class = key            
    return False
        
