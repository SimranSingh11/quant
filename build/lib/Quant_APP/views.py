from django.shortcuts import render
import os
import pandas as pd
from django.views.decorators.csrf import csrf_exempt
from Quant_App.models import DatalayersClass,BusinessLogicClass
import justpy as jp    ## For Justpy Grid... https://justpy.io/  
#from DatalayersClass import get_collections


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
        f = request.FILES
        for i in f.items():
            global filename
            filename = str(i[1]) 
            print(i[1])
            with open('myapp/documents/' +  str(i[1]), 'wb+') as destination:
                 for chunk in i[1].chunks():
                     destination.write(chunk)            
        doc_path = 'myapp/documents/' + filename
        message = DatalayersClass.insert_data_into_mongo(doc_path)  
        return render(request,'upload.html',{'message': message})
        
    return render(request,'upload.html')





































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