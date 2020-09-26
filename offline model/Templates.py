# Phrase segments
temps = { 
        "pre_intro": "This report was {} from a table with <b>{}</b> column{} and <b>{}</b> row{}, ",
        "intro": "which has {} numeric feature{}: <br> <b>{}</b><br> and {} categorical feature{}: <br> <b> {}</b> <br>",
        "free_vars": "For <b>{}</b> the mean is {:.2f} and the standard deviation is {:.2f}  ",
        "conj": ["besides that","additionally","also","besides","secondly","apart from that", "moreover", "futhermore",
                "in addition"],
        "final_conj_cop": [" and finally", "and lastly","and to end","and to conclude"],

        "max": ["maximum","maximum value","greatest value","greatest", "biggest value", "top value"],
        "min":["minimum","minimum value","smallest value", "lowest value", "littlest value"],
        "maxmin_text": ["the {} is {:.2f}"],

        "average": ["average"],
        
        #Estes 3 nao sao seleccionados de forma aleatoria! Sao escolhidos para a frase ser mais coerente.


        "maxmin_entity":["and belongs to the {}, <b>{}</b>", "and is associated with {}, <b>{}</b>",
                         "and matches {} <b>{}</b>", "and corresponds to {} <b>{}</b>"],
        "maxmin_time":["which happened in {} <b>{}</b>","which occurred in {} <b>{}</b>","took place in {} <b>{}</b>"],
        "maxmin_location":["in {}, <b>{}</b>"],
        #"maxmin_litter" : ["LIXO LIXO LIXO {}, <b>{}</b>"],

        "time": ["for the timeline of <b>{}</b> ", "for the period of <b>{}</b> ", "for the date of <b>{}</b> "],
        "timespan": ["for the time span ranging from <b>{}</b> to <b>{}</b> "],
        "default_intro":["It is possible to conclude {} the following:<br>  ","The following conclusions {} have been drawn:<br> "],
        "super_group_intro":["The information can be analyzed separately {} for each different value of  {}",
                             "By analyzing {} the data for the different values of {}",
                             "After analyzing {} all possible values for  {}"],
        "super_group_sub_intro":["It is possible to take the following conclusions:",
                              "The following can be concluded:",
                              "It is known:" ,
                              "The following conclusions have been drawn:",
                               "It is possible to conclude:"],                         

        "sg": ["{}  <b>{}</b>"],
        "sg_corr":["{} <b> {}</b>"],
        "sg_val": ["{} <b>{}</b>"],

        "same_sg_val": ["Still {} the same <b>{}</b> value","Continuing the analysis for {}",
                        "Analyzing the same {}"],
        "same_sg_verb":["considering","concerning","having in consideration","analyzing", "regarding", "about"],
        "same_sg_conj":["but now","but"],
        "sg_val_intro": ["For","Concerning","Considering","About","For the value","When it comes to the value","Concerning the value",
                        "For {}","Concerning {}","Considering {}","About {}","For the value {}","When it comes to the value {}"],
        "sg_val_var":["for","concerning","considering","about","considering the variable","concerning the variable","to",
                      "when it comes to the variable", "regarding"],
        "sg_val_col":["Concerning","Considering","About","Considering the column","Concerning the column",
                "When it comes to the column", "Regarding"],

        "sg_val_mean_std": ["the mean is {:.2f} and the standard deviation is {:.2f}",
                            "the average is {:.2f} and the standard deviation is {:.2f}"],

        "no_corrs": ["No correlations between the present variables have been detected {}","No correlations were found {}"],
        "analysis": ["during the analysis", ""],

        "corrs_intro": ["It {} detected {} correlation{} between the variables in the data, "],
        "corr_val": [" a {} one({:.2f}) between <b>{}</b> and <b>{}</b>"],   
        "excel_group_corr_val": [" a {} one({:.2f}) between <b>{}</b> and <b>{}</b>"],

        "tableau_group_corrs_intro": ["It was detected {} correlation{} for the different values of <b>{}</b>"],
        "excel_group_corrs_intro": ["It was detected {} correlation{} during the analysis when considering {} as a {}:"],
        "create" : ["created","made","generated", "produced"] ,  


        # 2020 new - need to be polished
        "global_val": "{} The {} is between {:.2f} and {:.2f}",
        "same_global_val": "{} The {} is {:.2f}",
        "supergroup_minmax_global" : " The {} is in supergroup {} and the {} is in supergroup {}",
        "global_extremes": "We can conclude too that the global maximum is {:.2f} in {} and the global minimum is {:.2f} in {}",

        "super_group_std":[' for each category,', ' and for each category,', ' coming about for every class,'],
        "super_group_std_major":[" the major changes are", " the biggest changes are"],
        "super_group_std_minor":[" the minor changes are", " the smallest changes are"],
        "contrast":['In contrast ', 'By contrast, '],
        "class_str":[" in {}'s "],
        "enumaration_str":[" {},"],
        "value_%":[" {:.2f}%"],
        "conclusion":['The paper concludes by arguing', 'In summary, this paper argued that', 
                'The analysis leads to the following conclusions:', 'This conclusion follows from the fact that'],
        "total_std_average":[ 'with a standard deviation average of', ' with a standard deviation mean of']
}    

# Phrase templates
dictionary = {
    'TOF_1': 'This report provides information obtained through data from excel or tableu, ',

    'TOF_2': 'This report will comment on the highligths of the data and search for possible correlations. These observations do have limitations which will be noted.',

    'timespan': [" in the year {}. ", " for the time {} to {}. "],

    'Introduction_1': "Although processing data is not the easiest thing for humans, analyzing data is simple. On the other hand, computers make data processing effortless but how far are they from being able to report them faithfully? This report sums up the information of {} column{} and {} row{}. ",

    'Introduction_2': "The program identified {} categorical feature{}: {} and {} numeric feature{}: {} ",
    
    'Introduction_3': "This report summarize mathematical operations within each column such as mean or standard deviation, and elaborate the comparative relation between different columns like global maximum and minimum.",

    'STD_max/min_fe_sg_1': ['After analyzing all possible values for {}, ',"The information can be analyzed separately for each different value of {} ", "By analyzing the data for the different values of {} "],

    "STD_max/min_fe_sg_2":['for every numeric category ', 'and for each numeric category, ', 'coming about for every numeric class '],

    "STD_max/min_fe_sg_3":["the major change", "the biggest change"],

    "STD_max/min_fe_sg_4":["the minor change", "the smallest change"],

    'noun_singular':' is ',
    'noun_plural':'s are ',

    "conclusion":['The paper concludes by arguing ', 'In summary, this paper argued that ', 
                'The analysis leads to the following conclusions: ', 'This conclusion follows from the fact that '],

    "total_std_average":['with a standard deviation average of ', 'with a standard deviation mean of '],

    "preposition_contrast":['In contrast, ', 'By contrast, ', 'Although, ', 'On the other hand, '],
    
    'preposition_about': ['about ','regarding ','regardless of ','concerning ','respecting ','relating to ','relative to ','with respect to ','with reference to ','in regard to ','with regard to '],

    "class_str": "in {}'s ",

    "Correlation_1" : "In this section, it is analyzed the correlation in the data. Correlation is a term that is a measure of the strength of a linear relationship between two quantitative variables. More specifically, it is composed by 2 key factors: strength and direction. While strength quantifies the correlation coefficient's value in absoltute range from 0 to 1, the sign of the coefficient indicates the direction of the relationship. In other words, the sign represents whereas the variables evolve in the same way and the absolute value the connection's power. ",

    "Correlation_2_1": "For the {} relevant correlation{} found {}, the most commun value is {} with {} connection{}. ",

    "Correlation_2_0": "For the {} relevant correlation{} found {}, there is not a commun value. ",

    "Correlation_3": ['increase', 'decrease'],

    "Correlation_4": ["As {} tends to {}, {} ", "When {} {}s, {}"],
    #   'As {'sg name'} tends to {'increase/decrease'}, {Correlation_5} '
    #   "When {'sg name'} {'increase/decrease'}'s, {Correlation_5}"

    "Correlation_5": ["", "judging by the sinal, "], 

    # not random when both directions were found
    "Correlation_6": ["{array_names} tend{singular_} to {dir} togheter with a Pearson correlation coefficient of {array_values}. ",
                        "{array_names} {dir}{singular_} with ratio {array_values}. "],  
    #   {'array sith sg names'} tend{'s if singular'} to {'increase/decrease'} togheter with a Pearson correlation coefficient of {'array with values'}
    #   {'array sith sg names'} {'increase/decrease'}{'s if singular'} with ratio {'array with values'}.

    "Correlation_7": "It was found correlation's pair{s_p} that increase {corr_7_1}{both}{corr_7_2}",
    #   "Is was found correlation's pair{singular or plural} that increase {Correlation_7_1} {, and -> if both Correlation_7_1 and Correlation_7_2} {Correlation_7_2}"

    "Correlation_7_1": "contrary which {} {}. ",
    # which {'is/are'} {'vector of pairs and value'}

    "Correlation_7_2": "simultaneously which {} {}. ",
    # which {'is/are'} {'vector of pairs and value'}

    "Correlation_8": "Note that it is never appropriate to conclude that changes in one variable cause changes in another based on correlation alone. Furthermore, the parallelism increase/decrease is mutual. "
}