"""
exec(open("/home/jrodriguez/NH_HC/codes/model_v2/experiments/EITC/eitc_param_exp_1.py").read())


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

	##Year 1995##
	if year==1995:
		#1 children
		r1_1=.34
		r2_1=.1598
		b1_1=6160
		b2_1=[11290,11290]
		state_eitc1=.04

		#2+ children
		r1_2=.36
		r2_2=.2022
		b1_2=8640
		b2_2=[11290,11290]
		state_eitc2=.16

		#3 children
		r1_3=.36
		r2_3=.2022
		b1_3=8640
		b2_3=[11290,11290]
		state_eitc3=.50

		
	##Year 1996##
	if year==1996:
		#1 children
		r1_1=.34
		r2_1=.1598
		b1_1=6330
		b2_1=[11610,11610]
		state_eitc1=.04

		#2+ children
		r1_2=.40
		r2_2=.2106
		b1_2=8890
		b2_2=[11610,11610]
		state_eitc2=.14

		#3 children
		r1_3=.40
		r2_3=.2106
		b1_3=8890
		b2_3=[11610,11610]
		state_eitc3=.43
		
		
	##Year 1997##
	if year==1997:
		#1 children
		r1_1=.34
		r2_1=.1598
		b1_1=6500
		b2_1=[11930,11930]
		state_eitc1=.04

		#2+ children
		r1_2=.40
		r2_2=.2106
		b1_2=9140
		b2_2=[11930,11930]
		state_eitc2=.14

		#3 children
		r1_3=.40
		r2_3=.2106
		b1_3=9140
		b2_3=[11930,11930]
		state_eitc3=.43

	##Year 1998##
	if year==1998:
		#1 children
		r1_1=.34
		r2_1=.1598
		b1_1=6680
		b2_1=[12260,12260]
		state_eitc1=.04

		#2+ children
		r1_2=.40
		r2_2=.2106
		b1_2=9390
		b2_2=[12260,12260]
		state_eitc2=.14

		#3 children
		r1_3=.40
		r2_3=.2106
		b1_3=9390
		b2_3=[12260,12260]
		state_eitc3=.43


	##Year 1999##
	if year==1999:
		#1 children
		r1_1=.34
		r2_1=.1598
		b1_1=6800
		b2_1=[12460,12460]
		state_eitc1=.04

		#2+ children
		r1_2=.40
		r2_2=.2106
		b1_2=9540
		b2_2=[12460,12460]
		state_eitc2=.14

		#3 children
		r1_3=.40
		r2_3=.2106
		b1_3=9540
		b2_3=[12460,12460]
		state_eitc3=.43


	##Year 2000##
	if year==2000:
		#1 children
		r1_1=.34
		r2_1=.1598
		b1_1=6920
		b2_1=[12690,12690]
		state_eitc1=.04

		#2+ children
		r1_2=.40
		r2_2=.2106
		b1_2=9720
		b2_2=[12690,12690]
		state_eitc2=.14

		#3 children
		r1_3=.40
		r2_3=.2106
		b1_3=9720
		b2_3=[12690,12690]
		state_eitc3=.43

	##Year 2001##
	if year==2001:
		#1 children
		r1_1=.34
		r2_1=.1598
		b1_1=7140
		b2_1=[13090,13090]
		state_eitc1=.04

		#2+ children
		r1_2=.40
		r2_2=.2106
		b1_2=10020
		b2_2=[13090,13090]
		state_eitc2=.14

		#3 children
		r1_3=.40
		r2_3=.2106
		b1_3=10020
		b2_3=[13090,13090]
		state_eitc3=.43

	##Year 2002##
	#Starting this year, beginning of phase-out increases for married couple
	if year==2002:
		#1 children
		r1_1=.34
		r2_1=.1598
		b1_1=7370
		b2_1=[13520, 13520+1000]
		state_eitc1=.04

		#2+ children
		r1_2=.40
		r2_2=.2106
		b1_2=10350
		b2_2=[13520,13520+1000]
		state_eitc2=.14

		#3 children
		r1_3=.40
		r2_3=.2106
		b1_3=10350
		b2_3=[13520,13520+1000]
		state_eitc3=.43


	##Year 2003##
	if year==2003:
		#1 children
		r1_1=.34
		r2_1=.1598
		b1_1=7490
		b2_1=[13730,13730+1000]
		state_eitc1=.04

		#2+ children
		r1_2=.40
		r2_2=.2106
		b1_2=10510
		b2_2=[13730,13730+1000]
		state_eitc2=.14

		#3 children
		r1_3=.40
		r2_3=.2106
		b1_3=10510
		b2_3=[13730,13730+1000]
		state_eitc3=.43

	##Year 2004##
	if year==2004:
		#1 children
		r1_1=.34
		r2_1=.1598
		b1_1=7660
		b2_1=[14040,14040+1000]
		state_eitc1=.04

		#2+ children
		r1_2=.40
		r2_2=.2106
		b1_2=10750
		b2_2=[14040,14040+1000]
		state_eitc2=.14

		#3 children
		r1_3=.40
		r2_3=.2106
		b1_3=10750
		b2_3=[14040,14040+1000]
		state_eitc3=.43

	##Year 2005##
	if year==2005:
		#1 children
		r1_1=.34
		r2_1=.1598
		b1_1=7830
		b2_1=[14370,14370+2000]
		state_eitc1=.04

		#2+ children
		r1_2=.40
		r2_2=.2106
		b1_2=11000
		b2_2=[14370,14370+2000]
		state_eitc2=.14

		#3 children
		r1_3=.40
		r2_3=.2106
		b1_3=11000
		b2_3=[14370,14370+2000]
		state_eitc3=.43

	##Year 2006##
	if year==2006:
		#1 children
		r1_1=.34
		r2_1=.1598
		b1_1=8080
		b2_1=[14810,14810+2000]
		state_eitc1=.04

		#2+ children
		r1_2=.40
		r2_2=.2106
		b1_2=11340
		b2_2=[14810,14810+2000]
		state_eitc2=.14

		#3 children
		r1_3=.40
		r2_3=.2106
		b1_3=11340
		b2_3=[14810,14810+2000]
		state_eitc3=.43

	##Year 2007##
	if year==2007:
		#1 children
		r1_1=.34
		r2_1=.1598
		b1_1=8390
		b2_1=[15390,15390+1000]
		state_eitc1=.04

		#2+ children
		r1_2=.40
		r2_2=.2106
		b1_2=11790
		b2_2=[15390,15390+1000]
		state_eitc2=.14

		#3 children
		r1_3=.40
		r2_3=.2106
		b1_3=11790
		b2_3=[15390,15390+1000]
		state_eitc3=.43

	##Year 2008##
	if year==2008:
		#1 children
		r1_1=.34
		r2_1=.1598
		b1_1=8580
		b2_1=[15740,15740+3000]
		state_eitc1=.04

		#2+ children
		r1_2=.40
		r2_2=.2106
		b1_2=12060
		b2_2=[15740,15740+3000]
		state_eitc2=.14

		#3 children
		r1_3=.40
		r2_3=.2106
		b1_3=12060
		b2_3=[15740,15740+3000]
		state_eitc3=.43

	##Year 2009##
	if year==2009:
		#1 children
		r1_1=.34
		r2_1=.1598
		b1_1=8950
		b2_1=[16420,16420+5000]
		state_eitc1=.04

		#2+ children
		r1_2=.40
		r2_2=.2106
		b1_2=12570
		b2_2=[16420,16420+5000]
		state_eitc2=.14

		#3 children
		r1_3=.45
		r2_3=.2106
		b1_3=12570
		b2_3=[16420,16420+5000]
		state_eitc3=.43

	##Year 2010##
	if year==2010:
		#1 children
		r1_1=.34
		r2_1=.1598
		b1_1=8970
		b2_1=[16450,16450+5010]
		state_eitc1=.04

		#2+ children
		r1_2=.40
		r2_2=.2106
		b1_2=12590
		b2_2=[16450,16450+5010]
		state_eitc2=.14

		#3 children
		r1_3=.45
		r2_3=.2106
		b1_3=12590
		b2_3=[16450,16450+5010]
		state_eitc3=.43

	##Year 2011##
	if year==2011:
		#1 children
		r1_1=.34
		r2_1=.1598
		b1_1=9100
		b2_1=[16690,16690+5080]
		state_eitc1=.04

		#2+ children
		r1_2=.40
		r2_2=.2106
		b1_2=12780
		b2_2=[16690,16690+5080]
		state_eitc2=.14

		#3 children
		r1_3=.45
		r2_3=.2106
		b1_3=12780
		b2_3=[16690,16690+5080]
		state_eitc3=.43

	##Year 2012##
	if year==2012:
		#1 children
		r1_1=.34
		r2_1=.1598
		b1_1=9320
		b2_1=[17090,17090+5210]
		state_eitc1=.04

		#2+ children
		r1_2=.40
		r2_2=.2106
		b1_2=13090
		b2_2=[17090,17090+5210]
		state_eitc2=.14

		#3 children
		r1_3=.45
		r2_3=.2106
		b1_3=13090
		b2_3=[17090,17090+5210]
		state_eitc3=.43

	##Year 2013##
	if year==2013:
		#1 children
		r1_1=.34
		r2_1=.1598
		b1_1=9560
		b2_1=[17530,17530+5340]
		state_eitc1=.04

		#2+ children
		r1_2=.40
		r2_2=.2106
		b1_2=13430
		b2_2=[17530,17530+5340]
		state_eitc2=.14

		#3 children
		r1_3=.45
		r2_3=.2106
		b1_3=13430
		b2_3=[17530,17530+5340]
		state_eitc3=.43

	#Save dictionary in this list
	dic_aux={'r1_1': r1_1, 'r2_1': r2_1, 'b1_1':b1_1, 'b2_1': b2_1, 
	'r1_2':r1_2, 'r2_2': r2_2, 'b1_2': b1_2, 'b2_2': b2_2,
	'r1_3':r1_3, 'r2_3': r2_3, 'b1_3': b1_3, 'b2_3': b2_3,
	   'state_eitc1': state_eitc1, 'state_eitc2': state_eitc2, 'state_eitc3': state_eitc3}

	#Save dictionary in this list
	eitc_list.append(dic_aux)

	

#Saving the list
pickle.dump(eitc_list,open('/home/jrodriguez/NH_HC/codes/model_v2/simulate_sample/eitc_dic_1.p','wb'))
		



