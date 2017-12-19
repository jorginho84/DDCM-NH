"""
execfile('elast.py')
This file computes marshallian elasticities

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
import matplotlib
matplotlib.use('Agg') # Force matplotlib to not use any Xwindows backend.
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
sys.path.append("/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/experiments/Elasticities")
from shock import Shock


np.random.seed(1)

betas_nelder=np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/betas_modelv16.npy')

#Number of periods where all children are less than or equal to 18
nperiods = 8

#Utility function
eta=betas_nelder[0]
alphap=betas_nelder[1]
alphaf=betas_nelder[2]

#wage process
wagep_betas=np.array([betas_nelder[3],betas_nelder[4],betas_nelder[5],
	betas_nelder[6],betas_nelder[7],betas_nelder[8],betas_nelder[9]]).reshape((7,1))

#Production function [young,old]
gamma1= betas_nelder[10]
gamma2= betas_nelder[11]
gamma3= betas_nelder[12]
tfp=betas_nelder[13]
sigma2theta=1

kappas=[[betas_nelder[14],betas_nelder[15],betas_nelder[16],betas_nelder[17]],
[betas_nelder[18],betas_nelder[19],betas_nelder[20],betas_nelder[21]]]

#initial theta
rho_theta_epsilon = betas_nelder[22]

#All factor loadings are normalized
lambdas=[1,1]

#Child care price
mup = 0.57*0 + (1-0.57)*750

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
x_wmk=x_df[  ['age_ra', 'age_ra2', 'd_HS2', 'constant'] ].values

#Data for treatment status
passign=x_df[ ['d_RA']   ].values
#passign = np.random.binomial(1,0.5,(N,1))

#The EITC parameters
eitc_list = pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/eitc_list.p', 'rb' ) )

#The AFDC parameters
afdc_list = pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/afdc_list.p', 'rb' ) )

#The SNAP parameters
snap_list = pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/snap_list.p', 'rb' ) )

#CPI index
cpi =  pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/cpi.p', 'rb' ) )


#number of kids at baseline
nkids0=x_df[ ['nkids_baseline']   ].values

#marital status at baseline
married0=x_df[ ['d_marital_2']   ].values

#age of child at baseline
agech0=x_df[['age_t0']].values
age_ch = np.zeros((N,nperiods))
for t in range(nperiods):
	age_ch[:,t] = agech0[:,0] + t



#Defines the instance with parameters
param0=util.Parameters(alphap,alphaf,eta,gamma1,gamma2,gamma3,
	tfp,sigma2theta,rho_theta_epsilon,wagep_betas, marriagep_betas, kidsp_betas, eitc_list,
	afdc_list,snap_list,cpi,lambdas,kappas,pafdc,psnap,mup)

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

#Indicate if model includes a work requirement (wr), 
#and child care subsidy (cs) and a wage subsidy (ws)
wr=1
cs=1
ws=1

#The estimate class
output_ins=estimate.Estimate(nperiods,param0,x_w,x_m,x_k,x_wmk,passign,agech0,nkids0,
	married0,D,dict_grid,M,N,moments_vector,var_cov,hours_p,hours_f,
	wr,cs,ws)

hours = np.zeros(N)
childcare  = np.zeros(N)

model_orig  = util.Utility(param0,N,x_w,x_m,x_k,passign,
	nkids0,married0,hours,childcare,agech0,hours_p,hours_f,wr,cs,ws)

#Obtaining emax instance: this is fixed throughout the exercise
emax_instance = output_ins.emax(param0,model_orig)



#Two models: one with shock = 0 and other where shock>0
shocks = [0,0.1]
choices_c = {}
models = []
for j in range(2):
	np.save('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/NH/shock.npy',shocks[j])
	models.append(Shock(param0,N,x_w,x_m,x_k,passign,
		nkids0,married0,hours,childcare,agech0,hours_p,hours_f,wr,cs,ws))
	choices_c['Choice_' + str(j)] = output_ins.samples(param0,emax_instance,models[j])

