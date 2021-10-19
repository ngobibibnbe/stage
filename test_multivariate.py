# Import modules.
import numpy as np
from pysad.utils import Data
import scipy.io
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
import time
import os 
from hyperopt import fmin, tpe,hp, STATUS_OK, Trials
from numba import jit, cuda
import code
import time
import os
import numba  
from numba import njit, types
from numba.extending import overload, register_jitable
from numba.core.errors import TypingError
import math
import sys
from datetime import datetime
from sklearn.preprocessing import OneHotEncoder

sys.path.append('MILOF/lib')
from MiLOF import MILOF

from stream_discord import class_our
from test_LAMP import class_LAMP
from test_hs_tree import class_hstree
from test_iforestASD import class_iforestASD
from score_nab import evaluating_change_point
from test_ARIMAFD import class_ARIMAFD
from test_KitNet import class_KitNet

from test_Milof import class_MILOF

def dataset_test(key,idx,dataset,scoring_metric="merlin"):
    
        df = pd.read_csv("dataset/"+dataset)
        flag =False
        try: 
            base2 = pd.read_excel("f1score_"+scoring_metric+"_abnormal_multivariate_point_results.xlsx") 
            ligne = base2[key+"best_param"][idx]
        except :
            flag=True
            print("erreur de fichier ")
            ligne="erreur"
            
        #try :
        if True: # ligne =="params" or flag:
            oe_style = OneHotEncoder()
            for col in df.columns:
                if df.dtypes[col]==np.object:
                    oe_results = oe_style.fit_transform(df[[col]])
                    df=df.join(pd.DataFrame(oe_results.toarray(), columns=oe_style.categories_))
            
            # reading the dataset
            X =[df.iloc[i].values for i in range(0,len(df))] 
            right=np.array(str(base["Position discord"][idx]).split(';'))
            nbr_anomalies=len(str(base["Position discord"][idx]).split(';'))

            if scoring_metric=="merlin":
                gap =int(len(X)/100)
            if key =="HS-tree":
                real_scores, scores_label, identified,score,best_param, time_taken_1= class_hstree.test(dataset,X,right,nbr_anomalies,gap,scoring_metric=scoring_metric)  # Le concept drift est encore à faire manuellement et;le threshold est fixé après en fonction du nombre d'anomalies dans le dataset pour ne pas pénaliser l'algorithme
            if key =="MILOF":
                real_scores, scores_label, identified,score,best_param, time_taken_1= class_MILOF.test(dataset,X,right,nbr_anomalies,gap)  # Le concept drift est encore à faire manuellement et;le threshold est fixé après en fonction du nombre d'anomalies dans le dataset pour ne pas pénaliser l'algorithme
            if key=="iforestASD":
                real_scores, scores_label, identified,score,best_param, time_taken_1= class_iforestASD.test(X,right,nbr_anomalies,gap)  # Le concept drift est encore à faire manuellement et;le threshold est fixé après en fonction du nombre d'anomalies dans le dataset pour ne pas pénaliser l'algorithme
            if key=="ARIMAFD":
                real_scores, scores_label, identified,score,best_param, time_taken_1= class_ARIMAFD.test(df,X,right,nbr_anomalies,gap,scoring_metric="merlin")  # Le concept drift est encore à faire manuellement et;le threshold est fixé après en fonction du nombre d'anomalies dans le dataset pour ne pas pénaliser l'algorithme
            if key=="KitNet":
                real_scores, scores_label, identified,score,best_param, time_taken_1= class_KitNet.test(X,right,nbr_anomalies,gap,scoring_metric="merlin")  # Le concept drift est encore à faire manuellement et;le threshold est fixé après en fonction du nombre d'anomalies dans le dataset pour ne pas pénaliser l'algorithme
            if key=="LAMP":
                """base2 = pd.read_excel("point_methods_result_milof.xlsx")
                if base2[key+"best_param"][idx]=='params':
                    return idx, 0,0, 0, 0"""
                real_scores, scores_label, identified,score,best_param, time_taken_1= class_LAMP.test(dataset,df[column].values,right,nbr_anomalies,gap)  # Le concept drift est encore à faire manuellement et;le threshold est fixé après en fonction du nombre d'anomalies dans le dataset pour ne pas pénaliser l'algorithme
            if key=="our":
                real_scores, scores_label, identified,score,best_param, time_taken_1= class_our.test(dataset,df[column].values,right,nbr_anomalies,gap)  # Le concept drift est encore à faire manuellement et;le threshold est fixé après en fonction du nombre d'anomalies dans le dataset pour ne pas pénaliser l'algorithme
            df["anomaly_score"]=real_scores
            df["label"]=scores_label#[0 if i<threshold else 1 for i in scores ]
            
            
            directory = os.path.dirname(('streaming_results/'+key+'/'+dataset))
            if not os.path.exists(directory):
                os.makedirs(directory)
            data_file_name=dataset.split('/')[-1]
            data_file_name =key+'_'+data_file_name
            dataset =directory+'/'+data_file_name
            df.to_csv(dataset, index=False)

            file1=scoring_metric+"_abnormal_multivariate_point_results.xlsx"
            file2= scoring_metric+"_"+key+"_abnormal_multivarie_point.xlsx"
            print(key,file1,file2,idx, best_param,time_taken_1, score, identified)

            return (key,file1,file2,idx, best_param,time_taken_1, score, identified) # key,file1,file2,idx, best_params,time_taken, merlin_score, all_identified

import multiprocessing
mutex =multiprocessing.Lock()

base_file ='multivariate_abnormal_point.csv'
base = pd.read_csv(base_file)
import multiprocessing as mp
from multiprocessing import Manager
pool =mp.Pool(mp.cpu_count())

thresholds=[]


        
# Test pipeline   
# ****************************************************************************************************************************
def test (meth) :                                                         
    merlin_score=np.zeros(len(base))
    time_taken = np.zeros(len(base))
    best_params= ["params" for i in time_taken]
    all_identified= ["no" for i in time_taken]
    methods= { meth:0}
    scoring_metric=["merlin"] # you can also use NAB if you want to use the NAB score 
    for  key, method in methods.items() :
        
        with Manager() as mgr:
            def listener(m):
                print("*****************************************")
                print(m)
                print("*****************************************")
                key,file1,file2,idx, best_param,time_take, merlin_scor, identified=m
                all_identified[idx] =identified
                merlin_score[idx]=merlin_scor
                time_taken[idx]=time_take
                best_params[idx]=best_param
                print(best_params,"***")
                file1="f1score_"+scoring+"_abnormal_multivariate_point_results.xlsx"
                file2= "f1score_"+scoring+"_"+key+"_abnormal_multivarie_point.xlsx"
                all_insertion(key,file1,file2,idx, best_params,time_taken, merlin_score, all_identified)

            merlin_score=mgr.list(list(np.zeros(len(base)) ))
            time_taken =mgr.list(list(np.zeros(len(base)) ))
            best_params= mgr.list( ["params" for i in time_taken])
            all_identified= mgr.list( ["no" for i in time_taken])

            for scoring  in scoring_metric:
                
                for idx,dataset in enumerate(base["Dataset"]) :
                    """m=dataset_test(key,idx,dataset,scoring)
                    listener(m)"""

                    pool.apply_async(dataset_test, args=(key,idx,dataset,scoring,), callback=listener )
                pool.close()
                pool.join()
                file1=scoring+"_abnormal_multivariate_point_results.xlsx"
                file2= scoring+"_"+key+"_abnormal_multivarie_point.xlsx"


def all_insertion(key,file1,file2,idx, best_params,time_taken, merlin_score, all_identified):
    print(file1,key,idx,best_params,time_taken,merlin_score, all_identified)
    insertion(file1,key,idx,best_params,time_taken,merlin_score, all_identified)
    insertion(file2,key,idx,best_params,time_taken,merlin_score, all_identified)

def insertion(file,key,idx,best_params,time_taken,merlin_score, all_identified):
            
            try:
                if key in file: 
                    base2 = pd.read_excel("streaming_results/"+file)
                else:
                    base2 = pd.read_excel(file) 
                
                base2[key+"_identified"] [idx]= all_identified[idx]
                base2[key+"_Overlap_merlin"] [idx]= merlin_score[idx]
                base2[key+"best_param"] [idx]=str(best_params [idx])
                base2[key+"time_taken"] [idx]= time_taken[idx]
            except :
                if key in file: 
                    base2 = pd.read_csv(base_file)
                else:
                    base2 = pd.read_excel("merlin_abnormal_multivariate_point_results.xlsx") 
                base2[key+"_identified"] = all_identified
                base2[key+"_Overlap_merlin"] = merlin_score
                base2[key+"best_param"] =best_params 
                base2[key+"time_taken"]= time_taken
                print("***************************************except***************")
                if key in file:
                    print(best_params)
                    for key2,value in best_params[idx].items():
                        base2["best_param"+key2] =best_params[idx][key2]

            if key in file:
                for key2,value in best_params[idx].items():
                    base2["best_param"+key2][idx] =best_params[idx][key2]
                base2.to_excel("streaming_results/"+file, index=False)
            else:
                base2.to_excel(file, index=False)


            
import sys
print("***",sys.argv)

test(sys.argv[1])




