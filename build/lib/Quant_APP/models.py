import pymongo
import pandas as pd
#import pymongo
import base64
import bson
from bson.binary import Binary#
import xlrd 
import justpy as jp
myclient = pymongo.MongoClient("mongodb://localhost:27017/")

from django.db import models

mydb = myclient["Excelfiles"]

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
        coll_list = mydb.list_collection_names()
        
        return coll_list

    def insert_data_into_mongo(excel_path):
        """
        method: insert_data_into_mongo(Excel_path):
            -- This function is used to insert data file which Excel into MongoDB as Collections...
            -- Its creates Every individual Excel sheet as Collection with Excel Sheet Name...

        Arg: excel_path while are upoloading from USER Interface...

        """
        loc = (excel_path)
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

### 13/07/2020 --SANDEEP -- ###

class Company():

    class Company():
        """
        Model Class... Its create a

        SA - I tries to run the code models.Model ... Its on HOLD...
        """
        Company_ID = models.CharField()

        pass

        #   Company_ID         =    model.Dtatatype(Length) - PK
        #   Company_name  =   model.datatype(max_length(50))
        #   Company_loc       =    model.datatype()
        #   Company_contactno  = model.contactno()
        #  CompanyEmail_id   = model.datatype()
          
        #   def __str__(self):
        #          self.Company_name
    class  Users():

        pass

