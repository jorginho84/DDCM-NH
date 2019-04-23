"""
exec(open("/home/jrodriguez/NH_HC/codes/model_v2/ses/master_se.py").read())


This file computes standard errors of structural parameters

"""


#from __future__ import division #omit for python 3.x
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
sys.path.append("/home/jrodriguez/NH_HC/codes/model_v2/simulate_sample")
import utility as util
import gridemax
import time
import int_linear
import emax as emax
import simdata as simdata
sys.path.append("/home/jrodriguez/NH_HC/codes/model_v2/estimation")
import estimate as estimate
sys.path.append("/home/jrodriguez/NH_HC/codes/model_v2/ses")
import se


np.random.seed(1)

betas_nelder=np.load("/home/jrodriguez/NH_HC/results/model_v2/estimation/betas_modelv27_twoch.npy")

#Number of periods where all children are less than or equal to 18
nperiods = 8

#Utility function
eta = betas_nelder[0]
alphap = betas_nelder[1]
alphaf = betas_nelder[2]

#wage process
wagep_betas=np.array([betas_nelder[3],betas_nelder[4],betas_nelder[5],
	betas_nelder[6],betas_nelder[7]]).reshape((5,1))

#income process: male
income_male_betas = np.array([betas_nelder[8],betas_nelder[9],
	betas_nelder[10]]).reshape((3,1))
c_emp_spouse = betas_nelder[11]


#Production function [young,old]
gamma1= betas_nelder[12]
gamma2= betas_nelder[13]
gamma3= betas_nelder[14] - 0.05
tfp = betas_nelder[15]
sigma2theta = 1



kappas=[[betas_nelder[16],betas_nelder[17],
betas_nelder[18],betas_nelder[19]],
[betas_nelder[20],betas_nelder[21],betas_nelder[22],
betas_nelder[23]]]

#initial theta
rho_theta_epsilon = betas_nelder[24]


lambdas=[1,1]

#Child care price
mup = 0.57*0 + (1-0.57)*750

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

#number of kids at baseline
nkids0=x_df[ ['nkids_baseline']   ].values

#marital status at baseline
married0=x_df[ ['d_marital_2']   ].values

#age of child at baseline
agech0=x_df[['age_t0']].values

#Defines the instance with parameters
param0=util.Parameters(alphap,alphaf,eta,gamma1,gamma2,gamma3,
	tfp,sigma2theta,rho_theta_epsilon,wagep_betas,
	income_male_betas,c_emp_spouse,
	marriagep_betas, kidsp_betas, eitc_list,
	afdc_list,snap_list,cpi,lambdas,kappas,pafdc,psnap,mup)



###Auxiliary estimates###
moments_vector=pd.read_csv("/home/jrodriguez/NH_HC/results/model_v2/aux_model/moments_vector.csv").values

#This is the var cov matrix of aux estimates
var_cov=pd.read_csv("/home/jrodriguez/NH_HC/results/model_v2/aux_model/var_cov.csv").values

#The W matrix in Wald metric
#Using diagonal of Var-Cov matrix of simulated moments
w_matrix  = np.zeros((var_cov.shape[0],var_cov.shape[0]))
for i in range(var_cov.shape[0]):
	w_matrix[i,i] = var_cov[i,i]


#Creating a grid for the emax computation
dict_grid=gridemax.grid()

#For montercarlo integration
D=20

#For II procedure
M=200

#How many hours is part- and full-time work
hours_p=20
hours_f=40

#Indicate if model includes a work requirement (wr), 
#and child care subsidy (cs) and a wage subsidy (ws)
wr=1
cs=1
ws=1

#The estimate class
output_ins=estimate.Estimate(nperiods,param0,x_w,x_m,x_k,x_wmk,passign,
	agech0,nkids0,married0,D,dict_grid,M,N,moments_vector,var_cov,hours_p,hours_f,
	wr,cs,ws)

def syminv(g):
	out = -np.log((2/(g+1)) - 1)
	return out

betas_opt=np.array([eta, alphap,alphaf,wagep_betas[0,0],
	wagep_betas[1,0],wagep_betas[2,0],
	np.log(wagep_betas[3,0]),wagep_betas[4,0],
	income_male_betas[0],income_male_betas[1],income_male_betas[2],
	c_emp_spouse,
	gamma1,gamma2,gamma3,tfp,
	kappas[0][0],kappas[0][1],kappas[0][2],kappas[0][3],
	kappas[1][0],kappas[1][1],kappas[1][2],kappas[1][3],
	syminv(rho_theta_epsilon)])


#Weighting matrix (same as estimation)
w_matrix  = np.zeros((var_cov.shape[0],var_cov.shape[0]))
for i in range(var_cov.shape[0]):
	w_matrix[i,i] = var_cov[i,i]**(-1)

#The SE class
se_ins=se.SEs(output_ins,w_matrix,betas_opt)

#Number of parameters and moments
npar = betas_opt.shape[0]
nmom = moments_vector.shape[0]

#The var-cov matrix of structural parameters
ses = se_ins.big_sand(0.01,nmom,npar)

np.save('/home/jrodriguez/NH_HC/results/model_v2/estimation/sesv3_modelv28.npy',ses['Var_Cov']*(1+1/M))

np.sqrt(np.diagonal(ses['Var_Cov']*(1+1/M)))

np.argmax(np.abs(ses['Gradient'][0,:]))

for s in range(npar):
	print ('This is argmax of gradient' + str(s), np.argmax(np.abs(ses['Gradient'][s,:])))


