import pymongo
import pandas as pd
#import pymongo
import base64
import bson
from bson.binary import Binary#
import xlrd 
import justpy as jp
import glob as gb
import os
import numpy as np
import datetime
from django.db import models
from os import listdir
from os.path import isfile, join
from collections import defaultdict
from bson.objectid import ObjectId
import sys 
from Quant_App.tasks import execute_computations

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["V-Quant"]  ## DB
company= mydb["Myparameters"]   ## Collection for Parameters table...
mycol = mydb["Quan-Users"]  ## Users Table
mytesting = myclient["MyTesting"]  ## DB this for Testing collection....
mystrategies = mydb['Mystrategies']
treatment = mydb['Treatment']
treat_param = mydb['TreatParam']
tca_data = mydb["TCA"]  ## Table 
industry = mydb["industry_universe"]  ## Table 
param_mapping = mydb["ParamMapping"]  ## Table 
return_risks_views = mydb["Return-Views"]
treatments_combinations = mydb['Treatment_Output_Combinations']
treat_all_dataframe = mydb["Treat_All_Dataframe"]


## Datefunctionlity 

currenttime = datetime.datetime.now()  ##
currenttime =  str(currenttime)


### Databases clas and methods
class DatalayersClass():
    """
    DatalayersClass is for retrive the data from Data base and insert data into Database collections...
    Any data CRUD Operation in MongoDB
    """

    def __init__(self):

        return self

    def get_collections():
        """
        retrieve all the collecions from EXCEL files data base...

        returns list of collection in Database...
        """
        #coll_list = mydb.list_collection_names()
        
        return coll_list

    def insert_data_into_mongo(excel_path):
        """
        method: insert_data_into_mongo(Excel_path):
            -- This function is used to insert data file which Excel into MongoDB as Collections...
            -- Its creates Every individual Excel sheet as Collection with Excel Sheet Name...

        Arg: excel_path while are upoloading from USER Interface...

        """
        loc = (excel_path)
        print(loc)
        try:
            wb = xlrd.open_workbook(loc) 
            sheet_names = wb.sheet_names()
            print('sheets:')
            print(sheet_names)
            
            number_of_sheet = len(sheet_names)
            print('there are ' + str(number_of_sheet) + ' sheets')

            for i in range(0,number_of_sheet):
                data = []
                sheet = wb.sheet_by_index(i) 
                sheet.cell_value(0, 0) 
                
                # Extracting number of rows 
                print('there are ' + str(sheet.nrows) + ' rows in this sheet')

                COLLECTION = sheet_names[i]
                print(COLLECTION)
                mycol = mydb[COLLECTION]
                header = sheet.row_values(0)
                print('header')
                print(header)
                for j in range(1,sheet.nrows):
                    row = sheet.row_values(j)
                    tmp = {'SheetName':COLLECTION}
                    for k in range(len(header)):
                        value = row[k]
                        if value == '':
                            value = 0
                        tmp.update({header[k]:value})
                    data.append(tmp)
                # print(data)
                x = mycol.insert_many(data)

            myclient.close()
            message = 'Successfull uploaded...'
        except:
            message = "Only Excel files will support"
        return message
    
    #### 13/07/2020 Code added Classes... 
    def create_database():

           Pass
    def import_create_collection():

       pass
    def delete_collection():

           Pass
    def insert_dataframes(ParamID, dataframe, share_price_data, exchange, start_date, industry_classification, end_date, industry_sector):
        """
        -- After we converted from CSV data to Dataframes we are inserting into Database...
        -- ParamID -- Dataframe Name
        -- dataframe -- data_dict is a object data...

        """

        df = dataframe
        paramId = ParamID
        data_dict = df.to_dict("records")  ## converting into Dictionary from DF
        company.insert({"id":"User1","ParamID":paramId, "dataframe":data_dict, "share_price_data":share_price_data, "exchange": exchange, "start_date": start_date, "industry_classification": industry_classification, "end_date": end_date, "industry_sector":industry_sector, "Status":"False"})
        
    def get_dataframes_ByID(paramID):
        """
        ## Depends on Selection of ParamID from Dropdown selection we will get data in Dataframe...
        ParamID  --  Selected Dropdown value to check in MongoDB

        """
        paramId = str(paramID)
        query = {"ParamID":paramId}
        my_dict = company.find_one(query)
        final_df = pd.DataFrame.from_dict(my_dict['dataframe'])  ## Dict 2 Dataframe...

        return final_df
    
    # getting json data from mongodb table 
    def get_data_dict_by_id(paramID):
        """
        ## Depends on Selection of ParamID from Dropdown selection we will get data in Dataframe...
        ParamID  --  Selected Dropdown value to check in MongoDB

        """
        paramId = str(paramID).strip()
        query = {"ParamID":paramId}
        my_dict = company.find_one(query)
        return my_dict['dataframe']

    def get_param_by_paramid(paramID):
        """
        its takes the file name and gives all the params or headers in the file
        """
        paramId = str(paramID)
        query = {"ParamID":paramId}
        my_dict = company.find_one(query)
        get_dict = my_dict['dataframe']
        for i in get_dict:
            key_list = list(i)
        return key_list 



    def get_dataframes():
        """
        ## Get all dataframes... to bind 
        """
        params = []
        for i in company.find():
            #print(i['ParamID'])
            params.append(i['ParamID'])
            
        return params
    def insert_excel_mul(all_df_dict):
        """
        After Excel read all the sheets data as individual Dataframes inserting into MongoDB as

        i == Sheet name
        data_dict == Dataframes each excel sheet...

        """

        all_dfs = all_df_dict
        mycol = mytesting["Dataframes"]
        i = 0 
        for i in all_dfs.keys():
            for j in all_dfs.values():
                j.columns=j.columns.str.replace('.','_')
                data_dict = j.to_dict("records")
            mycol.insert({"id":"User1","ParamID":i,"dataframe":data_dict})
    
    ## 22/07/2020 For Strategies creation...
    def insert_creatstrategy(paramdata,newstrategy,strategyname,parameterkey,Benchmark,comments):
        message = BusinessLogicClass.check_Strategy_ByParamID(paramdata)

        print('This checking message',message)
        if message == True:
            Stra_list = DatalayersClass.getStrategies()
            return Stra_list
        else:
            paramId = paramdata
            data_dict = newstrategy.to_dict("records")  ## converting into Dictionary from DF
            mystrategies.insert({"id":"User1","ParamID":paramId,"StrategyName":strategyname,"ParameterKey":parameterkey,"Benchmark":Benchmark,"StrategyDF":data_dict,"Comments": comments})
            return True
    
    def insert_creattreatment(treatment_by, correlation, math_operators, industry, strategyname, treatment_name, wieghtage, param_name):

        response = treatment.insert({"strat_name":strategyname, "treatment_name":treatment_name, "treatment_by":treatment_by, "correlation":correlation, "math_operators": math_operators, "industry":industry})
        print("[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[]]]]]]", response)
        for (a, b) in zip(wieghtage, param_name):
            treat_param.insert({"treatment_id":ObjectId(response), "wieghtage":a, "param_name":b })
        # execute_computations.delay(treatment_by, correlation, math_operators, industry, strategyname, treatment_name, wieghtage, param_name, str(response))
        
        return True

    def insert_computations(response, wieghtage, param_name, Trans, Df9, treatment_df, my_dfs):
        for (a, b) in zip(wieghtage, param_name):
            treat_param.insert({"treatment_id":response, "wieghtage":a, "param_name":b })
    
        # combinations insertions
        data_dict = Trans.to_dict("records")
        Df9_dict = Df9.to_dict("records")
        treatment_df = treatment_df.to_dict("records")
        treatments_combinations.insert({"treatment_id":response, "treatment_df":treatment_df ,'combinations_quartiles':data_dict, "unique_combinations":Df9_dict})

        # my_dfs insertion 
        for i in my_dfs:
            my_df_dic = i.to_dict("records")
            mydict = { "treatment_id":response,"MyDf_s": my_df_dic }
            treat_all_dataframe.insert(mydict,check_keys=False)
        
        # treat
        return True


    
    def update_treatment_details(wieghtage, param_id, treatment_by, correlation, math_operators, industry, treatment_name, treat_id):
        
        myquery = { "_id": ObjectId(treat_id) } 
        newvalues = { "$set": { "treatment_name":treatment_name,
                                "treatment_by":treatment_by,"correlation":correlation,"math_operators" :math_operators,
                                "industry":industry} }
        treatment.update_many(myquery,newvalues)

        for (a, b) in zip(wieghtage, param_id):
            myqueryparam = {"_id" : ObjectId(b) }
            newvalues = { "$set": { "wieghtage":a } }
            treat_param.update_many(myqueryparam,newvalues)

    

    def getStrategies():
        Stratgies_list = []
        mystrategies = mydb['Mystrategies']
        for strategy in mystrategies.find():

            Stratgies_list.append(strategy)
        
        return Stratgies_list
    
    def stratergy_by_id(strat_id):
        stratergy_id = str(strat_id)
        my_dict = mystrategies.find_one({'_id': ObjectId(stratergy_id) })

        return my_dict
    
    def get_dataframes_by_stratergyname(strat_name):
        StrategyName = str(strat_name)
        query = {"StrategyName":StrategyName}
        my_dict = mystrategies.find_one(query)
        StrategyDF = pd.DataFrame.from_dict(my_dict['StrategyDF'])  ## Dict 2 Dataframe...

        return StrategyDF


    def getTreatments():
        Treatment_list = []
        treatment = mydb['Treatment']
        for treat in treatment.find():
            Treatment_list.append(treat)
        
        return Treatment_list

    def treatment_by_id(paramID):
        paramId = str(paramID)
        my_dict = treatment.find_one({'_id': ObjectId(paramId) })

        return my_dict

    def get_benchmark_by_strat(strat_name):
        my_dict = mystrategies.find_one({'StrategyName': strat_name })

        return my_dict
    
    def get_treatment_By_stratergy(strat_name):
        my_dict = treatment.find({'strat_name': strat_name})
        return my_dict


    def treatment_param_by_id(paramID):
        paramId = str(paramID)
        from bson.objectid import ObjectId 
        my_dict = treat_param.find({'treatment_id': ObjectId(paramId) })
        print("==========?", my_dict)
        return my_dict
    

    
                          
    def insert_tca(unique_no,brokername,country_name,currency,Investee_currency,deliverybrokage,ltcgtax,othercharges,purchasetype,purchaserate,quantity,comments):

        tca_data.insert({'UserID':"UID_101","TCA_ID":unique_no,"Broker_Name":brokername, "Country_Name":country_name,
        
                         "Purchase_Currency":currency,"Investee_Currency":Investee_currency,"Delivery_Brokage" :deliverybrokage,
                         
                          "Ltcg_Tax":ltcgtax, "Other_Charges":othercharges,"Purchasetype":purchasetype,"purchaserate":purchaserate,
                          
                          "Quantity" : quantity , "Purchase_Date":datetime.datetime.now() , "Comments":comments})

        return "Successfully Inserted"
    def read_tca():
        tca_list = []
        mystrategies = mydb['TCA']
        for strategy in mystrategies.find():

            tca_list.append(strategy['TCA_ID'])
        
        return tca_list
    def tca_by_id(paramID):

        paramId = str(paramID)
        query = {"TCA_ID":paramId}
        my_dict = tca_data.find_one(query)

        #mytca_df = pd.DataFrame.from_dict(my_dict)

        return my_dict
    def get_tca():
        TCA_List = []
        mytca = mydb['TCA']
        for tca in mytca.find():

            TCA_List.append(tca)
        
        return TCA_List

    def update_tca(unique_no,brokername,country_name,currency,Investee_currency,deliverybrokage,ltcgtax,othercharges,purchasetype,purchaserate,quantity,comments):

        print('Came into Update')
        myquery = { "TCA_ID": unique_no } 

        newvalues = { "$set": { "Broker_Name":brokername, "Country_Name":country_name,
        
                         "Purchase_Currency":currency,"Investee_Currency":Investee_currency,"Delivery_Brokage" :deliverybrokage,
                         
                          "Ltcg_Tax":ltcgtax, "Other_Charges":othercharges,"Purchasetype":purchasetype,"purchaserate":purchaserate,
                          
                          "Quantity" : quantity ,"Purchase_Date":datetime.datetime.now(), "Comments":comments} }

        tca_data.update_many(myquery,newvalues)
        print('updated success')


    def insert_param_mapping(paramId, parameter, param_savart):

        param_mapping.insert({'ParamId':paramId ,'Param_Name':parameter ,"Param_Savart":param_savart, "is_deleted":1 })
        return "Successfully Inserted"

    def update_param_mapping(parammappingId, paramId, parameter, param_savart):
        myquery = { "_id": ObjectId(parammappingId) } 
        newvalues = { "$set": {'ParamId':paramId ,'Param_Name':parameter ,"Param_Savart":param_savart} }
        param_mapping.update_many(myquery,newvalues)
    
    def get_param_mapping():
        # mapping = []
        param_mapping = mydb['ParamMapping']
        return param_mapping.find()

    def get_param_mapping_by_id(id):
        parammappId = str(id)
        my_dict = param_mapping.find_one({'_id': ObjectId(parammappId) })
        my_dict['_id'] = str(my_dict['_id'])
        return my_dict

    def get_file_metadata():
        # mapping = []
        company= mydb["Myparameters"]
        return company.find()

    def get_return_riskviews():
        return_risks_ = []
        return_risks_views = mydb["Return-Views"]
        for return_views in return_risks_views.find():
            return_risks_.append(return_views['Return_Risks_Views'])
        return return_risks_
    
    def get_treatment_dfs(treat_id, output_measure, parameter_list):
        treatment_id = str(treat_id)

        if output_measure == "combination_quartile_view":
            my_dict = treatments_combinations.find_one({'treatment_id': ObjectId(treatment_id) })
            TreatmentDf = pd.DataFrame.from_dict(my_dict['combinations_quartiles'])


        if output_measure == "quartile_view":
            my_dict = treatments_combinations.find_one({'treatment_id': ObjectId(treatment_id) })
            Df = pd.DataFrame.from_dict(my_dict['treatment_df'])

            #Quartile
            Quartiles = Df.copy()
            if len(parameter_list) == 0:
                TreatmentDf = Quartiles
            else:
                TreatmentDf = Quartiles[parameter_list]

                for i in range(1,len(TreatmentDf.columns[1:])):
                #     Data_h = Data_e.copy()
                    col = str(TreatmentDf.columns[i])
                    TreatmentDf[col+'_Rank'] = TreatmentDf.iloc[:,i].rank(method = 'first',ascending=0)
                L = TreatmentDf.columns.get_loc('Shareprice_Appriciation') + 1
                col = TreatmentDf.iloc[: ,L:]
                TreatmentDf['Average_Rank'] = col.mean(axis=1).round()
                TreatmentDf["Quartiles"] = pd.qcut(TreatmentDf['Average_Rank'].rank(method='first'), int(np.sqrt(TreatmentDf.shape[0])) , labels=["Q1", "Q2", "Q3","Q4","Q5","Q6","Q7"])
        
        if output_measure == "rank_view_all":
            my_dict = treatments_combinations.find_one({'treatment_id': ObjectId(treatment_id) })
            DF = pd.DataFrame.from_dict(my_dict['treatment_df'])
            Ranking = DF.copy()
            if len(parameter_list) == 0:
                TreatmentDf = Ranking
            else:
                TreatmentDf = Ranking[parameter_list]
                for i in range(1,len(TreatmentDf.columns[1:])):
                #     Data_h = Data_e.copy()
                    col = str(TreatmentDf.columns[i])
                    TreatmentDf[col+'_Rank'] = TreatmentDf.iloc[:,i].rank(method = 'first',ascending=0)
                # Ranks.head()
        
        if output_measure == "rank_view_year":
            my_dict = treatments_combinations.find_one({'treatment_id': ObjectId(treatment_id) })
            TreatmentDf = pd.DataFrame.from_dict(my_dict['treatment_df'])
        
        if output_measure == "parameter_view":
            my_dict = treatments_combinations.find_one({'treatment_id': ObjectId(treatment_id) })
            DF = pd.DataFrame.from_dict(my_dict['treatment_df'])
            TreatmentDf = DF.copy()
            if len(parameter_list) == 0:
                TreatmentDf = TreatmentDf
            else:
                TreatmentDf = TreatmentDf[parameter_list]


        if output_measure == "industry_view":
            my_dict = treatments_combinations.find_one({'treatment_id': ObjectId(treatment_id) })
            TreatmentDf = pd.DataFrame.from_dict(my_dict['treatment_df'])

        return TreatmentDf

    def get_treatment_dfs_by_id(treat_id):
        treatment_id = str(treat_id)
        my_dict = treatments_combinations.find_one({'treatment_id': ObjectId(treatment_id) })
        TreatmentDf = pd.DataFrame.from_dict(my_dict['treatment_df'])

        return TreatmentDf
    
    def get_dfs_by_id(treat_id):
        treatment_id = str(treat_id)
        my_dict = treatments_combinations.find_one({'treatment_id': ObjectId(treatment_id) })
        CombinationDf = pd.DataFrame.from_dict(my_dict['combinations_quartiles'])
        TreatmentDf = pd.DataFrame.from_dict(my_dict['treatment_df'])
        UniqueDf = pd.DataFrame.from_dict(my_dict['unique_combinations'])



        return CombinationDf,TreatmentDf,UniqueDf
    


    


            



        





        

        


## This the BusinessLayer
class BusinessLogicClass():

    """
    This Class we used to write into logical functions...

    
    """
    def __init__(self):

        return self
    
    def read_datatable(selected_col):
        #myclient , mydb = get_connection()
        """
        retrieve the data from selected collection which is Selected_Col
        retrieved data convert into Dataframe using Pandas...
        returns table_df...
        """
        com_paras = mydb[selected_col]
        table_df = pd.DataFrame(list(com_paras.find()))

        return table_df

    def  edit_data(customerid,filename):


        # obj = read_cutomer(customerId)

        # get_collections()
        # create_collection()
       
        # return 'messgae'
        pass
     
    def delete_data():

        pass
    

    def  get_data(customerid,filename):
        #obj = read_cutomer(customerId)
        #get_collections(obj.database)
        
        #return df
        pass
    def Mul_Excel_DF(workbook_url):
        """
        Converting Excel workbook which has multiple worksheets into Individual Datatframes...

        all_dfs is a dictionary Object with {key:value} eg{"sheetname":"data"}

        """

        all_dfs = pd.read_excel(workbook_url, sheet_name=None)
        #s = type(all_dfs)
        #print(s)

        return all_dfs

    def grid_test(wm_df):
        """
        JUSTpy Grid functionaliy code... 

        https://justpy.io/grids_tutorial/grid_events/ 
        
        """

        wp = jp.WebPage()
        print('This WF_DF',type(wm_df))
        grid = wm_df.jp.ag_grid(a=wp)
        grid.options.pagination = True
        grid.options.paginationAutoPageSize = True
        grid.options.columnDefs[0].cellClass = ['text-white', 'bg-blue-500', 'hover:bg-blue-200']
        for col_def in grid.options.columnDefs[1:]:
            col_def.cellClassRules = {
                'font-bold': 'x < 20',
                'bg-red-300': 'x < 20',
                'bg-yellow-300': 'x >= 20 && x < 50',
                'bg-green-300': 'x >= 50'
            }
        print('Hello',type(wp))
        return wp

    def import_files_intoDF():
        """
        Read the imported files from Documents folders... convert into Final DF...

        Here we are calling 2 other methods which are..  converted_df , mydf 
        -- converted_df takes all the filenames from Document Folder... and return individual Dataframes...

        -- mydf == takes dataframes list and consolidated as single dataframe if all the dataframes have 
                    same identical columns...
                    Return object Consolidated Dataframes... or Message that not identical...
    
        """

        print('Path',gb.glob("./Quant_App/documents/*"))
        file_names = []
        for j in gb.glob("./Quant_App/documents/*"):
            j = j.split("\\")[-1]
            file_names.append(j)
            dataframes= BusinessLogicClass.converted_df(file_names)
            final_df = BusinessLogicClass.mydf(dataframes)
        # print("------------->", j)
        return final_df

    def converted_df(file_names):
        """
        converted_df takes all the filenames from Document Folder... and return individual Dataframes..

        return object is List of Dataframes... dataframes [ ]


        """
        #print('Converted',file_names)
        #print(type(file_names))
        excel_f = file_names
        dataframes = [ ]
        for read_i in excel_f:
            if read_i.split('.')[-1] == 'xlsx':
                #print('Filename',read_i)
                #read_i = os.getcwd() + "\\documents\\" + read_i
                #print(read_i)
                read_file = pd.read_excel(r"/home/simran/Desktop/Vantage_quant_copy/" + read_i)
                #print('readedFiles')
                convertedfile_name = 'Converted_'+ read_i.split('.')[0] + '.csv' 
                read_csv = read_file.to_csv(convertedfile_name, index = None, header=True)
                #print('hello')
                #print(convertedfile_name)
                #df.append(convertedfile_name)
                df = pd.read_csv(convertedfile_name)
                dataframes.append(df)

            elif read_i.split('.')[-1] == 'csv':
                #print(read_i)
                #df.append()
                df = pd.read_csv(r"/home/simran/Desktop/Vantage_quant_copy/" + read_i)
                #df = read_i.split('.')[0] + '_'  + 'DF'
                dataframes.append(df)
        return dataframes
    
    def mydf(dl):
        """
        mydf == takes dataframes list and consolidated as single dataframe if all the dataframes have 
                    same identical columns...
                    Return object Consolidated Dataframes... or Message that not identical...
        """
        print(type(dl))
        i = 0
        ## To show if two dataframes are not Identical...
        message = 'Sorry the selected files are NOT Identical with Columns...Please upload files with Identical Columns'
        if len(dl) > 1:
            for i in range(len(dl)-1):
                if len(dl[i].columns)  == len(dl[i+1].columns):
                    df = pd.concat([dl[i],dl[i+1]])  ## ignore_index = True
                    i+= 1
                else:
                    print('Else inside For DF')
                    df = message 
            print('Inside FOR DF:',type(df))
            return df
        else:
            print('Else DF')
            df = dl[i]
            return df

    def get_filteryears_list(final_df):
        """
        If Dataframe has "Year" column then Get all the years into list in Unique...
        Returns 
            -- Years list or Empty list..

        """
        s = final_df
        em_list = []
        year_ = final_df.columns.to_list()
        if 'Year' in year_:
            f_years = final_df['Year'].unique().tolist()
            return f_years
        else:
            return em_list
    
    def get_filterdatabyYear(df,selectedYear):
        """
        Filter dataframes by Year Feature...

        returns -- Filtered Dataframe...

        """

        print('get_byyear',type(df))
        print('get_',selectedYear)
        df_byyear = df[df['Year'] == selectedYear]

        return df_byyear

    def Users_login(UserEmail,password):

        """
        Authentication of USER Creadentials...

        USER name and Password
        """
        
        myquery = {"User EmailID":UserEmail,"Password": password}

        mydoc = mycol.find(myquery)
        
        #print(mydoc)
        Status = ""
        for i in mydoc:
            if i["User EmailID"] == str(UserEmail) and i["Password"] == str(password):
                if i['Status'] == 'Activate':
                    #print('Welcome to Login page')
                    Status = Status + "Success Full Login"

            else:
                Status = Status + "Wrong Credentials..."
        return Status
     ## 22/07/2020 --SA For Strategies and Treatment creations   

    def get_dataframe_parameters(strategyname):

        strategy_df = DatalayersClass.get_dataframes_ByID(strategyname)
        print(type(strategy_df))

        strategy_columns = strategy_df.columns.tolist()

        return strategy_columns

    ## Checking IF Strategy Name already in DB    
    def check_strategyname(startegyname):

        _strategynames = []
        for i in mystrategies.find():
            _strategynames.append(i['StrategyName'])
        if startegyname in _strategynames:
            return True
        else:
            return False
    def check_Strategy_ByParamID(ParamID):

        _parametersDataframe = []
        for i in mystrategies.find():
            _parametersDataframe.append(i['ParamID'])
        if ParamID in _parametersDataframe:
            return True
        else:
            return False   
    









### 13/07/2020 --SANDEEP -- ###

class Company():

    class Company():
        """
        Model Class... Its create a

        SA - I tries to run the code models.Model ... Its on HOLD...
        """
        Company_ID = models.CharField()

        pass

