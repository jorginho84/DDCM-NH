"""
execfile('eitc_exp.py')

This file computes EITC experiments
"""

from __future__ import division #omit for python 3.x
import numpy as np
import pandas as pd
import pickle
import itertools
import sys, os
from scipy import stats
#from scipy.optimize import minimize
from scipy.optimize import fmin_bfgs
from joblib import Parallel, delayed
from scipy import interpolate
import matplotlib.pyplot as plt
#sys.path.append("C:\\Users\\Jorge\\Dropbox\\Chicago\\Research\\Human capital and the household\]codes\\model")
sys.path.append("/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample")
import utility as util
import gridemax
import time
import int_linear
import emax as emax
import simdata as simdata
sys.path.append("/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/estimation")
import estimate as estimate
sys.path.append("/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/experiments")
from ate_gen import ATE
sys.path.append("/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/experiments/NH")
from bset import Budget

np.random.seed(1)

betas_nelder=np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/betas_modelv7_v2_e3.npy')


#Utility function
eta=betas_nelder[0]
alphap=betas_nelder[1]
alphaf=betas_nelder[2]
alpha_cc=betas_nelder[3]


#wage process
wagep_betas=np.array([betas_nelder[4],betas_nelder[5],betas_nelder[6],
	betas_nelder[7],betas_nelder[8],betas_nelder[9]]).reshape((6,1))


#Production function [young[cc0,cc1],old]
gamma1=[betas_nelder[10],betas_nelder[12]]
gamma2=[betas_nelder[11],betas_nelder[13]]
tfp=betas_nelder[14]
sigmatheta=0

#Measurement system: three measures for t=2, one for t=5
kappas=[[betas_nelder[15],betas_nelder[16],betas_nelder[17],betas_nelder[18]],
[betas_nelder[19],betas_nelder[20],betas_nelder[21],betas_nelder[22]]]
#First measure is normalized. starting arbitrary values
#All factor loadings are normalized
lambdas=[1,1]


#Weibull distribution of cc prices
scalew=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/scale.csv').values
shapew=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/shape.csv').values
q=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/q_prob.csv').values


#Probability of afdc takeup
pafdc=.60

#Probability of snap takeup
psnap=.70

#Data
#X_aux=pd.read_csv('C:\\Users\\Jorge\\Dropbox\\Chicago\\Research\\Human capital and the household\\results\\Model\\Xs.csv')
X_aux=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/sample_model_v2.csv')
x_df=X_aux

#Sample size 
N=X_aux.shape[0]

#Data for wage process
#see wage_process.do to see the order of the variables.
x_w=x_df[ ['age_ra', 'd_HS2', 'constant' ] ].values


#Data for marriage process
#Parameters: marriage. Last one is the constant
x_m=x_df[ ['age_ra', 'constant']   ].values
marriagep_betas=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/marriage_process/betas_m_v2.csv').values

#Data for fertility process (only at X0)
#Parameters: kids. last one is the constant
x_k=x_df[ ['age_ra', 'age_ra2', 'constant']   ].values
kidsp_betas=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/kids_process/betas_kids_v2.csv').values


#Minimum set of x's (for interpolation)
x_wmk=x_df[  ['age_ra', 'age_ra2', 'd_HS2', 'age_t0','age_t02','constant'] ].values

#Data for treatment status
passign=x_df[ ['d_RA']   ].values

#The EITC parameters: experiments 1 and 2
#Exp 1: Full EITC vs No EITC
#Exp 2: Full EITC vs fixed EITC
#Exp 3: Full EITC vs Full EITC
eitc_list_1 = pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/eitc_dic_1.p', 'rb' ) )
eitc_list_2 = pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/eitc_dic_2.p', 'rb' ) )
eitc_list_3 = pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/eitc_dic_3.p', 'rb' ) )

#The AFDC parameters
afdc_list = pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/afdc_list.p', 'rb' ) )

#The SNAP parameters
snap_list = pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/snap_list.p', 'rb' ) )

#CPI index
cpi =  pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/cpi.p', 'rb' ) )

#Here: the estimates from the auxiliary model
###
###

#Assuming random start
theta0=np.exp(np.random.randn(N))


#number of kids at baseline
nkids0=x_df[ ['nkids_baseline']   ].values

#marital status at baseline
married0=x_df[ ['d_marital_2']   ].values

#age of child at baseline
agech0=x_df[['age_t0']].values

###Auxiliary estimates### 

moments_vector=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/moments_vector.csv').values


#This is the var cov matrix of aux estimates
var_cov=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/var_cov.csv').values

#The W matrix in Wald metric
#Using diagonal of Var-Cov matrix of simulated moments
w_matrix  = np.zeros((var_cov.shape[0],var_cov.shape[0]))
for i in range(var_cov.shape[0]):
	w_matrix[i,i] = var_cov[i,i]


#Creating a grid for the emax computation
dict_grid=gridemax.grid()

#For montercarlo integration
D=50

#For II procedure
M=1000

#How many hours is part- and full-time work
hours_p=15
hours_f=40

#Indicate if model includes a work requirement (wr), 
#and child care subsidy (cs) and a wage subsidy (ws)

#In these experiments, cs is the only one that matters
wr=0
cs=0
ws=0

#number of periods to consider for each input
nperiods_cc = 3
nperiods_ct = 9
nperiods_emp = 9
nperiods_theta = 9

#Young until periodt=period_y
period_y = 2

#To start model instance
hours = np.zeros(N)
childcare  = np.zeros(N)

"""
EXPERIMENT 1: Full EITC vs No EITC (eitc_list_1)
EXPERIMENT 2: 1996 EITC vs 1994 EITC (eitc_list_2)
EXPERIMENT 3: CC subsidy + EITC vs EITC
EXPERIMENT 4: CC subsidy + EITC vs 1994 EITC
EXPERIMENT 5: CC subsidy + EITC vs No EITC

"""
eitc_list = [eitc_list_1,eitc_list_2,eitc_list_3]
cc_sub_list = [0,1]

experiments=[ [eitc_list[0],cc_sub_list[0]],
 [eitc_list[1],cc_sub_list[0]], [eitc_list[2],cc_sub_list[1]],
 [eitc_list[1],cc_sub_list[1]], [eitc_list[0],cc_sub_list[1]]]

dics = []

for j in range(5): #the experiment loop

	#Defines the instance with parameters
	param0=util.Parameters(alphap, alphaf, eta, alpha_cc,gamma1, gamma2, tfp, sigmatheta,
		wagep_betas, marriagep_betas, kidsp_betas, experiments[j][0],afdc_list,snap_list,
		cpi,q,scalew,shapew,lambdas,kappas,pafdc,psnap)

	output_ins=estimate.Estimate(param0,x_w,x_m,x_k,x_wmk,passign,agech0,theta0,nkids0,
		married0,D,dict_grid,M,N,moments_vector,var_cov,hours_p,hours_f,
		wr,experiments[j][1],ws)

	#The model (utility instance)
	
	model = Budget(param0,N,x_w,x_m,x_k,passign,theta0,nkids0,married0,
		hours,childcare,agech0,hours_p,hours_f,wr,experiments[j][1],ws)

	#Obtaining emax instances, samples, and betas for M samples
	np.random.seed(1)
	emax_instance = output_ins.emax(param0,model)
	choices = output_ins.samples(param0,emax_instance,model)

	#Obtaining ATEs and saving results
	ate_ins = ATE(M,choices,agech0,passign,hours_p,hours_f,
		nperiods_cc,nperiods_ct,nperiods_emp,nperiods_theta,period_y)
	dics.append(ate_ins.sim_ate())

#HERE I AM: see if nperiods_cc=3 makes the ate_CC>0.

######Making the Table#######
outcome_list = ['Consumption (US\$)', 'Part-time', 'Full-time', 'Child care',
r'$\ln \theta$ ($\sigma$s)', 'Utility']

output_list = ['Consumption', 'Part-time', 'Full-time', 'CC', 'Theta', 'Welfare']

with open('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/EITC/table_eitc_exp.tex','w') as f:
	f.write(r'\begin{tabular}{lcccccccccc}'+'\n')
	f.write(r'\hline'+'\n')
	f.write(r'ATE   &       & (1)   & & (2)   & & (3)   & & (4)   && (5) \bigstrut[b]\\'+'\n')
	f.write(r'\cline{1-1}\cline{3-11}'+'\n')
	for j in range(len(outcome_list)):
		
		if j==0: #consumption w/ no decimals
			
			f.write(outcome_list[j])
			for k in range(len(experiments)): #the policy loop
				f.write(r'  && '+ '{:02.0f}'.format(dics[k][output_list[j]]))
			f.write(r' \bigstrut[t]\\'+'\n')
		else:
			f.write(outcome_list[j])
			for k in range(len(experiments)): #the policy loop
				f.write(r'  && '+ '{:04.3f}'.format(dics[k][output_list[j]]))
			f.write(r' \bigstrut[t]\\'+'\n')

	f.write(r'\hline'+'\n')
	f.write(r'\textit{Treatment group} &&&&&&&&&&  \bigstrut[t]\\'+'\n')
	f.write(r'EITC (1995-2003) &       & $\checkmark$ &       & $\checkmark$ &       & $\checkmark$ &       & $\checkmark$ &       & $\checkmark$ \\'+'\n')
	f.write(r'Child care subsidy &       &       &       &       &       & $\checkmark$ &       & $\checkmark$ &       & $\checkmark$ \bigstrut[b]\\'+'\n')
	f.write(r'\hline'+'\n')
	f.write(r'\textit{Control group} &       &       &       &       &       &       &       &       &       &  \bigstrut[t]\\'+'\n')
	f.write(r'EITC (1995-2003) &       &       &       &       &       & $\checkmark$ &       &       &       &  \\'+'\n')
	f.write(r'EITC (1994) &       &       &       & $\checkmark$ &       &       &       & $\checkmark$ &       &  \\'+'\n')
	f.write(r'No EITC &       & $\checkmark$ &       &       &       &       &       &       &       & $\checkmark$ \bigstrut[b]\\'+'\n')
	f.write(r'\hline'+'\n')
	f.write(r'\end{tabular}'+'\n')