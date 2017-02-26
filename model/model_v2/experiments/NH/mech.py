"""
execfile('mech.py')
This file computes a decomposition analysis of variables that explain ATE on theta

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


np.random.seed(1)

betas_nelder=np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/betas_modelv4_v2.npy')

#Utility function
eta=betas_nelder[0]
alphap=betas_nelder[1]
alphaf=betas_nelder[2]

#wage process
wagep_betas=np.array([betas_nelder[3],betas_nelder[4],betas_nelder[5],
	betas_nelder[6],betas_nelder[7]]).reshape((5,1))


#Production function [young,old]
gamma1=[betas_nelder[8],betas_nelder[10]]
gamma2=[betas_nelder[9],betas_nelder[11]]
tfp=betas_nelder[12]
sigmatheta=0

#Measurement system: three measures for t=2, one for t=5
kappas=[[betas_nelder[13],betas_nelder[14],betas_nelder[15],betas_nelder[16]],
[betas_nelder[17],betas_nelder[18],betas_nelder[19],betas_nelder[20]]]

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
#theta0=np.exp(np.random.randn(N))
theta0=np.ones(N)

#number of kids at baseline
nkids0=x_df[ ['nkids_baseline']   ].values

#marital status at baseline
married0=x_df[ ['d_marital_2']   ].values

#age of child at baseline
agech0=x_df[['age_t0']].values

#Defines the instance with parameters
param0=util.Parameters(alphap, alphaf, eta, gamma1, gamma2, tfp,sigmatheta,
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
hours_f=30

output_ins=estimate.Estimate(param0,x_w,x_m,x_k,x_wmk,passign,agech0,theta0,nkids0,
	married0,D,dict_grid,M,N,moments_vector,var_cov,hours_p,hours_f)

#Obtaining emax instance: this is fixed throughout the exercise
emax_instance = output_ins.emax(param0)

#Original choices (dictionary)
choices = output_ins.samples(param0,emax_instance)

#Obtaining samples with the same emax
choices_c = {}
for j in range(2):
	passign_aux=j*np.ones((N,1))
	output_ins.__dict__['passign'] = passign_aux
	choices_c['Choice_' + str(j)] = output_ins.samples(param0,emax_instance)


#Generating statistics: have to do it by age.
#or maybe it's easier this way" f(input_1) - f(input_0)
#so: compute first choices then, use prod function to produce
#what's easier? maybe go back to the way I used to do it?
#find out first why ATEs give so different. To do this, I need the ate_inputs...

#Age of child
age_ch = np.zeros((N,9))
for t in range(9):
	age_ch[:,t] = agech0[:,0] + t


##################################################
#ATE on theta.
theta_matrix = np.log(choices['theta_matrix'])
ate_theta = np.mean(np.mean(theta_matrix[passign[:,0]==1,:,:],axis=0) - np.mean(theta_matrix[passign[:,0]==0,:,:],axis=0),axis=1)

theta_sim_matrix = []
for j in range(2):
	theta_sim_matrix.append(np.log(choices_c['Choice_' + str(j)]['theta_matrix']))
	
ate_theta_sim = np.mean(np.mean(theta_sim_matrix[1] - theta_sim_matrix[0],axis=0),axis=1)


#ATE on CC
cc_matrix = choices['choice_matrix']>=3
ate_cc = np.mean(np.mean(cc_matrix[passign[:,0]==1,:,:],axis=0) - np.mean(cc_matrix[passign[:,0]==0,:,:],axis=0),axis=1 )

cc_sim_matrix = []
for j in range(2):
	cc_sim_matrix.append(choices_c['Choice_' + str(j)]['choice_matrix']>=3)

ate_cc_sim = np.mean(np.mean(cc_sim_matrix[1],axis=2) - np.mean(cc_sim_matrix[0],axis=2),axis=0)

#ATE on log ct
consumption_matrix = np.log(choices['consumption_matrix'])
ate_ct = np.mean(np.mean(consumption_matrix[passign[:,0]==1,:,:],axis=0) - np.mean(consumption_matrix[passign[:,0]==0,:,:],axis=0),axis=1 )

ct_sim_matrix = []
for j in range(2):
	ct_sim_matrix.append(np.log(choices_c['Choice_' + str(j)]['consumption_matrix']))

ate_ct_sim = np.mean(np.mean(ct_sim_matrix[1] - ct_sim_matrix[0],axis=0),axis=1)

#ATE on log leisure
leisure_matrix = np.log(148 - choices['hours_matrix'])
ate_leisure = np.mean(np.mean(leisure_matrix[passign[:,0]==1,:,:],axis=0) - np.mean(leisure_matrix[passign[:,0]==0,:,:],axis=0),axis=1)

leisure_sim_matrix = []
for j in range(2):
	leisure_sim_matrix.append(np.log(148 - choices_c['Choice_' + str(j)]['hours_matrix']))
ate_leisure_sim = np.mean(np.mean(leisure_sim_matrix[1] - leisure_sim_matrix[0],axis=0),axis=1)



#####The difference in t=1, young vs old

tt = 0
#income
ate_ct_y = np.mean(np.mean(consumption_matrix[(passign[:,0]==1) & (age_ch[:,tt]<=6 ),tt,:],axis=0) - np.mean(consumption_matrix[(passign[:,0]==0) & (age_ch[:,tt]<=6),tt,:],axis=0),axis=0 )
ate_ct_o = np.mean(np.mean(consumption_matrix[(passign[:,0]==1) & (age_ch[:,tt]>6 ),tt,:],axis=0) - np.mean(consumption_matrix[(passign[:,0]==0) & (age_ch[:,tt]>6),tt,:],axis=0),axis=0 )

ate_ct_sim_y = np.mean(np.mean(ct_sim_matrix[1][age_ch[:,tt]<=6,tt,:] - ct_sim_matrix[0][age_ch[:,tt]<=6,tt,:],axis=0),axis=0)
ate_ct_sim_o = np.mean(np.mean(ct_sim_matrix[1][age_ch[:,tt]>6,tt,:] - ct_sim_matrix[0][age_ch[:,tt]>6,tt,:],axis=0),axis=0)

#ct
ate_cc_y = np.mean(np.mean(cc_matrix[(passign[:,0]==1) & (age_ch[:,tt]<=6),tt,:],axis=0) - np.mean(cc_matrix[(passign[:,0]==0) & (age_ch[:,tt]<=6),tt,:],axis=0),axis=0 )

ate_cc_sim_y = np.mean(np.mean(cc_sim_matrix[1][age_ch[:,tt]<=6,tt,:],axis=1) - np.mean(cc_sim_matrix[0][age_ch[:,tt]<=6,tt,:],axis=1),axis=0)


#leisure
ate_lt_y = np.mean(np.mean(leisure_matrix[(passign[:,0]==1) & (age_ch[:,tt]<=6),tt,:],axis=0) - np.mean(leisure_matrix[(passign[:,0]==0) & (age_ch[:,tt]<=6),tt,:],axis=0),axis=0)
ate_lt_o = np.mean(np.mean(leisure_matrix[(passign[:,0]==1) & (age_ch[:,tt]>6),tt,:],axis=0) - np.mean(leisure_matrix[(passign[:,0]==0) & (age_ch[:,tt]>6),tt,:],axis=0),axis=0)

ate_lt_sim_y = np.mean(np.mean(leisure_sim_matrix[1][age_ch[:,tt]<=6,tt,:] - leisure_sim_matrix[0][age_ch[:,tt]<=6,tt,:],axis=0),axis=0)
ate_lt_sim_o = np.mean(np.mean(leisure_sim_matrix[1][age_ch[:,tt]>6,tt,:] - leisure_sim_matrix[0][age_ch[:,tt]>6,tt,:],axis=0),axis=0)

#theta initial
ate_theta_y = np.mean(np.mean(theta_matrix[(passign[:,0]==1) & (age_ch[:,tt]<=6),tt,:],axis=0) - np.mean(theta_matrix[(passign[:,0]==0) & (age_ch[:,tt]<=6),tt,:],axis=0),axis=0)
ate_theta_o = np.mean(np.mean(theta_matrix[(passign[:,0]==1) & (age_ch[:,tt]>6),tt,:],axis=0) - np.mean(theta_matrix[(passign[:,0]==0) & (age_ch[:,tt]>6),tt,:],axis=0),axis=0)

ate_theta_sim_y = np.mean(np.mean(theta_sim_matrix[1][age_ch[:,tt]<=6,tt,:] - theta_sim_matrix[0][age_ch[:,tt]<=6,tt,:],axis=0 ),axis=0)
ate_theta_sim_o = np.mean(np.mean(theta_sim_matrix[1][age_ch[:,tt]>6,tt,:] - theta_sim_matrix[0][age_ch[:,tt]>6,tt,:],axis=0 ),axis=0)


ate_theta_y_1 = np.mean(np.mean(theta_matrix[(passign[:,0]==1) & (age_ch[:,tt]<=6),tt+1,:],axis=0) - np.mean(theta_matrix[(passign[:,0]==0) & (age_ch[:,tt]<=6),tt+1,:],axis=0),axis=0)
ate_theta_o_1 = np.mean(np.mean(theta_matrix[(passign[:,0]==1) & (age_ch[:,tt]>6),tt+1,:],axis=0) - np.mean(theta_matrix[(passign[:,0]==0) & (age_ch[:,tt]>6),tt+1,:],axis=0),axis=0)

ate_theta_sim_y_1 = np.mean(np.mean(theta_sim_matrix[1][age_ch[:,tt]<=6,tt+1,:] - theta_sim_matrix[0][age_ch[:,tt]<=6,tt+1,:],axis=0 ),axis=0)
ate_theta_sim_o_1 = np.mean(np.mean(theta_sim_matrix[1][age_ch[:,tt]>6,tt+1,:] - theta_sim_matrix[0][age_ch[:,tt]>6,tt+1,:],axis=0 ),axis=0)

#try with the SSRS2...see what I can get simulated-RA and simulated all
