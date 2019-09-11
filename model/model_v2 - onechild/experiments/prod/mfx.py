"""
exec(open("/home/jrodriguez/NH_HC/codes/model_v2/experiments/prod/mfx.py").read())


This code computes marginal effects of HH inputs on log(theta)

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
import subprocess
sys.path.append("/home/jrodriguez/NH_HC/codes/model_v2/simulate_sample")
import utility as util
import gridemax
import time
import int_linear
import emax as emax
import simdata as simdata
import openpyxl
sys.path.append("/home/jrodriguez/NH_HC/codes/model_v2/estimation")
import estimate as estimate


np.random.seed(1)

betas_nelder = np.load("/home/jrodriguez/NH_HC/results/Model/estimation/betas_modelv41.npy")


#Number of periods where all children are less than or equal to 18
nperiods = 8

#Utility function
eta = betas_nelder[0]
alphap = betas_nelder[1]
alphaf = betas_nelder[2]

mu_c = -0.56

#wage process en employment processes: female
wagep_betas=np.array([betas_nelder[3],betas_nelder[4],betas_nelder[5],
	betas_nelder[6],betas_nelder[7]]).reshape((5,1))

#income process: male
income_male_betas = np.array([betas_nelder[8],betas_nelder[9],
	betas_nelder[10]]).reshape((3,1))
c_emp_spouse = betas_nelder[11]


#Production function [young,old]
gamma1 = betas_nelder[12]
gamma2 = betas_nelder[13]
gamma3 = betas_nelder[14]
tfp = betas_nelder[15]
sigma2theta = 1

kappas = [betas_nelder[16],betas_nelder[17]]

#first sigma is normalized
sigma_z = [0.5,betas_nelder[18]]


#initial theta
rho_theta_epsilon = betas_nelder[19]

#All factor loadings are normalized
lambdas=[1,1]

#Child care price
mup = 750

#Probability of afdc takeup
pafdc=.60

#Probability of snap takeup
psnap=.70

#Data
X_aux=pd.read_csv("/home/jrodriguez/NH_HC/results/model_v2/sample_model.csv")
x_df=X_aux

#Sample size 
N=X_aux.shape[0]

#Data for wage process
#see wage_process.do to see the order of the variables.
x_w=x_df[ ['d_HS2', 'constant' ] ].values


#Data for marriage process
#Parameters: marriage. Last one is the constant
x_m=x_df[ ['age_ra', 'constant']   ].values
marriagep_betas=pd.read_csv("/home/jrodriguez/NH_HC/results/model_v2/marriage_process/betas_m_v2.csv").values

#Data for fertility process (only at X0)
#Parameters: kids. last one is the constant
x_k=x_df[ ['age_ra', 'age_ra2', 'constant']   ].values
kidsp_betas=pd.read_csv("/home/jrodriguez/NH_HC/results/model_v2/kids_process/betas_kids_v2.csv").values


#Minimum set of x's (for interpolation)
x_wmk=x_df[  ['age_ra','age_ra2', 'd_HS2', 'constant'] ].values

#Data for treatment status
passign=x_df[ ['d_RA']   ].values

#The EITC parameters
eitc_list = pickle.load( open("/home/jrodriguez/NH_HC/codes/model_v2/simulate_sample/eitc_list.p", 'rb' ) )

#The AFDC parameters
afdc_list = pickle.load( open("/home/jrodriguez/NH_HC/codes/model_v2/simulate_sample/afdc_list.p", 'rb' ) )

#The SNAP parameters
snap_list = pickle.load( open("/home/jrodriguez/NH_HC/codes/model_v2/simulate_sample/snap_list.p", 'rb' ) ) 

#CPI index
cpi =  pickle.load( open("/home/jrodriguez/NH_HC/codes/model_v2/simulate_sample/cpi.p", 'rb' ) )

#Federal Poverty Lines
fpl_list = pickle.load( open("/home/jrodriguez/NH_HC/codes/model_v2/simulate_sample/fpl_list.p", 'rb' ) )


#Here: the estimates from the auxiliary model
###
###

#Assuming random start
#theta0=np.exp(np.random.randn(N))

#number of kids at baseline
nkids0=x_df[ ['nkids_baseline']   ].values

#marital status at baseline
married0=x_df[ ['d_marital_2']   ].values

#age of child at baseline
agech0=x_df[['age_t0']].values

age_child = np.zeros((N,nperiods))
for t in range(nperiods):
	age_child = agech0 + t

#Defines the instance with parameters
param0 = util.Parameters(alphap,alphaf,mu_c,
	eta,gamma1,gamma2,gamma3,
	tfp,sigma2theta,rho_theta_epsilon,wagep_betas,
	income_male_betas,c_emp_spouse,
	marriagep_betas, kidsp_betas, eitc_list,
	afdc_list,snap_list,cpi,fpl_list,
	lambdas,kappas,pafdc,psnap,mup,sigma_z)



###Auxiliary estimates###
moments_vector=pd.read_csv("/home/jrodriguez/NH_HC/results/model_v2/aux_model/moments_vector.csv").values

#This is the var cov matrix of aux estimates
var_cov=pd.read_csv("/home/jrodriguez/NH_HC/results/model_v2/aux_model/var_cov.csv").values

#The vector of aux standard errors
#Using diagonal of Var-Cov matrix of simulated moments
se_vector  = np.sqrt(np.diagonal(var_cov))


#Creating a grid for the emax computation
dict_grid=gridemax.grid()

#For montercarlo integration
D=50

#For II procedure
M=1000

#How many hours is part- and full-time work
hours_p = 15
hours_f = 40

#Indicate if model includes a work requirement (wr), 
#and child care subsidy (cs) and a wage subsidy (ws)
wr=1
cs=1
ws=1

output_ins=estimate.Estimate(nperiods,param0,x_w,x_m,x_k,x_wmk,passign,agech0,nkids0,
	married0,D,dict_grid,M,N,moments_vector,var_cov,hours_p,hours_f,
	wr,cs,ws)

#The model (utility instance)
hours = np.zeros(N)
childcare  = np.zeros(N)

model  = util.Utility(param0,N,x_w,x_m,x_k,passign,
	nkids0,married0,hours,childcare,agech0,hours_p,hours_f,wr,cs,ws)

#Obtaining emax instances, samples, and betas for M samples
np.random.seed(1)
emax_instance = output_ins.emax(param0,model)
choices = output_ins.samples(param0,emax_instance,model)

#Inputs at mean values
theta_matrix = choices['theta_matrix']
consumption_matrix = choices['consumption_matrix']
hours_matrix = choices['hours_matrix']

#Mean across samples and periods
ec = np.mean(np.mean(consumption_matrix,axis=2),axis=1)
eh = np.zeros(N)+40 #everybody working full time

#assuming baseline period
lt = np.zeros(N)
lt[agech0[:,0]<=5]= 168 - eh[agech0[:,0]<=5] 
lt[agech0[:,0]>5] = 133 - eh[agech0[:,0]>5]
d_cc = np.zeros(N) #nobody in cc

#Computing mfx
theta_th = np.zeros((N,nperiods)) #shocked
theta_0 = np.zeros((N,nperiods))
theta_0[:,0] = np.mean(theta_matrix[:,0,:],axis=1) #initial value
theta_th[:,0] = theta_0[:,0].copy()

#SD units
sd_matrix = np.zeros((nperiods,M))
for k in range(nperiods):
	for j in range(M):
		sd_matrix[k,j] = np.std(np.log(theta_matrix[:,k,j]),axis=0)
sds = np.mean(sd_matrix,axis=1)

#the shocks
shock_th = theta_0[:,0] + np.exp(np.zeros(N)+0.3)

#theta with no shocks
for k in range(nperiods - 1):
	#no shocks
	theta_0[:,k+1] = np.exp(gamma1*np.log(theta_0[:,k]) + gamma2*np.log(ec) +gamma3*np.log(lt))

#Responses
for k in range(nperiods - 1):
	if k==0:
		theta_th[:,k+1] = np.exp(gamma1*np.log(shock_th) + gamma2*np.log(ec) +gamma3*np.log(lt))
	else:
		theta_th[:,k+1] = np.exp(gamma1*np.log(theta_th[:,k]) + gamma2*np.log(ec) +gamma3*np.log(lt))
#ATE
ate_theta = np.mean(np.log(theta_th) - np.log(theta_0),axis=0)/sds

#mfx: a 1,000 income shock
t0 = gamma1*np.log(np.ones(N)) + gamma2*np.log(ec) +gamma3*np.log(lt)
t1 = gamma1*np.log(np.ones(N)) + gamma2*np.log(ec+1000/(nkids0[:,0] + married0[:,0])) +gamma3*np.log(lt)
mfx_c = np.mean(t1-t0)/sds[1]

#mfx: a mup*12 shock income shock
t0 = gamma1*np.log(np.ones(N)) + gamma2*np.log(ec) +gamma3*np.log(lt)
t1 = gamma1*np.log(np.ones(N)) + gamma2*np.log(ec+mup*12/(nkids0[:,0] + married0[:,0])) +gamma3*np.log(lt)
mfx_c_mu = np.mean(t1-t0)/sds[1]


#mfx: from full time to unemployment
t0 = gamma1*np.log(np.ones(N)) + gamma2*np.log(ec) +gamma3*np.log(lt)
t1 = gamma1*np.log(np.ones(N)) + gamma2*np.log(ec) +gamma3*np.log((lt+40))
mfx_t = np.mean(t1-t0)/sds[1]

#mfx: impact of child care (everybody young)
tau = 168 - eh
t0 = gamma1*np.log(np.ones(N)) + gamma2*np.log(ec) +gamma3*np.log(tau)
t1 = gamma1*np.log(np.ones(N)) + gamma2*np.log(ec) +gamma3*np.log(tau) + tfp*np.ones(N)
mfx_cc = np.mean(t1-t0)/sds[1]


print('')
print('impact of 1,000 shock', mfx_c)
print('')
print ('')
print('impact of mup*12 shock', mfx_c_mu)
print('')
print('impact of unemployment shock', mfx_t)
print('')
print('impact of cc shock', mfx_cc)




