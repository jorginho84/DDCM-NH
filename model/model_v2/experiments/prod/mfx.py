"""
execfile('mfx.py')

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
#sys.path.append("C:\\Users\\Jorge\\Dropbox\\Chicago\\Research\\Human capital and the household\]codes\\model")
sys.path.append("/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample")
import utility as util
import gridemax
import time
import int_linear
import emax as emax
import simdata as simdata
import openpyxl
sys.path.append("/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/estimation")
import estimate as estimate


np.random.seed(1)

betas_nelder=np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/betas_modelv10_v1_e3.npy')

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
rho=betas_nelder[13]
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

#number of kids at baseline
nkids0=x_df[ ['nkids_baseline']   ].values

#marital status at baseline
married0=x_df[ ['d_marital_2']   ].values

#age of child at baseline
agech0=x_df[['age_t0']].values

#Defines the instance with parameters
param0=util.Parameters(alphap, alphaf, eta, gamma1, gamma2, 
	gamma3,tfp,rho,sigmatheta,
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

#For II procedure
M=1000

#How many hours is part- and full-time work
hours_p=15
hours_f=40

#Indicate if model includes a work requirement (wr), 
#and child care subsidy (cs) and a wage subsidy (ws)
wr=1
cs=1
ws=1

output_ins=estimate.Estimate(param0,x_w,x_m,x_k,x_wmk,passign,agech0,nkids0,
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
lt=148-eh #nobody in cc
d_cc = np.zeros(N) #nobody in ccc

#Computing mfx
theta_th = np.zeros((N,9)) #shocked
theta_0 = np.zeros((N,9))
theta_0[:,0] = np.mean(theta_matrix[:,0,:],axis=1) #initial value
theta_th[:,0] = theta_0[:,0].copy()

#SD units
sd_matrix = np.zeros((9,M))
for k in range(9):
	for j in range(M):
		sd_matrix[k,j] = np.std(np.log(theta_matrix[:,k,j]),axis=0)
sds = np.mean(sd_matrix,axis=1)

#the shocks
shock_th = theta_0[:,0] + np.exp(np.zeros(N)+0.3)

#theta with no shocks
for k in range(8):
	#no shocks
	theta_0[:,k+1] = np.exp((1/rho)*np.log(gamma1*theta_0[:,k]**rho + gamma2*ec**rho +gamma3*lt**rho))

#Responses
for k in range(8):
	if k==0:
		theta_th[:,k+1] = np.exp((1/rho)*np.log(gamma1*shock_th**rho + gamma2*ec**rho +gamma3*lt**rho))
	else:
		theta_th[:,k+1] = np.exp((1/rho)*np.log(gamma1*theta_th[:,k]**rho + gamma2*ec**rho +gamma3*lt**rho))
#ATE
ate_theta = np.mean(np.log(theta_th) - np.log(theta_0),axis=0)/sds

#mfx: a 1,000 income shock
t0 = (1/rho)*np.log(gamma1*np.ones(N)**rho + gamma2*ec**rho +gamma3*lt**rho)
t1 = (1/rho)*np.log(gamma1*np.ones(N)**rho + gamma2*(ec+1000/(nkids0[:,0] + married0[:,0]))**rho +gamma3*lt**rho)
mfx_c = np.mean(t1-t0)/sds[1]

#mfx: from full time to unemployment
t0 = (1/rho)*np.log(gamma1*np.ones(N)**rho + gamma2*ec**rho +gamma3*lt**rho)
t1 = (1/rho)*np.log(gamma1*np.ones(N)**rho + gamma2*ec**rho +gamma3*(lt+40)**rho)
mfx_t = np.mean(t1-t0)/sds[1]

print ''
print 'impact of 1,000 shock', mfx_c
print ''
print 'impact of unemployment shock', mfx_t


##The graph (shock on theta)
x = np.array(range(0,9))
fig, ax=plt.subplots()
ax.plot(x,ate_theta, color='k',zorder=1,linewidth=3)
ax.set_ylabel(r'Impact on $\ln(\theta_{t+1})$ (in $\sigma$s)', fontsize=14)
ax.set_xlabel(r'Years after random assignment ($t$)', fontsize=14)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
plt.show()
fig.savefig('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/prod/theta_shock.pdf', format='pdf')
plt.close()


