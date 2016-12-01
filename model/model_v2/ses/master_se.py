"""
execfile('master_se.py')

This file computes standard errors of structural parameters

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
import estimate_aux as estimate
sys.path.append("/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/ses")
import se


np.random.seed(1)

betas_nelder=np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/betas_modelv2_nelder_v9.npy')

#THIS IS TEMPORARY
betas_nelder2 = np.delete(betas_nelder,30,0)

#Utility function
eta=betas_nelder[0]
alphap=betas_nelder[1]
alphaf=betas_nelder[2]

#wage process
wagep_betas=np.array([betas_nelder[3],betas_nelder[4],betas_nelder[5],
	betas_nelder[6],betas_nelder[7]]).reshape((5,1))


#Production function [young[cc0,cc1],old]
#gamma1=[[betas_nelder[8],betas_nelder[10]],betas_nelder[12]]
#gamma2=[[betas_nelder[9],betas_nelder[11]],betas_nelder[13]]
gamma1=[[0.6,0.7],0.7]
gamma2=[[0.3,0.4],0.4]
sigmatheta=0

#Measurement system: three measures for t=2, one for t=5
kappas=[[[betas_nelder[14],betas_nelder[15],betas_nelder[16],betas_nelder[17]]
,[betas_nelder[18],betas_nelder[19],betas_nelder[20],betas_nelder[21]],
[betas_nelder[22],betas_nelder[23],betas_nelder[24],betas_nelder[25]]],
[[betas_nelder[26],betas_nelder[27],betas_nelder[28],betas_nelder[29]]]]
#First measure is normalized. starting arbitrary values
lambdas=[[1,0.9,0.9],[0.9]]


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
param0=util.Parameters(alphap, alphaf, eta, gamma1, gamma2,sigmatheta,
	wagep_betas, marriagep_betas, kidsp_betas, eitc_list,afdc_list,snap_list,
	cpi,q,scalew,shapew,lambdas,kappas,pafdc,psnap)



###Auxiliary estimates###
moments_vector=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/moments_vector.csv').values

"""
#The betas of child care and hours regressions
beta_cc_aux=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/beta_childcare_v2.csv').values
beta_cc=beta_cc_aux[1].reshape((1,1))
beta_h2=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/beta_level_hours2_v2.csv').values
beta_h3=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/beta_level_hours3_v2.csv').values

#betas in wage process
beta_wage=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/wage_process/betas_v2.csv').values

#betas in prod function
beta_kappas_t2=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/prob_inc_t2.csv').values
beta_lambdas_t2=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/prob_diff.csv').values
beta_inputs_old=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/inputs_moments_old.csv').values
beta_inputs_young_cc0=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/inputs_moments_young_cc0.csv').values
beta_inputs_young_cc1=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/inputs_moments_young_cc1.csv').values
beta_kappas_t5=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/prob_inc_t5.csv').values
beta_lambdas_t5=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/prob_diff_t5.csv').values

betas_dic={'beta_cc':beta_cc,'beta_h2':beta_h2,'beta_h3':beta_h3,
'beta_wage':beta_wage,'beta_kappas_t2':beta_kappas_t2,
'beta_lambdas_t2':beta_lambdas_t2,'beta_inputs_old':beta_inputs_old,
'beta_inputs_young_cc0':beta_inputs_young_cc0,
'beta_inputs_young_cc1':beta_inputs_young_cc1,
'beta_kappas_t5':beta_kappas_t5,'beta_lambdas_t5':beta_lambdas_t5}
"""
#This is the var cov matrix of aux estimates
var_cov=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/var_cov.csv').values

#The W matrix in Wald metric
#Using diagonal of Var-Cov matrix of simulated moments
w_matrix  = np.zeros((var_cov.shape[0],var_cov.shape[0]))
for i in range(var_cov.shape[0]):
	w_matrix[i,i] = var_cov[i,i]

"""
sigma_beta_cc_aux=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/sigma_childcare_v2.csv').values
sigma_beta_cc=sigma_beta_cc_aux[1]
sigma_beta_h2=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/sigma_level_hours2_v2.csv').values
sigma_beta_h3=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/sigma_level_hours3_v2.csv').values

sigma_beta_wage=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/wage_process/sigma_v2.csv').values

sigma_beta_kappas_t2=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/sigma_prob_inc_t2.csv').values
sigma_beta_lambdas_t2=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/sigma_prob_diff.csv').values
sigma_beta_inputs_old=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/sigma_inputs_moments_old.csv').values
sigma_beta_inputs_young_cc0=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/sigma_inputs_moments_young_cc0.csv').values
sigma_beta_inputs_young_cc1=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/sigma_inputs_moments_young_cc1.csv').values
sigma_beta_kappas_t5=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/sigma_prob_inc_t5.csv').values
sigma_beta_lambdas_t5=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/sigma_prob_diff_t5.csv').values

sigma_dic={'sigma_beta_cc':sigma_beta_cc,'sigma_beta_h2':sigma_beta_h2,
'sigma_beta_h3':sigma_beta_h3,'sigma_beta_wage':sigma_beta_wage,
'sigma_beta_kappas_t2':sigma_beta_kappas_t2,
'sigma_beta_lambdas_t2':sigma_beta_lambdas_t2,
'sigma_beta_inputs_old':sigma_beta_inputs_old,
'sigma_beta_inputs_young_cc0':sigma_beta_inputs_young_cc0,
'sigma_beta_inputs_young_cc1':sigma_beta_inputs_young_cc1,
'sigma_beta_kappas_t5':sigma_beta_kappas_t5,
'sigma_beta_lambdas_t5':sigma_beta_lambdas_t5}
"""



#Creating a grid for the emax computation
dict_grid=gridemax.grid()

#For montercarlo integration
D=50

#For II procedure
M=1000

#The estimate class
output_ins=estimate.Estimate(param0,x_w,x_m,x_k,x_wmk,passign,agech0,theta0,nkids0,
	married0,D,dict_grid,M,N,moments_vector,w_matrix)

#The SE class
se_ins=se.SEs(output_ins,var_cov,betas_nelder2)

#The standard errors
ses = se_ins.big_sand(0.00001,36,33) 
