"""
execfile('master_dcheck.py')

This file computes Emax 1 for a grid of D values

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

np.random.seed(1)

betas_nelder=np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/betas_modelv7_v2_e5.npy')

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
param0=util.Parameters(alphap, alphaf, eta, alpha_cc, gamma1, gamma2,tfp,sigmatheta,
	wagep_betas, marriagep_betas, kidsp_betas, eitc_list,afdc_list,snap_list,
	cpi,q,scalew,shapew,lambdas,kappas,pafdc,psnap)

#For montercarlo integration
D=[5, 10, 15, 20, 25, 30, 35, 40, 50, 60, 70, 80, 90, 100]

#How many hours is part- and full-time work
hours_p=15
hours_f=40

hours = np.zeros(N)
childcare = np.zeros(N)
wr,cs,ws=1,1,1

#This is an arbitrary initialization of Utility class
model = util.Utility(param0,N,x_w,x_m,x_k,passign,nkids0,married0,hours,childcare,
	agech0,hours_p,hours_f,wr,cs,ws)

######################################################################
#Creating a grid for the emax computation
#The interpolated dataset
dict_grid=gridemax.grid()




#data for initial state values
data_int_ex=np.concatenate(( np.reshape(np.log(theta0),(N,1)),nkids0,married0,
	np.reshape(np.square(np.log(theta0)),(N,1)),passign,x_wmk ), axis=1)

J = 6

#average emax for the grid of D (for N individuals)
av_emax = []
se_emax = []

for k in range(len(D)):
	
	#The emax interpolated values
	np.random.seed(2)
	emax_function_in=emax.Emaxt(param0,D[k],dict_grid,hours_p,hours_f,wr,cs,ws,model)
	emax_dic = emax_function_in.recursive(8)
	

	emax_t1_int = np.zeros((N,J))
	for j in range(J):
		emax_int_ins = emax_dic[0]['emax1'][j]
		emax_betas = emax_int_ins.betas()
		emax_t1_int[:,j] = emax_int_ins.int_values(data_int_ex,emax_betas)

	#av individual emax and se
	av_emax.append(np.mean(emax_t1_int,axis=0))
	se_emax.append(np.std(emax_t1_int,axis=0))


for k in range(len(D)):
	print ''
	print 'This is Emax1 for D=' + str(D[k]), av_emax[k]
	
for k in range(len(D)):
	print ''
	print 'This is SE_Emax1 for D=' + str(D[k]), se_emax[k]
