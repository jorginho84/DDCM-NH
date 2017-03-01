"""
execfile('nhpol.py')

This file computes ATE theta and inputs of different New Hope policies

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
sys.path.append("/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/experiments/NH")
from ate_gen import ATE


np.random.seed(1)

betas_nelder=np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/betas_modelv5_v1.npy')


#Utility function
eta=.1
alphap=-0.1
alphaf=-0.15
alpha_cc = -0.35


#wage process
wagep_betas=np.array([0.005,betas_nelder[4],betas_nelder[5],
	1.2,0.94]).reshape((5,1))


#Production function [young[cc0,cc1],old]
gamma1=[betas_nelder[8],betas_nelder[10]]
gamma2=[betas_nelder[9],betas_nelder[11]]
tfp=betas_nelder[12]
sigmatheta=0

#Measurement system: three measures for t=2, one for t=5
kappas=[[betas_nelder[13],betas_nelder[14],betas_nelder[15],betas_nelder[16]],
[betas_nelder[17],betas_nelder[18],betas_nelder[19],betas_nelder[20]]]
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

#The EITC parameters
eitc_list = pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/eitc_list.p', 'rb' ) )

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

#Defines the instance with parameters
param0=util.Parameters(alphap, alphaf, eta, alpha_cc,gamma1, gamma2, tfp, sigmatheta,
	wagep_betas, marriagep_betas, kidsp_betas, eitc_list,afdc_list,snap_list,
	cpi,q,scalew,shapew,lambdas,kappas,pafdc,psnap)



###Auxiliary estimates###
moments_vector=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/moments_vector.csv').values

#This is the var cov matrix of aux estimates
var_cov=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/var_cov.csv').values

#The vector of aux standard errors
#Using diagonal of Var-Cov matrix of simulated moments
se_vector  = np.sqrt(np.diagonal(var_cov))

#Creating a grid for the emax computation
dict_grid=gridemax.grid()

#For montercarlo integration
D=50

#Number of samples to produce
M=1000

#How many hours is part- and full-time work
hours_p=15
hours_f=40

#This is the list of models to compute [wr,cs,ws]. This order is fixed
models_list = [[0,0,1], [0,1,1], [1,0,1],
[0,1,0],[1,1,0],[1,1,1]]


###Computing counterfactuals
dics = []
for j in range(len(models_list)):
	output_ins=estimate.Estimate(param0,x_w,x_m,x_k,x_wmk,passign,agech0,theta0,nkids0,
		married0,D,dict_grid,M,N,moments_vector,var_cov,hours_p,hours_f,
		models_list[j][0],models_list[j][1],models_list[j][2])

	hours = np.zeros(N) #arbitrary to initialize model instance
	childcare  = np.zeros(N)
	model = util.Utility(param0,N,x_w,x_m,x_k,passign,theta0,nkids0,married0,hours,childcare,
		agech0,hours_p,hours_f,models_list[j][0],models_list[j][1],models_list[j][2])

	np.random.seed(1)
	emax_instance = output_ins.emax(param0,model)
	choices = output_ins.samples(param0,emax_instance,model)
	ate_ins = ATE(choices,agech0,passign,hours_p,hours_f,model)
	dics.append(ate_ins.sim_ate())



####The table###
#the list of policies

pol_list = ['Wage sub.', 'Child care s. +  wage sub.', 'Work req. + wage sub.',
'Child care s.', 'Work req. + child care s.', 'Work req. + child care s. +  wage sub.']

with open('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/NH/table_nhpol.tex','w') as f:
	f.write(r'\begin{tabular}{llccccccccccc}'+'\n')
	f.write(r'\hline'+'\n')
	f.write(r'Policies &       & Part-time &       & Full-time &       & Child care &       & Consumption &       & $\log \theta$ &       & Welfare \bigstrut\\'+'\n')
	f.write(r'\cline{1-1}\cline{3-3}\cline{5-5}\cline{7-7}\cline{9-9}\cline{11-11}\cline{13-13}      &       &       &       &       &       &       &       &       &       &       &       &  \bigstrut[t]\\'+'\n')
	
	for j in range(6): #there are five policies
		f.write(pol_list[j] +r'&       & '+ '{:04.3f}'.format(dics[j]['Part-time']) +
			r' & & ' + '{:04.3f}'.format(dics[j]['Full-time'])  + 
			r' & &  '  '{:04.3f}'.format(dics[j]['CC']) + 
			r' & &   '+ '{:04.3f}'.format(dics[j]['Consumption']) +
			r' & & '+ '{:04.3f}'.format(dics[j]['Theta'])  )

		#welfare effects relative to the baseline policy
		if j==5:
			f.write(r'&&' + '-' + r' \\'+'\n')
		else:
			f.write(r'&&' + '{:04.3f}'.format(dics[j]['Welfare']-dics[5]['Welfare']) + r' \\'+'\n')

	f.write(r'\hline'+'\n')
	f.write(r'\end{tabular}' + '\n')
	f.close()



