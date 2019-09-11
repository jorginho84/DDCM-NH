"""
execfile('afdc_param.py')
exec(open("C:\\Users\\jrodriguezo\\Dropbox\\Chicago\\Research\\Human capital and the household\\codes\\DDCM-NH\\model\\model_v2 - onechild\\simulate_sample\\afdc_param.py").read())

This file generates a list of AFDC parameters
The paramaters are used in the t=0 AFDC computation.
The parameters vay by family size

Source: Welfare Rules Database
"""

#from __future__ import division #omit for python 3.x
import numpy as np
import pandas as pd
import itertools
import sys, os
import pickle
from scipy import stats

#save dictionaries here:
afdc_list=[]

#these vary by family size
cutoff = np.array([311,550,647,772,886,958,1037,1099,1151,1179,1204,1229])*1.85*12 

benefit_std = np.array([249,440,518,618,709,766,830,879,921,943,963,983])*12

afdc_dic = {'cutoff':cutoff,'benefit_std':benefit_std}

afdc_list.append(afdc_dic)

#Saving the list
pickle.dump(afdc_list,open('C:\\Users\\jrodriguezo\\Dropbox\\Chicago\\Research\\Human capital and the household\\codes\\DDCM-NH\\model\\model_v2\\simulate_sample\\afdc_list.p','wb'))

