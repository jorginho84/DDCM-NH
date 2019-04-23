"""
execfile('eitc_figures.py')

This file plots the EITC schedules of two experiments:

Experiment 1: EITC vs no EITC
Experiment 2: EITC vs 1994 EITC
"""

from __future__ import division #omit for python 3.x
import numpy as np
import pandas as pd
import itertools
import sys, os
import pickle
import copy
from scipy import stats
import matplotlib
matplotlib.use('Agg') # Force matplotlib to not use any Xwindows backend.
import matplotlib.pyplot as plt



eitc_list_1 = pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/eitc_dic_1.p', 'rb' ) )
eitc_list_2 = pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/eitc_dic_2.p', 'rb' ) )
eitc_list = [eitc_list_1,eitc_list_2]

nperiods = 9

#2 children, income 0-34800

pwage = np.array(range(0,34801))
eitc_fed = np.zeros((pwage.shape[0],nperiods,2)) 
eitc_state = np.zeros((pwage.shape[0],nperiods,2)) 
eitc = np.zeros((pwage.shape[0],nperiods,2)) 


for k in range(2): #the experiment loop

	for periodt in range(nperiods):

		#The EITC parameters (2 children)
		dic_eitc=[eitc_list[k]['No EITC'][periodt],eitc_list[k]['Full EITC'][periodt]]
		r1_2=[dic_eitc[0]['r1_2'],dic_eitc[1]['r1_2']]
		r2_2=[dic_eitc[0]['r2_2'],dic_eitc[1]['r2_2']]
		b1_2=[dic_eitc[0]['b1_2'],dic_eitc[1]['b1_2']]
		b2_2=[dic_eitc[0]['b2_2'],dic_eitc[1]['b2_2']]
		state_eitc2=[dic_eitc[0]['state_eitc2'],dic_eitc[1]['state_eitc2']]

		for j in range(2): #the treatment loop
			eitc_fed[(pwage<b1_2[j]),periodt,j]=r1_2[j]*pwage[(pwage<b1_2[j])]
			eitc_fed[(pwage>=b1_2[j]) & (pwage<b2_2[j]),periodt,j]=r1_2[j]*b1_2[j]
			eitc_fed[(pwage>=b2_2[j]),periodt,j]=np.maximum(r1_2[j]*b1_2[j]-r2_2[j]*(pwage[(pwage>=b2_2[j])]-b2_2[j]),np.zeros(pwage[(pwage>=b2_2[j])].shape[0]))
			if j==0:
				eitc_state[:,periodt,j]=np.minimum(state_eitc2[j]*eitc_fed[:,periodt,j],499)
			else:
				eitc_state[:,periodt,j]=state_eitc2[j]*eitc_fed[:,periodt,j]
			eitc[:,periodt,j] = eitc_fed[:,periodt,j] + eitc_state[:,periodt,j] 


		#The graphs
		fig,ax = plt.subplots()
		plot1=ax.plot(pwage/100,eitc[:,periodt,0]/100,'k--',label='Control',alpha=0.9)
		plot2=ax.plot(pwage/100,eitc[:,periodt,1]/100,'k-',label='Treatment',alpha=0.9)
		plt.setp(plot1,linewidth=3)
		plt.setp(plot2,linewidth=3)
		ax.tick_params(labelsize='large')
		ax.legend()
		ax.set_ylabel(r'Subsidy (hundreds of dollars)',fontsize=15)
		ax.set_xlabel(r'Earnings (hundreds of dollars)',fontsize=15)
		ax.spines['right'].set_visible(False)
		ax.spines['top'].set_visible(False)
		ax.yaxis.set_ticks_position('left')
		ax.set_autoscaley_on(False)
		ax.set_ylim([0,55])
		ax.xaxis.set_ticks_position('bottom')
		plt.show()
		fig.savefig('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/EITC/eitc_exp'
			+str(k)+ '_t'+ str(periodt) +'.pdf', format='pdf')
		plt.close()




