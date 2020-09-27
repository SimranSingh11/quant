from django.shortcuts import render
import os
import pandas as pd
from django.views.decorators.csrf import csrf_exempt
from Quant_App.models import DatalayersClass,BusinessLogicClass
import os
import shutil 
import justpy as jp    ## For Justpy Grid... https://justpy.io/   ## Not using
#from DatalayersClass import get_collections
import datetime
from django.shortcuts import redirect
from django.http import JsonResponse
import json

# importing according to jupyter notebook
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
import matplotlib.pyplot as plt
# %matplotlib inline
import time
import seaborn as sns

from Quant_App.compute import treatment_quartiles_df,automate_Raking,check_consequtive_fall_dfs,get_summary,transpose_rowindex,get_bestparametes_Combinations_unique

@csrf_exempt
def show_data(request):
    """
    Fun description: to display selected file information in tabular form...

    This view function show excel collections into dropdown >> get_collections()...
    retrieving the selected excel file into page to display... >> read_datatable(file_name)
     read_datatable  returns dataframe...
     dataframe converted into html and display in htmlp page...
     file_name : to show the message that what file we selected... 
    """
    if request.method == 'POST':
        file_name = request.POST["selected_file"]
        finaldf =  BusinessLogicClass.read_datatable(file_name)
        #wp = jp.justpy(BusinessLogicClass.grid_test(finaldf))

        #wp = BusinessLogicClass.just_py_test(finaldf)
        #print(wp)
        coll_list = DatalayersClass.get_collections()  # after pick the filename reload the page with file collections
        table_content = finaldf.to_html()
        context = {'table_content': table_content}
        return render(request,'home.html',{'context':table_content,'coll_list':coll_list,'file':file_name})

    coll_list= DatalayersClass.get_collections()  

    return render(request,'home.html',{'coll_list':coll_list})


def fileupload(request):
    """
    Fun desc: File upload choose Excel and CSV format files and insert into MONGODB..

    uploading file from local machine to local folder documents/ ...
    
    insert_data_into_mongo(doc_path)  is updated into MongoDB. >> excelinsert.py 

    After upload succefully show success message...... 
    """
    if request.method == 'POST':
        # meta data
        share_price_data = request.POST.get("share_price_data")
        exchange = request.POST.get("exchange")
        start_date = request.POST.get("start_date")
        industry_classification = request.POST.get("industry_classification")
        end_date = request.POST.get("end_date")
        industry_sector = request.POST.get("industry_sector")

        f = request.FILES.getlist('file')
        for i in f:
            global filename
            filename = str(i)   
            #print('This is I Object:',i)
            with open('Quant_App/documents/' +  str(i), 'wb+') as destination:
                 for chunk in i.chunks():
                     destination.write(chunk)            
            doc_path = 'Quant_App/documents/' + str(i)
            #message = DatalayersClass.insert_data_into_mongo(doc_path)
        
        filename = filename.split('.')[0]
        message = ''
        final_df = BusinessLogicClass.import_files_intoDF()
        ## This below path is used to delete the files from Document folders...
        # empty_dir = r"/home/simran/Desktop/Django/Vantage_Quant/Quant_App/documents"
        empty_dir = r"/home/simran/Desktop/Vantage_quant_copy/Quant_App/documents"
        shutil.rmtree(empty_dir)
        ## Actually its deleted the folder it self... so we are creating Folder again...
        os.mkdir("/home/simran/Desktop/Vantage_quant_copy/Quant_App/documents")
        if type(final_df) != str:
            final_df.columns=final_df.columns.str.replace('.','_')  ## If Columsn has (.) in name
            x = datetime.datetime.now()
            paramId = filename+"_"+ str(x.strftime("%m%d%H%M%S"))
            DatalayersClass.insert_dataframes(paramId, final_df, share_price_data, exchange, start_date, industry_classification, end_date, industry_sector)
            params = DatalayersClass.get_dataframes()
        else:
            pass

        if type(final_df) != str:
            list_years = BusinessLogicClass.get_filteryears_list(final_df)
        else:
            pass
        #print(list_years)Quant_App/documents
        
        if type(final_df) == str :
            print('This is the message',final_df)
            return render(request,'upload.html',{'message': message,'df_message':final_df})
        else:
            final_df.columns=final_df.columns.str.replace('.','_')  ## If Columsn has (.) in name
            x = datetime.datetime.now()
            paramId = filename+"_"+ str(x.strftime("%m%d%H%M%S"))
            get_dict = DatalayersClass.get_data_dict_by_id(paramId)
            value_list=[]
            for i in get_dict:
                key_list = list(i)
                values = i.values()
                value_list.append(values)
            # table_content1 = final_df.to_html() 
            # context = {'table_content1': table_content1}
            #return render(request,'upload.html',{'message': message,'table_content1':table_content1})
            return render(request,'upload.html',{'key_list':key_list, 'value_list':value_list, 'params':params})

    return render(request,'upload.html')
    
def filtered_data(request):
    """
    1. This functionality will bind Final Dataframe data as Parameters data into First Dropdown...
    2. If the Selected DF has 'Year' Columns then It will filter by Year too...

    Retreiving all the Dataframes

    """
    if request.method == 'POST' and 'filterbydata' in request.POST :
        global filtered_year
        filtered_year = request.POST["filter_bydata"]
        final_df = DatalayersClass.get_dataframes_ByID(filtered_year)
        table_content1 = final_df.to_html()
        context = {'table_content1': table_content1}
        params = DatalayersClass.get_dataframes()
        if type(final_df) != str:
            list_years = BusinessLogicClass.get_filteryears_list(final_df)
        else:
            pass
        return render(request,'filtered.html',{'table_content1':table_content1,'params':params,'years':list_years})
    elif request.method == 'POST' and 'filterbyyear' in request.POST:

        fyear = request.POST["Filter_byyear"]
        mydf = DatalayersClass.get_dataframes_ByID(filtered_year)
        final_df = BusinessLogicClass.get_filterdatabyYear(mydf,fyear)
        table_content1 = final_df.to_html()
        context = {'table_content1': table_content1}
        params = DatalayersClass.get_dataframes()
        if type(final_df) != str:
            list_years = BusinessLogicClass.get_filteryears_list(final_df)
        else:
            pass

        return render(request,'filtered.html',{'table_content1':table_content1,'params':params,'years':list_years})

def User_login(request):
    
    if request.method == 'POST':

        uname = request.POST["uname"]
        pwd = request.POST["psw"]

        print('Username',uname)

        print("Password",pwd)
        
        Status = BusinessLogicClass.Users_login(uname,pwd)
        print(Status)

        if Status == "Success Full Login":

            return redirect('Viewstrategies')  

        else:
            message = "USER Credentials Wrong..."

            return render(request,"Userlogin.html",{"Message":message})

    return render(request,"Userlogin.html")

def get_oldstrategy(request):
    """
    ## Get all the startegies which already created ... get all Strategies from MongoDB as Dataframes...

    """
    
    params = DatalayersClass.get_dataframes()

    if request.method == 'POST':
        paramdata = request.POST["filter_strategy"]
        get_dict = DatalayersClass.get_data_dict_by_id(paramdata)
        value_list=[]
        for i in get_dict:
            key_list = list(i)
            values = i.values()
            value_list.append(values)

        return render(request,"strategy.html",{'key_list':key_list, 'value_list':value_list, 'params':params})

    return render(request,"strategy.html",{'params':params})
def new_strategy(request):
    """
    Fun desc: File upload choose Excel and CSV format files and insert into MONGODB..

    uploading file from local machine to local folder documents/ ...
    
    insert_data_into_mongo(doc_path)  is updated into MongoDB. >> excelinsert.py 

    After upload succefully show success message...... 
    """

    ## Not using sofar...
    if request.method == 'POST':
        f = request.FILES.getlist('file')
        for i in f:
            global filename
            filename = str(i) 
            print('This is I Object:',i)
            
            with open('Quant_App/documents/' +  str(i), 'wb+') as destination:
                 for chunk in i.chunks():
                     destination.write(chunk)            
            doc_path = 'Quant_App/documents/' + str(filename)
            print(doc_path)

            all_df_dict = BusinessLogicClass.Mul_Excel_DF(doc_path)
            #print(all_df_dict)
            DatalayersClass.insert_excel_mul(all_df_dict)
    
    return render(request,"newstrategy_s.html")

def create_strategy(request):
    """
    ## Get all the startegies which already created ... get all Strategies from MongoDB as Dataframes...

    """
    params = DatalayersClass.get_dataframes()
    if request.method == 'POST' and 'viewdataframe' in request.POST :
    #if request.method == 'POST':
        paramdata = request.POST["viewstrategydata"]
        final_df = DatalayersClass.get_dataframes_ByID(paramdata)
        print(type(final_df))
        table_content1 = final_df.to_html()
        context = {'table_content1': table_content1}

        return render(request,"createstrategy.html",{'table_content1':table_content1,'params':params})
    elif request.method == 'POST' and 'savestrategy' in request.POST :
        paramdata = request.POST["viewstrategydata"]
        newstrategy = DatalayersClass.get_dataframes_ByID(paramdata)
        strategyname = request.POST["strategyname"]
        parameterkey = request.POST["parameterkey"]
        Benchmark = request.POST["Benchmark"]
        comments = request.POST["comments"]
        print("----------------->",paramdata,newstrategy,strategyname,parameterkey,Benchmark,comments )
        

        return_message = DatalayersClass.insert_creatstrategy(paramdata,newstrategy,strategyname,parameterkey,Benchmark,comments)
        #print('This is Return Message',return_message)
        if type(return_message) == list:
            message = "There is Strategy already created on this " + paramdata
            Strat_list = return_message 
            print(type(Strat_list))
            return render(request,"Viewstratgies.html",{'params':params,'return_message':message,"Strat_list":Strat_list})
        else:
            message = "Create a new Strategy with name " + strategyname
            return render(request,"createstrategy.html",{'params':params,'return_message':message})

    elif request.method == 'POST' and 'createtreatment' in request.POST :
        paramdata = request.POST["viewstrategydata"]
        print("------------>",paramdata)
        strategyname = request.POST.get("strategyname")
        parameterkey = request.POST.get("parameterkey")
        Benchmark = request.POST.get("Benchmark")
        
        
        parameters = BusinessLogicClass.get_dataframe_parameters(paramdata)
       

        return render(request,'treatment.html',{'paramets':parameters, 'strategyname': strategyname, 'parameterkey': parameterkey, 'Benchmark':Benchmark})

    return render(request,"createstrategy.html",{'params':params})

# meta deta with file
def get_file_metadata(request):
    data = DatalayersClass.get_file_metadata()

    return render(request,'file_metadata.html',{'data' : data })



# treatement view
def treatment(request):
    paramid = request.GET["parameter_id"]
    stratergy_name = request.GET["stratergy_name"]
    strat_id = request.GET["strat_id"]
    param_list = DatalayersClass.get_param_by_paramid(paramid)
    
    return render(request,'treatment.html',{'paramets':param_list, 'strategyname': stratergy_name, 'strat_id': strat_id})



# Creating treatment with computations************** important
def create_treatment(request):
    wieghtage = request.POST.getlist("wieghtage")
    param_name = request.POST.getlist("param_name")
    treatment_by = request.POST.get("treatment_by")
    correlation = request.POST.get("correlation")
    strategyname = request.POST.get("strategyname")
    math_operators = request.POST.get("math_operators")
    industry = request.POST.get("industry")
    treatment_name = request.POST.get("treatment_name")
    strat_id = request.POST['strat_id']
    
    return_message = DatalayersClass.insert_creattreatment(treatment_by, correlation, math_operators, industry, strategyname, treatment_name, wieghtage, param_name)    

    print("------------>", return_message)

    from django.urls import reverse
    from urllib.parse import urlencode
    base_url = reverse('ViewSingleStratergy')  # 1 /products/
    query_string =  urlencode({'stratergy_id': strat_id})  # 2 category=42
    url = '{}?{}'.format(base_url, query_string)  # 3 /products/?category=42
    if return_message == True:
        return redirect(url) 
    else:
        return redirect(url)






def update_treatment(request):
    treat_id = request.GET['treat_id']
    get_list = DatalayersClass.treatment_by_id(treat_id)
    get_params_list = DatalayersClass.treatment_param_by_id(treat_id)

    return render(request,'edit_treatment.html',{'get_list' : get_list, 'get_params_list' : get_params_list })

def update_treatment_detail(request):

    wieghtage = request.POST.getlist("wieghtage")
    param_id = request.POST.getlist("param_id")
    treatment_by = request.POST.get("treatment_by")
    correlation = request.POST.get("correlation")
    math_operators = request.POST.get("math_operators")
    industry = request.POST.get("industry")
    treatment_name = request.POST.get("treatment_name")
    treat_id = request.POST.get("treat_id")
    print("------------->", wieghtage, param_id, treatment_by, correlation, math_operators, industry, treatment_name)

    DatalayersClass.update_treatment_details(wieghtage, param_id, treatment_by, correlation, math_operators, industry, treatment_name, treat_id)
    return redirect('view_treatment')  


def getall_startegies(request):
    
    Str_list = DatalayersClass.getStrategies()

    return render(request,'Viewstratgies.html',{'Strat_list':Str_list})

def get_single_stratergy(request):
    strat_id = request.GET["stratergy_id"]
    get_list = DatalayersClass.stratergy_by_id(strat_id)
    stratergy_name = get_list['StrategyName']
    get_treat_by_stratergy = DatalayersClass.get_treatment_By_stratergy(stratergy_name)
    count_treat = get_treat_by_stratergy.count()
    return render(request,'single_stratergy.html',{'get_list' : get_list, 'treatment_list':get_treat_by_stratergy, "count_treat": count_treat})


def stratergy_treatment_view(request):
    treat_id = request.GET["treat_id"]
    get_treat_data = DatalayersClass.treatment_by_id(treat_id)
    strat_name = get_treat_data['strat_name']
    get_strat_data = DatalayersClass.get_benchmark_by_strat(strat_name)
    get_treat_param = DatalayersClass.treatment_param_by_id(treat_id)
    return render(request,'treatment_view.html',{'treat_list': get_treat_data, 'strat_data': get_strat_data, 'param_list': get_treat_param})


def getall_treatments(request):
    
    Str_list = DatalayersClass.getTreatments()
    return render(request,'Viewtreatment.html',{'Strat_list':Str_list})

## Creating TCA
def create_tca(request):

    if request.method == 'POST':
        brokername = request.POST["brokername"]
        country_name = request.POST["countryname"]
        currency = request.POST["purchasecurrency"]
        Investee_currency = request.POST["investeecurrency"]
        deliverybrokage = request.POST["deliverybrokage"]
        ltcgtax = request.POST["ltcgtax"]
        othercharges = request.POST["othercharges"]
        purchasetype = request.POST["purchasetype"]
        purchaserate = request.POST["purchaserate"]
        quantity = request.POST["quantity"]
        # Purchase_date = request.POST["purchasedate"]
        comments = request.POST["comments"]

        x = datetime.datetime.now()
        year =  x.strftime("%Y")
        date = x.strftime("%d")
        hms = x.strftime("%H%M%S")
        unique_no = "TCA" + "-" + year + "_" + date + "_" + hms

        tca_message = DatalayersClass.insert_tca(unique_no,brokername,country_name,currency,Investee_currency,deliverybrokage,ltcgtax,othercharges,purchasetype,purchaserate,quantity,comments)
        return render(request,'tcacreate.html',{'tca_message':tca_message})

    return render(request,'tcacreate.html')

def view_tca(request):

    get_tca_list = DatalayersClass.get_tca()

    return render(request,'tcaView.html',{"TCA_list":get_tca_list })

def tca_views(request,id):
    # tca_id = get_object_or_404(TCA)
    
    print(id.split("|"))
    get_list = DatalayersClass.tca_by_id(id.split("|")[0])
    print(get_list) 

    if id.split("|")[1] == 'View':
        
        return render(request,'ViewTCA.html',{"get_list":get_list})
    if id.split("|")[1] == 'Edit':
        

        return render(request,'editTCA.html',{"get_list":get_list}) 

def update_tca(request):
    print('UPDATE TCA')

    if request.method == 'POST':
        TCA_ID = request.POST["TCA_ID"]
        print('TCA_ID', TCA_ID)
        brokername = request.POST["brokername"]
        print('Brokername', brokername)
        country_name = request.POST["countryname"]
        print('country_name', country_name)
        currency = request.POST["purchasecurrency"]
        print('currency', currency)
        Investee_currency = request.POST["investeecurrency"]
        print('Investee_currency', Investee_currency)
        deliverybrokage = request.POST["deliverybrokage"]
        print('deliverybrokage', deliverybrokage)
        ltcgtax = request.POST["ltcgtax"]
        print('ltcgtax', ltcgtax)
        othercharges = request.POST["othercharges"]
        purchasetype = request.POST["purchasetype"]
        purchaserate = request.POST["purchaserate"]
        quantity = request.POST["quantity"]

        # Purchase_date = request.POST["purchasedate"]
        comments = request.POST["comments"]



        #TCA_ID,brokername,country_name,currency,Investee_currency,deliverybrokage,ltcgtax,othercharges,purchasetype,purchaserate,quantity,comments

        DatalayersClass.update_tca(TCA_ID,brokername,country_name,currency,Investee_currency,deliverybrokage,ltcgtax,othercharges,purchasetype,purchaserate,quantity,comments)

        return render(request,'tcaView.html') 

# param mapping views

def getall_paramsmapping(request):
    params = DatalayersClass.get_dataframes()
    data = DatalayersClass.get_param_mapping()
    savart_param = DatalayersClass.get_new_param()
    # return render(request,'param_mapping.html',{"params":params, 'data' : data })
    return render(request,'parammapping.html',{"params":params, 'data' : data , 'savart_param':savart_param})

def add_new_param(request):
    params = DatalayersClass.get_dataframes()
    data = DatalayersClass.get_param_mapping()

    # return render(request,'param_mapping.html',{"params":params, 'data' : data })
    return render(request,'new_param.html',{})


def fetch_param_by_file(request, file):
    list_of_params = DatalayersClass.get_param_by_paramid(file)
    # data.append({'params':list_of_params })
    return JsonResponse(list_of_params,safe=False)

def fetch_param_mapping_by_id(request, id):
    list_mapped_param = DatalayersClass.get_param_mapping_by_id(id)
    # data.append({'params':list_of_params })
    return JsonResponse(list_mapped_param)

def create_param_mapping(request):

    if request.method == 'POST':
        paramId = request.POST['file_name']
        parameter = request.POST['parameter']   
        param_savart = request.POST['param_savart']
        DatalayersClass.insert_param_mapping(paramId, parameter, param_savart)
        return redirect('param_mapping')

def create_new_param(request):

    if request.method == 'POST':
        paramname = request.POST['parameter_name']
        formula = request.POST['formula']   
        units = request.POST['units']   
        paramsid = request.POST['paramsid']   
        operators = request.POST['operators']   
        comments = request.POST['comments']   
        DatalayersClass.insert_new_param(paramname, formula, units, paramsid, operators, comments)
        return redirect('new_param')

def update_param_mapping(request):

    if request.method == 'POST':
        parammappingId = request.POST['param_mapping_id']
        paramId = request.POST['file_name_edit']
        parameter = request.POST['parameter_edit']   
        param_savart = request.POST['param_savart_edit']
        DatalayersClass.update_param_mapping(parammappingId, paramId, parameter, param_savart)
        return redirect('param_mapping')

# visuals

# def visual(request):
#     treatments = DatalayersClass.getTreatments()
    
#     if request.method == 'POST':
#         treatment_id = request.POST['treatment_id']
#         df = DatalayersClass.get_dfs_by_id(treatment_id)
#         combination_df = df[0]
#         treat_df = df[1]
#         treatment_df = get_quartile_by_company(treat_df)
#         unique_df = df[2]
#         x_axis_com = combination_df['Row_Indexing'][:20]
#         y_axis_com = combination_df['Q1'][:20]
        
#         x_axis_unique = list(range(0,20))
#         y_axis_unique = unique_df['Q1'][:20]

#         x_axis_treat_not_str = treatment_df['Company Name']
#         x_axis_treat = {str(x) for x in x_axis_treat_not_str}
#         print("================>",x_axis_treat)
#         y_axis_treat = treatment_df['Shareprice_Appriciation']

#         combination_df_altered = combination_df[:20].to_html()
#         unique_df_altered = unique_df[:20].to_html()
#         treatment_df_altered = treatment_df[['Company Name','Shareprice_Appriciation']].to_html()
#         return render(request,'visuals.html',{
#             'treatments':treatments,
#             'x_axis_com':list(x_axis_com),
#             'y_axis_com':list(y_axis_com),
#             'x_axis_unique':x_axis_unique,
#             'y_axis_unique':list(y_axis_unique),
#             'x_axis_treat':x_axis_treat,
#             'y_axis_treat':list(y_axis_treat),
#             "combination_df_altered": combination_df_altered,
#             "unique_df_altered":unique_df_altered,
#             "treatment_df_altered":treatment_df_altered
#             })


#     return render(request,'newvisual.html',{'treatments':treatments }) 

# visual updated code
def visual(request):
    treatments = DatalayersClass.getTreatments()
    
    if request.method == 'POST':
        #treatment_id = "5f6ca3ee3b24926598222deb"
        treatment_id = request.POST['treatment_id']
        print(treatment_id)
        df = DatalayersClass.get_dfs_by_id(treatment_id)
        print(df)
        combination_df = df[0]
        CombiDF = combination_df.to_dict("records")
        CombiDF = combination_df[:10].to_html()
        
        treat_df = df[1]
        print('Before HHH')
        treatment_df = get_quartile_by_company(treat_df)
        print('HHHHH')
        print(treatment_df)
        unique_df = df[2]
        UniqueDF = unique_df.to_dict("records")
        UniqueDF = unique_df[:10].to_html()

        ## For Template Table

        CombinColumns = list(combination_df.columns[1:3])
        Combinational_Tbldf = combination_df.iloc[:10,1:3].to_dict("records")
        Combi_value_list = []
        for i in Combinational_Tbldf:
            value = i.values()
            Combi_value_list.append(value)

        
        UnidfColumns = list(unique_df.columns[:2])
        Unidf_table = unique_df.iloc[:10,:2].to_dict("records")
        Unidf_value_list = []
        for i in Unidf_table:
            value = i.values()
            Unidf_value_list.append(value)

        ## Table Changes

        if len(combination_df) != 0:
            x_axis_com = combination_df['Row_Indexing'][:20]
            y_axis_com = combination_df['Q1'][:20]
        if len(unique_df) != 0:
            x_axis_unique = list(range(0,10))
            y_axis_unique = unique_df['Q1'][:10]

        x_axis_treat_not_str = treatment_df['Company Name']
        x_axis_treat = {str(x) for x in x_axis_treat_not_str}
        print("================>",x_axis_treat)
        y_axis_treat = treatment_df['Shareprice_Appriciation']



        # combination_df_altered = combination_df[:20].to_html()
        # unique_df_altered = unique_df[:20].to_html()
        treatment_df_table =   treatment_df[['Company Name','Shareprice_Appriciation']]
        treatment_df_altered = treatment_df[['Company Name','Shareprice_Appriciation']].to_html()
        Treatment_table_colums= list(treatment_df_table.columns)
        treatment_df_altered_values = treatment_df_table.to_dict("records")
        treatement_values = []
        for i in treatment_df_altered_values:
            value = i.values()
            treatement_values.append(value)

        if len(combination_df) != 0 and len(unique_df) != 0:
              
            return render(request,'newvisual.html',{
                # 'treatments':treatments,
                 "Treatment_table_colums" : Treatment_table_colums,
                "treatement_values"  :treatement_values,

                "CombinColumns" :CombinColumns,
                "Combi_value_list":Combi_value_list,

                "UnidfColumns":UnidfColumns,
                "Unidf_value_list":Unidf_value_list,



                'x_axis_com':list(x_axis_com),
                'y_axis_com':list(y_axis_com),
                'x_axis_unique':x_axis_unique,
                'y_axis_unique':list(y_axis_unique),
                'treatments':treatments,
                'x_axis_treat':x_axis_treat,
                'y_axis_treat':list(y_axis_treat),
                # "combination_df_altered": combination_df_altered,
                # "unique_df_altered":unique_df_altered,
                "treatment_df_altered":treatment_df_altered,
                "UniqueDF" : UniqueDF,
                "CombiDF" : CombiDF

                })

        else:

            return render(request,'newvisual.html',{
                # 'treatments':treatments,
                # 'x_axis_com':list(x_axis_com),
                # 'y_axis_com':list(y_axis_com),
                # 'x_axis_unique':x_axis_unique,
                # 'y_axis_unique':list(y_axis_unique),
                "Treatment_table_colums" : Treatment_table_colums,
                "treatement_values"  :treatement_values,

                'treatments':treatments,
                'x_axis_treat':x_axis_treat,
                'y_axis_treat':list(y_axis_treat),
                # "combination_df_altered": combination_df_altered,
                # "unique_df_altered":unique_df_altered,
                "treatment_df_altered":treatment_df_altered
                })
    #return render(request,'vs.html',{'treatments':treatments })
    return render(request,'newvisual.html',{'treatments':treatments })
    #return render(request,'vs.html',{'x_axis_treat':x_axis_treat,'y_axis_treat':list(y_axis_treat) }) 


def get_quartile_by_company(treat_df):
    Quartiles = treat_df.copy()
    # Quartiles = Quartiles[new_columns_list]
    for i in range(2,len(Quartiles.columns[:-1])):
    #     Data_h = Data_e.copy()
        col = str(Quartiles.columns[i])
        Quartiles[col+'_Rank'] = Quartiles.iloc[:,i].rank(method = 'first',ascending=0)
    L = Quartiles.columns.get_loc('Shareprice_Appriciation') + 1
    col = Quartiles.iloc[: ,L:]
    Quartiles['Average_Rank'] = col.mean(axis=1).round()
    Quartiles["Quartiles"] = pd.qcut(Quartiles['Average_Rank'].rank(method='first'), int(np.sqrt(Quartiles.shape[0])) , labels=["Q1", "Q2", "Q3","Q4","Q5","Q6","Q7"])
    Quartiles = Quartiles.loc[Quartiles['Quartiles'].isin(["Q1"])]
    return Quartiles


# custom view code 
def get_custom_views(request):
    treatments = DatalayersClass.getTreatments()
    params = DatalayersClass.get_dataframes()
    # Dataframe = DatalayersClass.get_Treatment_OPmeasures()
    # DFColumns = list(Dataframe.columns)
    # Dataframe = Dataframe.to_dict("records")

    # return render(request,'custom_view.html',{'treatments':treatments, 'params': params})
    return render(request,'customviews.html',{'treatments':treatments, 'params': params})



def get_all_treat_data(request):
    treatments = DatalayersClass.getTreatments()
    params = DatalayersClass.get_dataframes()

    treatment_id = request.POST['treatment_id']
    parameter_list = request.POST.getlist("parameter")
    output_measure = request.POST['output_measure']

    print("------------>", treatment_id,parameter_list,output_measure) 

    get_treatement_df = DatalayersClass.get_treatment_dfs(treatment_id,output_measure,parameter_list)
    print("0000000000000000>", get_treatement_df) 
    
    if get_all_treat_data=='Empty DataFrame':
        pass
    else:   
        columns = list(get_treatement_df.columns)
        get_treatdf_dict = get_treatement_df.to_dict("records")
        value_list = []
        for i in get_treatdf_dict:
            value = i.values()
            value_list.append(value)

    return render(request,'customviews.html',{'treatments':treatments, 'params': params, "columns":columns, 'value_list':value_list})

def get_params_by_treatment_id(request, id):
    get_treatement_df = DatalayersClass.get_treatment_dfs_by_id(id)
    columns = list(get_treatement_df.columns)
    return JsonResponse(columns,safe=False)


def risk_return_view(request):
    # treatments = DatalayersClass.
    treatments  = DatalayersClass.getTreatments()
    return_risks_ = DatalayersClass.get_return_riskviews()

    # return render(request,'risk_return_view.html',{"treatments":treatments,"return_risks":return_risks_})
    return render(request,'output.html',{"treatments":treatments,"return_risks":return_risks_})


def upload_risk_return_file(request):
    return_risks_ = DatalayersClass.get_return_riskviews()
 
    drop_name = request.POST['file_name']
    f = request.FILES.getlist('file')
    for i in f:
        global filename
        filename = str(i) 
        #print('This is I Object:',i)
        with open('Quant_App/documents/' +  str(i), 'wb+') as destination:
                for chunk in i.chunks():
                    destination.write(chunk)            
        doc_path = 'Quant_App/documents/' + str(i)
        print("------------>", doc_path)

    filename = filename.split('.')[0]
    # common code
    Data = pd.ExcelFile(doc_path)
    
    # years
    years = pd.read_excel(Data, 'Years',skiprows=1)
    years_lastindex = years.columns.get_loc('Share Appreciation for 5 years')+1
    years = years.iloc[:,2:17]

    # months
    monthly = pd.read_excel(Data, 'monthly',skiprows=1,skipfooter=2)
    monthly_lastindex = monthly.columns.get_loc('BDP_Close11') + 1
    monthly = monthly.iloc[:,2:16]
    
    # Daily
    daily = pd.read_excel(Data, 'Daily',skiprows=1)
    Daily = daily.copy()
    for i in range(2,len(Daily.columns)-1):
        j = i + 1
        col = str(Daily.columns[i] + Daily.columns[j] + "_DailyShareprice_Appri")
        Daily[col] = (Daily.iloc[:,j] - Daily.iloc[:,i])/Daily.iloc[:,i]

    F = monthly.copy()
    for i in range(2,len(F.columns)):
        j = i + 1
        col = str(F.columns[i] + F.columns[j] + "_Shareprice_Appri")
        F[col] = (F.iloc[:,j] - F.iloc[:,i])/F.iloc[:,i]

    # sharp ratio
    if drop_name == '(Alpha) Sharpe ratio ':
        new_df = years.copy()
        new_df["Quartiles"] = pd.qcut(new_df['Shareprice_Appriciation'].rank(method='first'), int(np.sqrt(new_df.shape[0])) , labels=["Q7", "Q6", "Q5","Q4","Q3","Q2","Q1"])
        Q1_Port = new_df.loc[new_df['Quartiles'].isin(["Q1"])]
        Portfilio_df  = pd.DataFrame(Q1_Port.groupby('Portfolio')["Shareprice_Appriciation"].median())
        Portfilio_df['Sharp_ratio'] = (Portfilio_df.iloc[0:] - 0.06)/Portfilio_df.iloc[0:].std()
        Portfilio_df = Portfilio_df.reset_index()
        # table_content1 = Portfilio_df.to_html()
        columns = list(Portfilio_df.columns)
        get_treatdf_dict = Portfilio_df.to_dict("records")
        value_list = []
        for i in get_treatdf_dict:
            value = i.values()
            value_list.append(value)

        return render(request,'output.html',{"columns":columns, 'value_list':value_list , "return_risks":return_risks_})
    
    if drop_name == '1 Year Return (Historical)':
        new_df = years.copy()
        new_df["Quartiles"] = pd.qcut(new_df['Shareprice_Appriciation'].rank(method='first'), int(np.sqrt(new_df.shape[0])) , labels=["Q7", "Q6", "Q5","Q4","Q3","Q2","Q1"])
        Q1_Port = new_df.loc[new_df['Quartiles'].isin(["Q1"])]
        Portfilio_df  = pd.DataFrame(Q1_Port.groupby('Portfolio')["Shareprice_Appriciation"].median())
        # table_content1 = Portfilio_df.to_html()
        Portfilio_df = Portfilio_df.reset_index()
        columns = list(Portfilio_df.columns)
        get_treatdf_dict = Portfilio_df.to_dict("records")
        value_list = []
        for i in get_treatdf_dict:
            value = i.values()
            value_list.append(value)

        return render(request,'output.html',{"columns":columns, 'value_list':value_list , "return_risks":return_risks_ })
    
    if drop_name == '3 Year Return (Annualized) (Historical)':
        new_df = years.copy()
        new_df["Quartiles"] = pd.qcut(new_df['Share Appreciation for 3 years'].rank(method='first'), int(np.sqrt(new_df.shape[0])) , labels=["Q7", "Q6", "Q5","Q4","Q3","Q2","Q1"])
        Q1_Port_3years = new_df.loc[new_df['Quartiles'].isin(["Q1"])]
        Portfilio_df_3years  = pd.DataFrame(Q1_Port_3years.groupby('Portfolio')["Share Appreciation for 3 years"].median())
        # table_content1 = Portfilio_df_3years.to_html()
        Portfilio_df_3years = Portfilio_df_3years.reset_index()
        columns = list(Portfilio_df_3years.columns)
        get_treatdf_dict = Portfilio_df_3years.to_dict("records")
        value_list = []
        for i in get_treatdf_dict:
            value = i.values()
            value_list.append(value)

        return render(request,'output.html',{"columns":columns, 'value_list':value_list , "return_risks":return_risks_ })

    if drop_name == '5 Year Return (Annualized) (Historical)':
        new_df = years.copy()
        new_df["Quartiles"] = pd.qcut(new_df['Share Appreciation for 5 years'].rank(method='first'), int(np.sqrt(new_df.shape[0])) , labels=["Q7", "Q6", "Q5","Q4","Q3","Q2","Q1"])
        Q1_Port_5years = new_df.loc[new_df['Quartiles'].isin(["Q1"])]
        Portfilio_df_5years  = pd.DataFrame(Q1_Port_5years.groupby('Portfolio')["Share Appreciation for 5 years"].median())
        # table_content1 = Portfilio_df_5years.to_html()
        Portfilio_df_5years = Portfilio_df_5years.reset_index()
        columns = list(Portfilio_df_5years.columns)

        get_treatdf_dict = Portfilio_df_5years.to_dict("records")
        value_list = []
        for i in get_treatdf_dict:
            value = i.values()
            value_list.append(value)

        return render(request,'output.html',{"columns":columns, 'value_list':value_list , "return_risks":return_risks_ })
    
    if drop_name == 'Annualized Volatility':
        # years_index = years.columns.get_loc('Shareprice_Appriciation')
        new_df = years.copy()
        new_df['Volatality'] = new_df.iloc[:,12:].std(axis=1,skipna = True)
        Volatality = new_df[["Company Name","Shareprice_Appriciation","Share Appreciation for 3 years","Share Appreciation for 5 years","Volatality"]]
        # table_content1 = Volatality.to_html()
        Volatality = Volatality.reset_index()
        columns = list(Volatality.columns)
        get_treatdf_dict = Volatality.to_dict("records")
        value_list = []
        for i in get_treatdf_dict:
            value = i.values()
            value_list.append(value)


        return render(request,'output.html',{"columns":columns, 'value_list':value_list , "return_risks":return_risks_ })
    
    if drop_name == '1 year Maximum Drawdown':
        new_df = years.copy()
        new_df["Quartiles"] = pd.qcut(new_df['Shareprice_Appriciation'].rank(method='first'), int(np.sqrt(new_df.shape[0])) , labels=["Q7", "Q6", "Q5","Q4","Q3","Q2","Q1"])
        Q1_Port_1year = new_df.loc[new_df['Quartiles'].isin(["Q1"])]
        Maximum_Drawdown_1year = (Q1_Port_1year['Shareprice_Appriciation'].min() - Q1_Port_1year['Shareprice_Appriciation'].max())/Q1_Port_1year['Shareprice_Appriciation'].max()
        # table_content1 = Maximum_Drawdown_1year
        Maximum_Drawdown_1year = Maximum_Drawdown_1year.reset_index()
        columns = list(Maximum_Drawdown_1year.columns)
        get_treatdf_dict = Maximum_Drawdown_1year.to_dict("records")
        value_list = []
        for i in get_treatdf_dict:
            value = i.values()
            value_list.append(value)
        
        return render(request,'output.html',{"columns":columns, 'value_list':value_list , "return_risks":return_risks_ })
    
    if drop_name == '3 year Maximum Drawdown':
        new_df = years.copy()
        new_df["Quartiles"] = pd.qcut(new_df['Share Appreciation for 3 years'].rank(method='first'), int(np.sqrt(new_df.shape[0])) , labels=["Q7", "Q6", "Q5","Q4","Q3","Q2","Q1"])
        Q1_Port_3year = new_df.loc[new_df['Quartiles'].isin(["Q1"])]
        Maximum_Drawdown_3year = (Q1_Port_3year['Share Appreciation for 3 years'].min() - Q1_Port_3year['Share Appreciation for 3 years'].max())/Q1_Port_3year['Share Appreciation for 3 years'].max()
        # table_content1 = Maximum_Drawdown_3year
        Maximum_Drawdown_3year = Maximum_Drawdown_3year.reset_index()
        columns = list(Maximum_Drawdown_3year.columns)
        get_treatdf_dict = Maximum_Drawdown_3year.to_dict("records")
        value_list = []
        for i in get_treatdf_dict:
            value = i.values()
            value_list.append(value)

        return render(request,'output.html',{"columns":columns, 'value_list':value_list , "return_risks":return_risks_ })
    
    if drop_name == '5 year Maximum Drawdown':
        new_df = years.copy()
        new_df["Quartiles"] = pd.qcut(new_df['Share Appreciation for 5 years'].rank(method='first'), int(np.sqrt(new_df.shape[0])) , labels=["Q7", "Q6", "Q5","Q4","Q3","Q2","Q1"])
        Q1_Port_5year = new_df.loc[new_df['Quartiles'].isin(["Q1"])]
        Maximum_Drawdown_5year = (Q1_Port_5year['Share Appreciation for 5 years'].min() - Q1_Port_5year['Share Appreciation for 5 years'].max())/Q1_Port_5year['Share Appreciation for 5 years'].max()
        # table_content1 = Maximum_Drawdown_5year
        Maximum_Drawdown_5year = Maximum_Drawdown_5year.reset_index()
        columns = list(Maximum_Drawdown_5year.columns)
        get_treatdf_dict = Maximum_Drawdown_5year.to_dict("records")
        value_list = []
        for i in get_treatdf_dict:
            value = i.values()
            value_list.append(value)

        return render(request,'output.html',{"columns":columns, 'value_list':value_list , "return_risks":return_risks_ })

    if drop_name == '1 year Maximum Drawdown Ratio':
        new_df = years.copy()
        new_df["Quartiles"] = pd.qcut(new_df['Shareprice_Appriciation'].rank(method='first'), int(np.sqrt(new_df.shape[0])) , labels=["Q7", "Q6", "Q5","Q4","Q3","Q2","Q1"])
        Q1_Port_1year = new_df.loc[new_df['Quartiles'].isin(["Q1"])]
        Maximum_Drawdown_1year = (Q1_Port_1year['Shareprice_Appriciation'].min() - Q1_Port_1year['Shareprice_Appriciation'].max())/Q1_Port_1year['Shareprice_Appriciation'].max()
        Portfilio_df_1year  = pd.DataFrame(Q1_Port_1year.groupby('Portfolio')["Shareprice_Appriciation"].median())
        Portfilio_df_1year["Return/MaximumDrawdow"] = Portfilio_df_1year/Maximum_Drawdown_1year

        # table_content1 = Portfilio_df_1year.to_html()
        Portfilio_df_1year = Portfilio_df_1year.reset_index()
        columns = list(Portfilio_df_1year.columns)
        get_treatdf_dict = Portfilio_df_1year.to_dict("records")
        value_list = []
        for i in get_treatdf_dict:
            value = i.values()
            value_list.append(value)
        return render(request,'output.html',{"columns":columns, 'value_list':value_list , "return_risks":return_risks_ })
    
    if drop_name == '3 year Maximum Drawdown Ratio':
        new_df = years.copy()
        new_df["Quartiles"] = pd.qcut(new_df['Share Appreciation for 3 years'].rank(method='first'), int(np.sqrt(new_df.shape[0])) , labels=["Q7", "Q6", "Q5","Q4","Q3","Q2","Q1"])
        Q1_Port_3year = new_df.loc[new_df['Quartiles'].isin(["Q1"])]

        Maximum_Drawdown_3year = (Q1_Port_3year['Share Appreciation for 3 years'].min() - Q1_Port_3year['Share Appreciation for 3 years'].max())/Q1_Port_3year['Share Appreciation for 3 years'].max()
        Portfilio_df_3year  = pd.DataFrame(Q1_Port_3year.groupby('Portfolio')["Share Appreciation for 3 years"].median())
        Portfilio_df_3year["Return/MaximumDrawdow"] = Portfilio_df_3year/Maximum_Drawdown_3year
        # table_content1 = Portfilio_df_3year.to_html()
        Portfilio_df_3year = Portfilio_df_3year.reset_index()
        columns = list(Portfilio_df_3year.columns)
        get_treatdf_dict = Portfilio_df_3year.to_dict("records")
        value_list = []
        for i in get_treatdf_dict:
            value = i.values()
            value_list.append(value)
        return render(request,'output.html',{"columns":columns, 'value_list':value_list , "return_risks":return_risks_ })

    if drop_name == '5 year Maximum Drawdown Ratio':
        new_df = years.copy()
        new_df["Quartiles"] = pd.qcut(new_df['Share Appreciation for 5 years'].rank(method='first'), int(np.sqrt(new_df.shape[0])) , labels=["Q7", "Q6", "Q5","Q4","Q3","Q2","Q1"])
        Q1_Port_5year = new_df.loc[new_df['Quartiles'].isin(["Q1"])]

        Maximum_Drawdown_5year = (Q1_Port_5year['Share Appreciation for 5 years'].min() - Q1_Port_5year['Share Appreciation for 5 years'].max())/Q1_Port_5year['Share Appreciation for 5 years'].max()
        Portfilio_df_5year  = pd.DataFrame(Q1_Port_5year.groupby('Portfolio')["Share Appreciation for 5 years"].median())

        Portfilio_df_5year["Return/MaximumDrawdow"] = Portfilio_df_5year/Maximum_Drawdown_5year

        # table_content1 = Portfilio_df_5year.to_html()
        Portfilio_df_5year = Portfilio_df_5year.reset_index()
        columns = list(Portfilio_df_5year.columns)
        get_treatdf_dict = Portfilio_df_5year.to_dict("records")
        value_list = []
        for i in get_treatdf_dict:
            value = i.values()
            value_list.append(value)
        return render(request,'output.html',{"columns":columns, 'value_list':value_list , "return_risks":return_risks_ })

    if drop_name == 'Monthly Standard Deviation':
        
        F['Std on Monthly'] = F.iloc[:,14:-1].std(axis = 1,skipna=True)
        MonthlyStd = F[['Company Name',"Std on Monthly"]]
        # table_content1 = MonthlyStd.to_html()
        MonthlyStd = MonthlyStd.reset_index()
        columns = list(MonthlyStd.columns)
        get_treatdf_dict = MonthlyStd.to_dict("records")
        value_list = []
        for i in get_treatdf_dict:
            value = i.values()
            value_list.append(value)
        return render(request,'output.html',{"columns":columns, 'value_list':value_list , "return_risks":return_risks_ })

    if drop_name == 'Min. Monthly Return':
        F["Minimum_Rows_Monthly"] = F.iloc[:,14:-2].min(axis=1,skipna=True)
        Min_Monthly_Return  = pd.DataFrame(F.groupby('Portfolio')["Minimum_Rows_Monthly"].min())
        # table_content1 = Min_Monthly_Return.to_html()
        Min_Monthly_Return = Min_Monthly_Return.reset_index()
        columns = list(Min_Monthly_Return.columns)
        get_treatdf_dict = Min_Monthly_Return.to_dict("records")
        value_list = []
        for i in get_treatdf_dict:
            value = i.values()
            value_list.append(value)
        return render(request,'output.html',{"columns":columns, 'value_list':value_list , "return_risks":return_risks_ })
    
    if drop_name == 'Avg. Monthly Return':
        F["Minimum_Rows_Monthly"] = F.iloc[:,14:-2].min(axis=1,skipna=True)
        Min_Monthly_Return_Avg  = pd.DataFrame(F.groupby('Portfolio')["Minimum_Rows_Monthly"].mean())
        # table_content1 = Min_Monthly_Return_Avg.to_html()
        Min_Monthly_Return_Avg = Min_Monthly_Return_Avg.reset_index()
        columns = list(Min_Monthly_Return_Avg.columns)
        get_treatdf_dict = Min_Monthly_Return_Avg.to_dict("records")
        value_list = []
        for i in get_treatdf_dict:
            value = i.values()
            value_list.append(value)

        return render(request,'output.html',{"columns":columns, 'value_list':value_list , "return_risks":return_risks_ })

    if drop_name == 'Percent of Month with Positive performance':
        F["Maximum_MonthlyReturn"] = F.iloc[:,14:-3].max(axis=1,skipna=True)
        Min_Monthly_Return_max  = pd.DataFrame(F.groupby('Portfolio')["Maximum_MonthlyReturn"].max())
        # table_content1 = Min_Monthly_Return_max.to_html()
        Min_Monthly_Return_max = Min_Monthly_Return_max.reset_index()
        columns = list(Min_Monthly_Return_max.columns)
        get_treatdf_dict = Min_Monthly_Return_max.to_dict("records")
        value_list = []
        for i in get_treatdf_dict:
            value = i.values()
            value_list.append(value)

        return render(request,'output.html',{"columns":columns, 'value_list':value_list , "return_risks":return_risks_ })

    if drop_name == 'Daily Standard Deviation':
        
        Daily['Std on Daily'] = Daily.iloc[:,24:].std(axis = 1,skipna=True)
        Daily_standard_deviation = pd.DataFrame(Daily[['Company Name','Portfolio','Std on Daily']])
        # table_content1 = Daily_standard_deviation.to_html()
        Daily_standard_deviation = Daily_standard_deviation.reset_index()
        columns = list(Daily_standard_deviation.columns)
        get_treatdf_dict = Daily_standard_deviation.to_dict("records")
        value_list = []
        for i in get_treatdf_dict:
            value = i.values()
            value_list.append(value)

        return render(request,'output.html',{"columns":columns, 'value_list':value_list , "return_risks":return_risks_ })

    if drop_name == 'Average Daily Return':
        Daily["Average Daily Return"] = Daily.iloc[:,24:].mean(axis=1,skipna=True)
        Average_DailyReturns_ByPortfolio  = pd.DataFrame(Daily.groupby('Portfolio')["Average Daily Return"].median())
        # table_content1 = Average_DailyReturns_ByPortfolio.to_html()
        Average_DailyReturns_ByPortfolio = Average_DailyReturns_ByPortfolio.reset_index()
        columns = list(Average_DailyReturns_ByPortfolio.columns)
        get_treatdf_dict = Average_DailyReturns_ByPortfolio.to_dict("records")
        value_list = []
        for i in get_treatdf_dict:
            value = i.values()
            value_list.append(value)

        return render(request,'output.html',{"columns":columns, 'value_list':value_list , "return_risks":return_risks_ })
    
    if drop_name == 'Minimum Daily Return':
        Daily["Minimum_Daily"] = Daily.iloc[:,24:].min(axis=1,skipna=True)
        Minimum_DailyReturns_ByPortfolio  = pd.DataFrame(Daily.groupby('Portfolio')["Minimum_Daily"].median())
        # table_content1 = Minimum_DailyReturns_ByPortfolio.to_html()
        Minimum_DailyReturns_ByPortfolio = Minimum_DailyReturns_ByPortfolio.reset_index()
        columns = list(Minimum_DailyReturns_ByPortfolio.columns)
        get_treatdf_dict = Minimum_DailyReturns_ByPortfolio.to_dict("records")
        value_list = []
        for i in get_treatdf_dict:
            value = i.values()
            value_list.append(value)

        return render(request,'output.html',{"columns":columns, 'value_list':value_list , "return_risks":return_risks_ })

    if drop_name == 'Return / Risk Ratio':
        d = daily.copy()
        d['Return_Risk_Ratio'] = d.iloc[:,2:].mean(axis=1) / d.iloc[:,2:].std(axis=1,skipna=True)
        Return_Riskratio_Daily = pd.DataFrame(d.groupby('Portfolio')["Return_Risk_Ratio"].median())

        # table_content1 = Return_Riskratio_Daily.to_html()
        Return_Riskratio_Daily = Return_Riskratio_Daily.reset_index()
        columns = list(Return_Riskratio_Daily.columns)
        get_treatdf_dict = Return_Riskratio_Daily.to_dict("records")
        value_list = []
        for i in get_treatdf_dict:
            value = i.values()
            value_list.append(value)
        return render(request,'output.html',{"columns":columns, 'value_list':value_list  , "return_risks":return_risks_ })

    if drop_name == 'Monthly Return risk ratio':
        m = monthly.copy()
        m['Return_Risk_Ratio'] = m.iloc[:,4:].mean(axis=1) / m.iloc[:,4:].std(axis=1,skipna=True)
        Return_Riskratio = pd.DataFrame(m.groupby('Portfolio')["Return_Risk_Ratio"].median())
        # table_content1 = Return_Riskratio.to_html()
        Return_Riskratio = Return_Riskratio.reset_index()
        columns = list(Return_Riskratio.columns)
        get_treatdf_dict = Return_Riskratio.to_dict("records")
        value_list = []
        for i in get_treatdf_dict:
            value = i.values()
            value_list.append(value)
        return render(request,'output.html',{"columns":columns, 'value_list':value_list  , "return_risks":return_risks_ })

        



    







 








    








    

    
















#*************************Backup - 16-07-2020 Sandeep *********************************

# def fileupload(request):
#     """
#     Fun desc: File upload choose Excel and CSV format files and insert into MONGODB..

#     uploading file from local machine to local folder documents/ ...
    
#     insert_data_into_mongo(doc_path)  is updated into MongoDB. >> excelinsert.py 

#     After upload succefully show success message...... 
#     """
#     if request.method == 'POST':
#         f = request.FILES.getlist('file')
#         for i in f:
#             global filename
#             filename = str(i) 
#             print('This is I Object:',i)
            
#             with open('Quant_App/documents/' +  str(i), 'wb+') as destination:
#                  for chunk in i.chunks():
#                      destination.write(chunk)            
#             doc_path = 'Quant_App/documents/' + str(i)
#             #message = DatalayersClass.insert_data_into_mongo(doc_path)
#         message = ''
#         final_df = BusinessLogicClass.import_files_intoDF()
#         #print('Checking the type of Final DF:',final_df)
#         #print('Type of FinalDF1',type(final_df))
#         empty_dir = r"C:/Users/Nagaraj/Desktop/Backupcode/Vantage_Quant - Copy/Vantage_Quant/Quant_App/documents/"
#         #os.path.remove(empty_dir)
#         shutil.rmtree(empty_dir)
#         os.mkdir('C:/Users/Nagaraj/Desktop/Backupcode/Vantage_Quant - Copy/Vantage_Quant/Quant_App/documents')

#         if type(final_df) == str :
#             print('This is the message',final_df)
#             return render(request,'upload.html',{'message': message,'df_message':final_df})
#         else:
#             table_content1 = final_df.to_html()
#             context = {'table_content1': table_content1}
#             #return render(request,'upload.html',{'message': message,'table_content1':table_content1})
#             return render(request,'upload.html',{'message': message,'table_content1':table_content1})
        

#     return render(request,'upload.html')


# ***************************************8 16-07-2020 -************************************






















    # if request.method == 'POST':
    #     f = request.FILES
    #     print('Multiple:',f)
    #     for i in f.items():
    #         global filename
    #         filename = str(i[1]) 
    #         print('This is I Object:',i[1])
            
    #         with open('Quant_App/documents/' +  str(i[1]), 'wb+') as destination:
    #              for chunk in i[1].chunks():
    #                  destination.write(chunk)            
    #     doc_path = 'Quant_App/documents/' + filename
    #     message = DatalayersClass.insert_data_into_mongo(doc_path)  
    #     return render(request,'upload.html',{'message': message})
        
    # return render(request,'upload.html')













"""
Below code is for backup I copies ... 10/07/2020- Sandeep

"""
########################################################################3
# @csrf_exempt
# def show_data(request):
#     print('hhaaaaa')
#     """
#     Fun description: to display selected file information in tabular form...

#     This view function show excel collections into dropdown >> get_collections()...
#     retrieving the selected excel file into page to display... >> read_datatable(file_name)
#      read_datatable  returns dataframe...
#      dataframe converted into html and display in htmlp page...
#      file_name : to show the message that what file we selected... 
#     """
#     if request.method == 'POST':
#         file_name = request.POST["selected_file"]
#         finaldf =  DataaccesslayerClass.get_table(file_name)
#         coll_list = DataaccesslayerClass.collections()  # after pick the filename reload the page with file collections
#         print('This is MY yes')
#         table_content = finaldf.to_html()
#         context = {'table_content': table_content}
#         return render(request,'home.html',{'context':table_content,'coll_list':coll_list,'file':file_name})
#     coll_list= DataaccesslayerClass.collections()
#     #coll_list = datalayersClass.get_collections()
  
#     return render(request,'home.html',{'coll_list':coll_list})

#===========================================
# def cal_means(request):
#     dataframelist = cal_mean()
#     final_df_median = cal_median()

#     return render(request,'mean.html',{'dataframe':dataframelist,'median_df':final_df_median})







######################################################################
# """ def fileupload(request):
#     """
#     Fun desc: File upload choose Excel and CSV format files and insert into MONGODB..

#     uploading file from local machine to local folder documents/ ...
    
#     insert_data_into_mongo(doc_path)  is updated into MongoDB. >> excelinsert.py 

#     After upload succefully show success message...... 
     
#     """
#     if request.method == 'POST':
#         f = request.FILES
#         for i in f.items():
#             global filename
#             filename = str(i[1]) 
#             print(i[1])
#             with open('myapp/documents/' +  str(i[1]), 'wb+') as destination:
#                  for chunk in i[1].chunks():
#                      destination.write(chunk)            
#         doc_path = 'myapp/documents/' + filename
#         insert_data_into_mongo(doc_path)   ## excelinsert.py 
#         return render(request,'upload.html',{'message': 'Uploaded Successfully'})
        
#     return render(request,'upload.html')

# @csrf_exempt
# def show_data(request):
#     """
#     Fun description: to display selected file information in tabular form...

#     This view function show excel collections into dropdown >> get_collections()...
#     retrieving the selected excel file into page to display... >> read_datatable(file_name)
#      read_datatable  returns dataframe...
#      dataframe converted into html and display in htmlp page...
#      file_name : to show the message that what file we selected... 
#     """
#     if request.method == 'POST':
#         file_name = request.POST["selected_file"]
#         finaldf =  read_datatable(file_name)
#         coll_list = get_collections()  # after pick the filename reload the page with file collections
#         table_content = finaldf.to_html()
#         context = {'table_content': table_content}
#         return render(request,'home.html',{'context':table_content,'coll_list':coll_list,'file':file_name})

#     coll_list = get_collections()
#     return render(request,'home.html',{'coll_list':coll_list})


# def cal_means(request):
#     dataframelist = cal_mean()
#     final_df_median = cal_median()

#     return render(request,'mean.html',{'dataframe':dataframelist,'median_df':final_df_median}) """