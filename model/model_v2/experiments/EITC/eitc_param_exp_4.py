"""
execfile('eitc_param_exp_4.py')

This file generates a list of EITC parameters
Each element of the list (0-9) corresponds to a dictionary of parameters
of the EITC (1995-2003), where:

-t=0 <=> 1995

-r1,r2: phase-in and phase-out rates
-b1,b2: minimum income for max credit/beginning income for phase-out
-state_eitc=fraction of federal eitc

"""
from __future__ import division #omit for python 3.x
import numpy as np
import pandas as pd
import itertools
import sys, os
import pickle
import copy
from scipy import stats


#save dictionaries here:
eitc_list=[]

#The parameters
for year in range(1995,2014):

	#1 children
	r1_1=0
	r2_1=0
	b1_1=6160
	b2_1=11290
	state_eitc1=0

	#2+ children
	r1_2=0
	r2_2=0
	b1_2=8640
	b2_2=11290
	state_eitc2=0

	#3 children
	r1_3=0
	r2_3=0
	b1_3=8640
	b2_3=11290
	state_eitc3=0

		
	#Save dictionary in this list
	dic_aux={'r1_1': r1_1, 'r2_1': r2_1, 'b1_1':b1_1, 'b2_1': b2_1, 
	'r1_2':r1_2, 'r2_2': r2_2, 'b1_2': b1_2, 'b2_2': b2_2,
	'r1_3':r1_3, 'r2_3': r2_3, 'b1_3': b1_3, 'b2_3': b2_3,
	   'state_eitc1': state_eitc1, 'state_eitc2': state_eitc2, 'state_eitc3': state_eitc3}

	#Save dictionary in this list
	eitc_list.append(dic_aux)

#Saving the list
pickle.dump(eitc_list,open('/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/eitc_dic_4.p','wb'))
		



