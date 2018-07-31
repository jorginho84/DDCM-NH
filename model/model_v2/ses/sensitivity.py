"""
execfile('sensitivity.py')

This file computes a sensitivity analysis

Following Andrews, Gentzkow and Shapiro (2017, QJE):

betas_sensitivity = \Lambda * g(a)

\Lambda = - (G'WG)^{-1}G'W
G = Jacobian of moments w/r to structural parameters
W = Weighting matrix used in estimation
g(a) = moments evaluated under alternative assumption "a"
bias = bias under alternative assumption "a"

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
sys.path.append("/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/ses")
import se
sys.path.append("/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/experiments/EITC")
from bset2 import Budget


np.random.seed(1)

betas_nelder=np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/betas_modelv21.npy')

#Number of periods where all children are less than or equal to 18
nperiods = 8

#Utility function
eta = betas_nelder[0]
alphap = betas_nelder[1]
alphaf = betas_nelder[2]

#wage process
wagep_betas=np.array([betas_nelder[3],betas_nelder[4],betas_nelder[5],
	betas_nelder[6],betas_nelder[7]]).reshape((5,1))

#Production function [young,old]
gamma1= betas_nelder[8]
gamma2= -betas_nelder[9]
gamma3= betas_nelder[10]
tfp=betas_nelder[11]
sigma2theta=1

kappas=[[betas_nelder[12],betas_nelder[13],betas_nelder[14],betas_nelder[15]],
[betas_nelder[16],betas_nelder[17],betas_nelder[18],betas_nelder[19]]]

#initial theta
rho_theta_epsilon = betas_nelder[20]


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
x_w=x_df[ ['d_HS2', 'constant' ] ].values


#Data for marriage process
#Parameters: marriage. Last one is the constant
x_m=x_df[ ['age_ra', 'constant']   ].values
marriagep_betas=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/marriage_process/betas_m_v2.csv').values

#Data for fertility process (only at X0)
#Parameters: kids. last one is the constant
x_k=x_df[ ['age_ra', 'age_ra2', 'constant']   ].values
kidsp_betas=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/kids_process/betas_kids_v2.csv').values


#Minimum set of x's (for interpolation)
x_wmk=x_df[  ['age_ra','age_ra2', 'd_HS2', 'constant'] ].values

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

#number of kids at baseline
nkids0=x_df[ ['nkids_baseline']   ].values

#marital status at baseline
married0=x_df[ ['d_marital_2']   ].values

#age of child at baseline
agech0=x_df[['age_t0']].values

#Defines the instance with parameters
param0=util.Parameters(alphap,alphaf,eta,gamma1,gamma2,gamma3,
	tfp,sigma2theta, rho_theta_epsilon,wagep_betas, marriagep_betas, kidsp_betas, eitc_list,
	afdc_list,snap_list,cpi,lambdas,kappas,pafdc,psnap,mup)



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
hours_p=20
hours_f=40

#Indicate if model includes a work requirement (wr), 
#and child care subsidy (cs) and a wage subsidy (ws)
wr=1
cs=1
ws=1

#The estimate class
output_ins=estimate.Estimate(nperiods,param0,x_w,x_m,x_k,x_wmk,passign,agech0,nkids0,
	married0,D,dict_grid,M,N,moments_vector,w_matrix,hours_p,hours_f,
	wr,cs,ws)

def syminv(g):
	out = -np.log((2/(g+1)) - 1)
	return out

betas_opt=np.array([eta, alphap,alphaf,wagep_betas[0,0],
	wagep_betas[1,0],wagep_betas[2,0],
	np.log(wagep_betas[3,0]),wagep_betas[4,0],
	gamma1,gamma2,gamma3,tfp,
	kappas[0][0],kappas[0][1],kappas[0][2],kappas[0][3],
	kappas[1][0],kappas[1][1],kappas[1][2],kappas[1][3],
	syminv(rho_theta_epsilon)])

#The SE class
se_ins=se.SEs(output_ins,var_cov,betas_opt)

#Number of parameters and moments
npar = betas_opt.shape[0]
nmom = moments_vector.shape[0]


######################33#Computing the G matrix#########################
G = se_ins.db_dtheta(betas_opt,0.01,nmom,npar) 

################Computing new moments under alternative scenario: no EITC##############
#The EITC parameters
eitc_original = pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/eitc_list.p', 'rb' ) )

#Exp 1: Full EITC vs No EITC
eitc_list_1 = pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/eitc_dic_1.p', 'rb' ) )

#Exp 2: Full EITC vs fixed EITC
eitc_list_2 = pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/eitc_dic_2.p', 'rb' ) )

#Exp 3: Everybody with EITC
eitc_list_3 = pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/eitc_dic_3.p', 'rb' ) )

#Exp 4: Everybody no EITC
eitc_list_4 = pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/eitc_dic_4.p', 'rb' ) )

#Exp 5: A fixed EITC
eitc_list_5 = pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/eitc_dic_5.p', 'rb' ) )

"""
#eitc_list_1: Full EITC vs No EITC
#eitc_list_2: Full EITC vs fixed EITC
#eitc_list_3: Everybody with EITC
#eitc_list_4: Everybody no EITC
#eitc_list_5: Fixed EITC

"""
hours = np.zeros(N)
childcare  = np.zeros(N)

eitc_list = [eitc_list_1,eitc_list_2,eitc_list_3,eitc_list_4,eitc_list_5]

param0=util.Parameters(alphap,alphaf,eta,gamma1,gamma2,gamma3,
	tfp,sigma2theta, rho_theta_epsilon,wagep_betas, marriagep_betas, kidsp_betas, 
	eitc_list[4],afdc_list,snap_list,cpi,lambdas,kappas,pafdc,psnap,mup)

output_ins=estimate.Estimate(nperiods,param0,x_w,x_m,x_k,x_wmk,passign,agech0,nkids0,
	married0,D,dict_grid,M,N,moments_vector,var_cov,hours_p,hours_f,
	wr,cs,ws)

model_eitc = Budget(param0,N,x_w,x_m,x_k,passign,nkids0,married0,
	hours,childcare,agech0,hours_p,hours_f,wr,cs,ws)
emax_instance=output_ins.emax(param0,model_eitc)
choices=output_ins.samples(param0,emax_instance,model_eitc)
dic_betas=output_ins.aux_model(choices)

beta_childcare=np.mean(dic_betas['beta_childcare'],axis=0) #1x1
beta_hours1=np.mean(dic_betas['beta_hours1'],axis=0) #1x1
beta_hours2=np.mean(dic_betas['beta_hours2'],axis=0) #1x1
beta_wagep=np.mean(dic_betas['beta_wagep'],axis=1) # 6 x 1
beta_kappas_t2=np.mean(dic_betas['beta_kappas_t2'],axis=1) #4 x 1
beta_kappas_t5=np.mean(dic_betas['beta_kappas_t5'],axis=1) #4 x 1
beta_inputs=np.mean(dic_betas['beta_inputs'],axis=1) #4 x 1
betas_init_prod=np.mean(dic_betas['betas_init_prod'],axis=1) #1 x 1

#Number of moments to match
num_par=beta_childcare.size + beta_hours1.size + beta_hours2.size + beta_wagep.size + + beta_kappas_t2.size +  beta_kappas_t5.size + beta_inputs.size + betas_init_prod.size

#Outer matrix
x_vector=np.zeros((num_par,1))


x_vector[0:beta_childcare.size,0]=beta_childcare - moments_vector[0,0]

ind=beta_childcare.size
x_vector[ind:ind+beta_hours1.size,0]=beta_hours1 - moments_vector[ind,0]

ind = ind + beta_hours1.size
x_vector[ind:ind+beta_hours2.size,0]=beta_hours2 - moments_vector[ind,0]

ind=ind + beta_hours2.size
x_vector[ind: ind+ beta_wagep.size,0]=beta_wagep - moments_vector[ind:ind+ beta_wagep.size,0]

ind = ind + beta_wagep.size
x_vector[ind:ind + beta_kappas_t2.size,0]=beta_kappas_t2 - moments_vector[ind:ind + beta_kappas_t2.size,0]

ind = ind + beta_kappas_t2.size
x_vector[ind: ind + beta_kappas_t5.size,0] = beta_kappas_t5 - moments_vector[ind: ind + beta_kappas_t5.size,0]

ind = ind + beta_kappas_t5.size
x_vector[ind:ind + beta_inputs.size,0] = beta_inputs - moments_vector[ind:ind + beta_inputs.size,0]

ind = ind + beta_inputs.size
x_vector[ind:ind + betas_init_prod.size,0] = betas_init_prod - moments_vector[ind:ind + betas_init_prod.size,0]
		

######################Computing \Lambda and bias#########################
W = np.zeros((var_cov.shape[0],var_cov.shape[0]))
for i in range(var_cov.shape[0]):
	W[i,i] = var_cov[i,i]**(-1)

left = np.dot(np.transpose(G),W)
Lambda = - np.dot(np.linalg.inv(np.dot(left,G)),left)
bias = np.dot(Lambda,x_vector)

#bias as a % of original
betas_original=np.array([eta, alphap,alphaf,wagep_betas[0,0],
	wagep_betas[1,0],wagep_betas[2,0],
	wagep_betas[3,0],wagep_betas[4,0],
	gamma1,gamma2,gamma3,tfp,
	kappas[0][0],kappas[0][1],kappas[0][2],kappas[0][3],
	kappas[1][0],kappas[1][1],kappas[1][2],kappas[1][3],
	rho_theta_epsilon])

bias_pc = bias[:,0]/np.abs(betas_original)



