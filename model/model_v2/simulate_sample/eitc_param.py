"""
execfile('eitc_param.py')

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
from scipy import stats


#save dictionaries here:
eitc_list=[]

#The parameters
for year in range(1995,2003):

	##Year 1995##
	if year==1995:
		#1 children
		r1_1=.34
		r2_1=.1598
		b1_1=6160
		b2_1=11290
		state_eitc1=.04

		#2+ children
		r1_2=.36
		r2_2=.2022
		b1_2=8640
		b2_2=11290
		state_eitc2=.16

		#3 children
		state_eitc3=.50

		
	##Year 1996##
	if year==1996:
		#1 children
		r1_1=.34
		r2_1=.1598
		b1_1=6330
		b2_1=11610
		state_eitc1=.04

		#2+ children
		r1_2=.40
		r2_2=.2106
		b1_2=8890
		b2_2=11610
		state_eitc2=.14

		#3 children
		state_eitc3=.43
		
		
	##Year 1997##
	if year==1997:
		#1 children
		r1_1=.34
		r2_1=.1598
		b1_1=6500
		b2_1=11930
		state_eitc1=.04

		#2+ children
		r1_2=.40
		r2_2=.2106
		b1_2=9140
		b2_2=11930
		state_eitc2=.14

		#3 children
		state_eitc3=.43

	##Year 1998##
	if year==1998:
		#1 children
		r1_1=.34
		r2_1=.1598
		b1_1=6680
		b2_1=12260
		state_eitc1=.04

		#2+ children
		r1_2=.40
		r2_2=.2106
		b1_2=9390
		b2_2=12260
		state_eitc2=.14

		#3 children
		state_eitc3=.43


	##Year 1999##
	if year==1999:
		#1 children
		r1_1=.34
		r2_1=.1598
		b1_1=6800
		b2_1=12460
		state_eitc1=.04

		#2+ children
		r1_2=.40
		r2_2=.2106
		b1_2=9540
		b2_2=12460
		state_eitc2=.14

		#3 children
		state_eitc3=.43


	##Year 2000##
	if year==2000:
		#1 children
		r1_1=.34
		r2_1=.1598
		b1_1=6920
		b2_1=12690
		state_eitc1=.04

		#2+ children
		r1_2=.40
		r2_2=.2106
		b1_2=9720
		b2_2=12690
		state_eitc2=.14

		#3 children
		state_eitc3=.43

	##Year 2001##
	if year==2001:
		#1 children
		r1_1=.34
		r2_1=.1598
		b1_1=7140
		b2_1=13090
		state_eitc1=.04

		#2+ children
		r1_2=.40
		r2_2=.2106
		b1_2=10020
		b2_2=13090
		state_eitc2=.14

		#3 children
		state_eitc3=.43

	##Year 2002##
	if year==2002:
		#1 children
		r1_1=.34
		r2_1=.1598
		b1_1=.7370
		b2_1=.13520
		state_eitc1=.04

		#2+ children
		r1_2=.40
		r2_2=.2106
		b1_2=10350
		b2_2=13520
		state_eitc2=.14

		#3 children
		state_eitc3=.43


	##Year 2003##
	if year==2003:
		#1 children
		r1_1=.34
		r2_1=.1598
		b1_1=7490
		b2_1=13730
		state_eitc1=.04

		#2+ children
		r1_2=.40
		r2_2=.2106
		b1_2=10510
		b2_2=13730
		state_eitc2=.14

		#3 children
		state_eitc3=.43

	#Dictionary
	dic_aux={'r1_1': r1_1, 'r2_1': r2_1, 'b1_1':b1_1, 'b2_1': b2_1, 
	'r1_2':r1_2, 'r2_2': r2_2, 'b1_2': b1_2, 'b2_2': b2_2,
	   'state_eitc1': state_eitc1, 'state_eitc2': state_eitc2, 'state_eitc3': state_eitc3}

	#Save dictionary in this list
	eitc_list.append(dic_aux)

#Saving the list
pickle.dump(eitc_list,open('/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/eitc_list.p','wb'))
		



