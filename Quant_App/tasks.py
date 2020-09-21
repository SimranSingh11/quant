import pymongo
import pandas as pd
# from Quant_App.models import DatalayersClass
from Quant_App.compute import automate_Raking, check_consequtive_fall_dfs, get_summary, transpose_rowindex, get_bestparametes_Combinations_unique
from Vantage_Quant.celery import app
from bson.objectid import ObjectId



myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["V-Quant"]
mystrategies = mydb['Mystrategies']
treat_param = mydb['TreatParam']
treatments_combinations = mydb['Treatment_Output_Combinations']
treat_all_dataframe = mydb["Treat_All_Dataframe"]


@app.task
def execute_computations(treatment_by, correlation, math_operators, industry, strategyname, treatment_name, wieghtage, param_name, response):
 
    # dataframe according to stratergy name
    print("0000000000000000000000000>", strategyname)
    StrategyName = str(strategyname)
    query = {"StrategyName":StrategyName}
    my_dict = mystrategies.find_one(query)
    strat_df = pd.DataFrame.from_dict(my_dict['StrategyDF']) 

    # strat_df = DatalayersClass.get_dataframes_by_stratergyname(strategyname)

    wieghtage = [int(i) for i in wieghtage] 
    treatment_df = strat_df * wieghtage

    print("COmputation started")
    # calling computation function
    my_dfs,Sorted_dfs,reductions_Dfs = automate_Raking(treatment_df)
    all_dfs = check_consequtive_fall_dfs(Sorted_dfs)
    print("this is all dfs length", len(all_dfs))
    Summary = get_summary(all_dfs)
    Trans = transpose_rowindex(Summary)
    Df9 = get_bestparametes_Combinations_unique(Trans)

    # database activity
    for (a, b) in zip(wieghtage, param_name):
        treat_param.insert({"treatment_id":ObjectId(response), "wieghtage":a, "param_name":b })
    
    # combinations insertions
    data_dict = Trans.to_dict("records")
    Df9_dict = Df9.to_dict("records")
    treatment_df = treatment_df.to_dict("records")
    treatments_combinations.insert({"treatment_id":ObjectId(response), "treatment_df":treatment_df ,'combinations_quartiles':data_dict, "unique_combinations":Df9_dict})

    # my_dfs insertion 
    for i in my_dfs:
        my_df_dic = i.to_dict("records")
        mydict = { "treatment_id":ObjectId(response),"MyDf_s": my_df_dic }
        treat_all_dataframe.insert(mydict,check_keys=False)
        
    # DatalayersClass.insert_computations(response, wieghtage, param_name, Trans, Df9, treatment_df, my_dfs)
    
    
    return True