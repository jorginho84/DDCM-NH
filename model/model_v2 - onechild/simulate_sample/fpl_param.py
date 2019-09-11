"""
exec(open("/home/jrodriguez/NH_HC/codes/model_v2/simulate_sample/fpl_param.py").read())

This file generates a federal poverty lines
Source: US Department of Health & Human Services

format:

[X,Y], where

X: FPL for one person
Y: for each additional person

"""
import numpy as np
import pandas as pd
import itertools
import sys, os
import pickle
from scipy import stats

#save dictionaries here:
fpl_list=[]

for year in range(1995,2014):
	if year == 1995:
		fpl = 7470
		mult = 2560

	if year == 1996:
		fpl = 7740
		mult = 2620

	if year == 1997:
		fpl = 7890
		mult = 2720

	if year == 1998:
		fpl = 8050
		mult = 2800
	
	if year == 1999:
		fpl = 8240
		mult = 2820
	
	if year == 2000:
		fpl = 8350
		mult = 2900

	if year == 2001:
		fpl = 8590
		mult = 3020

	if year == 2002:
		fpl = 8860
		mult = 3080

	if year == 2003:
		fpl = 8980
		mult = 3140

	if year == 2004:
		fpl = 9310
		mult = 3180

	if year == 2005:
		fpl = 9570
		mult = 3260

	if year == 2006:
		fpl = 9800
		mult = 3400

	if year == 2007:
		fpl = 10210
		mult = 3480

	if year == 2008:
		fpl = 10400
		mult = 3600

	if year == 2009:
		fpl = 10830
		mult = 3740

	if year == 2010:
		fpl = 10830
		mult = 3740

	if year == 2011:
		fpl = 10890
		mult = 3820

	if year == 2012:
		fpl = 11170
		mult = 3960

	if year == 2013:
		fpl = 11490
		mult = 4020


	fpl_dic = {'fpl': fpl, 'multip': mult}

	fpl_list.append(fpl_dic)

#Saving the list
pickle.dump(fpl_list,open('/home/jrodriguez/NH_HC/codes/model_v2/simulate_sample/fpl_list.p','wb'))
