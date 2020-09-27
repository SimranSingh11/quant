## Libraries 

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
import matplotlib.pyplot as plt
# %matplotlib inline
import time
import seaborn as sns


from itertools import combinations 
def rSubset(arr, r): 
    """
    Get the combinations from parameters list.. 
    
    """
  
    return list(combinations(arr, r)) 

######################################
from itertools import product
def all_repeat(str1, rno):
    """
    This is function we used to permutations product..
    columns a b c
    """
    
    chars = list(str1)
    results = []
    for c in product(chars, repeat = rno):
        
        results.append(c)
    return results

##############################################
def get_columnnames(ls1,ls2,ls3,ls4):
    """
    ls1 - 
    
    """
    
    list3 = []
    for i in ls3:
        list3.append(str(i))
    
    list1 = ls1
    list2 = ls2
    list4 = ls4
    sum_list = []

    for (item2,item1,item3,item4) in zip(list2, list1,list3,list4):
        sum_list.append(item2+item1+item3+item4)

    return sum_list
#######################################

def sort_quartiles(df):
    mydfs = df 
    mydfs  =  mydfs.copy()
    Strt_index = mydfs.columns.get_loc('Avg_Rank')  + 1
    Last_index = mydfs.columns.get_loc('Weightages_Avarage_Rank')
    strin = ""
    for s in list(mydfs.columns[Strt_index:Last_index]):
        strin =  strin + s
    Name = str(strin + "_SharePrice_Appr%")
    mydfs[Name] = mydfs["Shareprice_Appriciation"]
    Sort_df = pd.DataFrame(mydfs.groupby('Quartiles')[Name].median())
    
    return Sort_df


# def automate_Raking(Data):
#     """
#     This functions which Data file with [Company Name, Para1,para2 ....., ParaN, Shareprice_Appriciation]
#     Get the combinations columsn list...
#     Created DataFrames with this combinations.. 
#     ## Checking with Multicolinearity with parameters.. Threshold 0.75
#     ## Ranking on Parameters   ## Column name==  Parametername + _Rank
#     ## Avg_value of Ranking parameters ##Column name =  Avg_Weightage_Rank
#     ## ranking on Avg_Weightage_Rank ###Column = Weightages_Avarage_Rank
    
#     ## sort_quartiles by Return DataFrame with Quartiles.. 
    
#     Returns : 
#     my_dfs ==> After multicolinearity all the combinations DataFrames...
#     Sorted_dfs ==> Group by Quartiles DataFrames...
#     reductions_Dfs ==> Reductions Dfs...
    
#     """
    
def automate_Raking(Data):
    """
    This functions which Data file with [Company Name, Para1,para2 ....., ParaN, Shareprice_Appriciation]
    Get the combinations columsn list...
    Created DataFrames with this combinations.. 
    ## Checking with Multicolinearity with parameters.. Threshold 0.75
    ## Ranking on Parameters   ## Column name==  Parametername + _Rank
    ## Avg_value of Ranking parameters ##Column name =  Avg_Weightage_Rank
    ## ranking on Avg_Weightage_Rank ###Column = Weightages_Avarage_Rank
    
    ## sort_quartiles by Return DataFrame with Quartiles.. 
    
    Returns : 
    my_dfs ==> After multicolinearity all the combinations DataFrames...
    Sorted_dfs ==> Group by Quartiles DataFrames...
    reductions_Dfs ==> Reductions Dfs...
    
    """
    
    Df = Data
    Df = Df.fillna(0)
#     Df = Df[Df.iloc[:,-1].replace({0:-1})]
    Df = Df.copy()
    df_list = list(Df.columns)

    fina_ls = []
    

    for i in range(1,len(df_list[1:])):
        s = rSubset(df_list[2:-1],i)
        combi_list = []
        for j in s:
            combi_list.append(list(j)) 
        fina_ls.append(combi_list)
        
    print("Length of Cobmbinations",len(fina_ls))

    ## Created dataframes with all combinations...

    multi_corr = []
    # fina_ls[0]
    for j in fina_ls[:]:
        for i in j[:]:

            i.insert(0,'Company Name')
            i.insert(1,'Portfolio')
            i.extend(['Shareprice_Appriciation'])
            df1 = pd.DataFrame(Df[i])
            multi_corr.append(df1) 
    
    #############
    
    ### Getting Non Multi collinearity commbinations
    All_Dataframes = []        
    reductions_Dfs = []
    for i in range(len(multi_corr[:])):
        n = pd.DataFrame(multi_corr[i].iloc[:,:-1].corr()[:] >= 0.75)
        leng = len(n)
        s= n.values
        j = np.eye(leng) == 1
        comparison = s == j
        equal_arrays = comparison.all()
        if equal_arrays== True:
            All_Dataframes.append(multi_corr[i])
        else:
            reductions_Dfs.append(multi_corr[i])
    print('After Multi_Collinearity',len(All_Dataframes))
    print('Reductions ',len(reductions_Dfs))

#     ## Giving the ranks to features... depends on correlations with Return%...

    for frame in All_Dataframes:
        copied_frame = frame.copy()
        correlation = frame.corr()
        copied_Cor = correlation.copy()
        for j in range(0,len(copied_Cor.columns)-1):  ## Its -2 
            columns = list(copied_Cor.columns)
            #print('Value',columns[j])
            columns_name = columns[j]
            k = len(copied_Cor.columns)-1
            #print('K Value',k)
            i = j+2      ## J+ 4 means after from 5th index
#             if copied_Cor.iloc[j,k] >= 0.05: ## Dont use
            frame[str(columns_name) + '_Rank'] = copied_frame.iloc[:,i].rank(method = 'first',ascending=0)
    my_dfs = All_Dataframes.copy()            
    for f in my_dfs:
        
        L = f.columns.get_loc('Shareprice_Appriciation') + 1
        col = f.iloc[: ,L:]
        f['Avg_Rank'] = col.mean(axis=1).round()
    
    Avg_ranks = my_dfs.copy()
    
    my_dfs = []
    for new in Avg_ranks:
        i = new.columns.get_loc("Shareprice_Appriciation")+1
        j = new.columns.get_loc("Avg_Rank")
        l = len(new.columns[i:j])
        z = np.ones(l).tolist()
        for k in range(0,l):
            arrs = z.copy()
            for m in range(1,6):
                arrs[k] = m

                df1 = new.copy()
                p = df1.columns.get_loc("Shareprice_Appriciation")+1
                q = df1.columns.get_loc("Avg_Rank")
                cols = list(df1.columns[p:q])
                weightage_list = ['_Weight_','_Weight_','_Weight_','_Weight_','_Weight_','_Weight_','_Weight_','_Weight_','_Weight_','_Weight_','_Weight_']
                Separater_list = ['|','|','|','|','|','|','|','|','|','|','|','|','|','|','|']
                w_c = get_columnnames(weightage_list,cols,arrs,Separater_list)
    #             print(p,q)
    #             print(cols)
    #             print(arrs)
                df1[w_c] = df1.iloc[:,p:q] * arrs
    #             print(df1)
                df = pd.DataFrame(df1)
        #         print(df)
                my_dfs.append(df)
                #print('***')
        #print('#####')
    
    for frames in my_dfs:
#     frame = frames.copy()
        i = frames.columns.get_loc("Avg_Rank")+1
        frames['Weightages_Avarage_Rank'] = frames.iloc[:,i:].mean(axis=1).round()
        
        ##
        j = frames.columns.get_loc("Weightages_Avarage_Rank")
        frames['Weighatages_Rank'] = frames.iloc[:,j].rank(method = 'first',ascending=1)
       ##
   
    lables_ = []
    for i in range(1,int(np.sqrt(Df.shape[0]).round())+1):
        lab = 'Q' + str(i)
        lables_.append(lab)

    
    Sorted_dfs = []
    for frames in my_dfs:
        #frames["Quartiles"] = pd.qcut(frames['Weightages_Avarage_Rank'].rank(method='first'), int(np.sqrt(frames.shape[0]).round()) , labels=["Q1", "Q2", "Q3","Q4","Q5","Q6","Q7"])
        frames["Quartiles"] = pd.qcut(frames['Weighatages_Rank'].rank(method='first'), int(np.sqrt(frames.shape[0]).round()) , labels=lables_)
        Testing_Q = frames.copy()
        Sort_df = sort_quartiles(Testing_Q)
        sortted_q  = list(Sort_df.iloc[:,0])
        # if sortted_q[0] > sortted_q[1] > sortted_q[2] > sortted_q[3]:
        #     print('Yes Falling down...')
        #     Falling_down.append(list(Sort_df.columns))
        # else:
        Sorted_dfs.append(Sort_df)

    return my_dfs,Sorted_dfs,reductions_Dfs

def check_consequtive_fall_dfs(Sorted_dfs):
    """
    From GroupedBy Quartiles if 4 consecutive Combinations Quartiles are falling down... then drop that.
    Return ==> all_dfs which after falldowns DataFrames..
    
    """
    
    i = 0 
    j = i + 5
    fin_list = []
    fin_removed = []
    for frame in range(len(Sorted_dfs[:])):
        removed = []
        check = []
        sub_dataframes = []
        for i in range(i,j):
            k = i+1
            if k < len(Sorted_dfs[:]):

                #print('Start',i,k)
                s = Sorted_dfs[i].iloc[0][0] > Sorted_dfs[k].iloc[0][0] and Sorted_dfs[i].iloc[1][0] > Sorted_dfs[k].iloc[1][0] and Sorted_dfs[i].iloc[2][0] > Sorted_dfs[k].iloc[2][0] and Sorted_dfs[i].iloc[3][0] > Sorted_dfs[k].iloc[3][0]
                check.append(s)
                sub_dataframes.append(Sorted_dfs[i])
                sub_dataframes.append(Sorted_dfs[k])
                if len(check) == 4:
                    s = check[0] == check[1] ==check[2] ==check[3] == True
                    check.clear()
                    #print('clear')
                    #print('Is false',s)
                    if s == True:
                        removed.append(sub_dataframes)
                        sub_dataframes.clear()
                        i = j 
                        j = i + 5
                        #print('Comesinto list',i,j)
    #             elif:
    #                 print('Next index',i)
    #                 print('Index',i,k)
    #                 pass
                #print('Sandeep',i,k,j)       
                if k == j:
                    i = j
                    j = i + 5

                    #print('End Range',i,j)
                    #print('**')
    #     checked.append(check)           
        fin_removed.append(removed) 
        fin_list.append(sub_dataframes)
        
    final_list = []
    for i in fin_list:
        for j in i:
            final_list.append(j)
    all_dfs = []
    all_col = []
    for i in final_list:
        if i.columns[0] not in all_col:
            all_col.append(i.columns[0])
            all_dfs.append(i)

#     return fin_list,fin_removed
    return all_dfs

def get_summary(all_dfs):
    """
    Finnalize all the combinations with weightages group by Q1 and in Soreted way.. 
    ## Returns ==> Get Smmary in Soreted by Q1
    
    """
    myQ = all_dfs[:]
    mq = myQ.copy()
    Summary = pd.DataFrame(columns=['Quartiles'])
    for i in range(len(mq)-1):
        #  Summary_copied = Summary.copy()
         Summary = pd.merge_ordered(Summary, mq[i], on='Quartiles')
    
    Summary = Summary.set_index('Quartiles')
    Summary = Summary.sort_values(by ='Q1', axis=1,ascending=False)
    
    return Summary

def transpose_rowindex(Summary):
    """
    Summarized Combinations Dataframes Transposed and Add row_indexing columns
    ## Created anothe column with Row_Indexing Series 
    Returns ==> DataFrame with Row_indexing
    
    """
    TrialRun = Summary.copy()
    Tranposed_D = TrialRun.transpose()
    Tranposed_D.columns = list(Tranposed_D.columns)
    Tranposed_D = Tranposed_D.reset_index()
    Tranposed_D = Tranposed_D.rename(columns = {'index': 'Quartiles',}, inplace = False)
    s= pd.Series(list(range(len(Tranposed_D))))
    Tranposed_D['Row_Indexing'] = s
    Tranposed_D = Tranposed_D[['Row_Indexing','Quartiles', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', ]]
    return Tranposed_D

def get_bestparametes_Combinations_unique(Trans):
    """
    From the All Transposed combnations get only one Combinations from Set of all the combinations with High Shareprice_Appriciation
    Returns ==> DataFrame with Unique Combinations with High Shareprice_Appriciation
    
    """
    
    Data  = Trans.copy()
    Data['Newcolu'] = Data['Quartiles'].str.replace('\d+.', '')
    Data = Data[['Row_Indexing','Newcolu','Quartiles', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7']]
    Data = Data.iloc[:,1:]
    Df3 = Data.set_index('Newcolu')
    Df3 = Df3.reset_index()
    Sorted = Df3.sort_values(by='Q1',axis=0,ascending = False)
    S = Sorted.groupby(['Newcolu'])
    New = pd.DataFrame(S)
    News = pd.DataFrame(S.first())
    Df9 = News.sort_values(by=['Q1'],ascending=False)
    Df9 = Df9.reset_index()
    Df9 = Df9.iloc[:,1:]
    
    return Df9 

def get_lineplots(Df9):
    """
    ## Line Plotting on top from Unique Combinations with High Shareprice_Appriciation
    ## 
    """
    
    D9 = Df9.copy()
    plots = []
    for i in range(0,20):
        fig, ax = plt.subplots()
        fig= plt.figure(figsize=(12,8))
        s = ax.plot(D9.iloc[i,1:],label= str(D9.iloc[i,0]))
        leg = ax.legend(loc=9, bbox_to_anchor=(2,1));
        plots.append(s)

def treatment_quartiles_df(df, wieghtage):
    Quartiles = df.copy()
    Quartiles = Quartiles.fillna(0)
    # Quartiles = Quartiles[new_columns_list]
    for i in range(2,len(Quartiles.columns[:-1])):
        col = str(Quartiles.columns[i])
        Quartiles[col+'_Rank'] = Quartiles.iloc[:,i].rank(method = 'first',ascending=0)
    L = Quartiles.columns.get_loc('Shareprice_Appriciation') + 1
    wieghtage = [int(i) for i in wieghtage]
    wieghtage = wieghtage[2:-1]
    Quartiles.iloc[:,L:] = Quartiles.iloc[:,L:] * wieghtage
    col = Quartiles.iloc[: ,L:]
    Quartiles['Average_Rank'] = col.mean(axis=1).round()
    j = Quartiles.columns.get_loc("Average_Rank")
    Quartiles['Weighatages_Rank'] = Quartiles.iloc[:,j].rank(method = 'first',ascending=1)
    Quartiles["Quartiles"] = pd.qcut(Quartiles['Weighatages_Rank'].rank(method='first'), int(np.sqrt(Quartiles.shape[0]).round()) , labels=["Q1", "Q2", "Q3","Q4","Q5","Q6","Q7"])

    return Quartiles
