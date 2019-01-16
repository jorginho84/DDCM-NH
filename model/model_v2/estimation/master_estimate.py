"""
exec(open("/home/jrodriguez/NH_HC/codes/model/estimation/master_estimate.py").read())

This file returns the structural parameters' estimates

This master file implements the Wald metric to estimate the structural
parameters

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
sys.path.append("/home/jrodriguez/NH_HC/codes/model/simulate_sample")
import utility as util
import gridemax
import time
import int_linear
import emax as emax
import simdata as simdata
sys.path.append("/home/jrodriguez/NH_HC/codes/model/estimation")
import estimate as estimate

np.random.seed(1)

betas_nelder=np.load('/home/jrodriguez/NH_HC/results/Model/estimation/betas_modelv23.npy')


#Number of periods where all children are less than or equal to 18
nperiods = 8

betas_nelder=np.load("/home/jrodriguez/NH_HC/results/Model/estimation/betas_modelv24.npy")


#Number of periods where all children are less than or equal to 18
nperiods = 8

#Utility function
eta = betas_nelder[0] + 0.1
alphap = betas_nelder[0]
alphaf = betas_nelder[2] - 0.1 

#wage process
wagep_betas=np.array([betas_nelder[3],betas_nelder[4],1.65,
	betas_nelder[6],betas_nelder[7]]).reshape((5,1))

#income process: male
income_male_betas = np.array([0.2,7.2,.32]).reshape((3,1))
c_emp_spouse = .8


#Production function [young,old]
gamma1= betas_nelder[8]
gamma2= 0.05
gamma3= betas_nelder[10] + 0.02
tfp=0.1
sigma2theta = 1
varphi = 0.7


kappas=[[betas_nelder[12],betas_nelder[13],betas_nelder[14],betas_nelder[15]],
[betas_nelder[16]-0.15,betas_nelder[17]-0.15,betas_nelder[18]-0.15,
betas_nelder[19]-0.15]]

#initial theta
rho_theta_epsilon = 0.05
rho_theta_ab = 0.25

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
X_aux=pd.read_csv("/home/jrodriguez/NH_HC/results/Model/sample_model.csv")
x_df=X_aux

#Sample size 
N=X_aux.shape[0]

#Data for wage process
#see wage_process.do to see the order of the variables.
x_w=x_df[ ['d_HS2', 'constant' ] ].values


#Data for marriage process
#Parameters: marriage. Last one is the constant
x_m=x_df[ ['age_ra', 'constant']   ].values
marriagep_betas=pd.read_csv("/home/jrodriguez/NH_HC/results/marriage_process/betas_m_v2.csv").values

#Data for fertility process (only at X0)
#Parameters: kids. last one is the constant
x_k=x_df[ ['age_ra', 'age_ra2', 'constant']   ].values
kidsp_betas=pd.read_csv("/home/jrodriguez/NH_HC/results/kids_process/betas_kids_v2.csv").values

#Minimum set of x's (for interpolation)
x_wmk=x_df[  ['age_ra','age_ra2','d_HS2','constant'] ].values

#Data for treatment status
passign=x_df[ ['d_RA']   ].values

#The EITC parameters
eitc_list = pickle.load( open("/home/jrodriguez/NH_HC/codes/model/simulate_sample/eitc_list.p", 'rb' ) )

#The AFDC parameters
afdc_list = pickle.load( open("/home/jrodriguez/NH_HC/codes/model/simulate_sample/afdc_list.p", 'rb' ) )

#The SNAP parameters
snap_list = pickle.load( open("/home/jrodriguez/NH_HC/codes/model/simulate_sample/snap_list.p", 'rb' ) ) 


#CPI index
cpi =  pickle.load( open("/home/jrodriguez/NH_HC/codes/model/simulate_sample/cpi.p", 'rb' ) )

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
agech0_a=x_df[['age_t0A']].values[:,0]
agech0_b=x_df[['age_t0B']].values[:,0]
d_childb=x_df[['d_childB']].values
d_childa=x_df[['d_childA']].values

#Defines the instance with parameters
param0=util.Parameters(alphap,alphaf,eta,gamma1,gamma2,gamma3,
	tfp,sigma2theta,varphi,rho_theta_epsilon,rho_theta_ab,wagep_betas,
	income_male_betas,c_emp_spouse,
	marriagep_betas, kidsp_betas, eitc_list,
	afdc_list,snap_list,cpi,lambdas,kappas,pafdc,psnap,mup)



###Auxiliary estimates### 
moments_vector=pd.read_csv("/home/jrodriguez/NH_HC/results/aux_model/moments_vector.csv").values

#This is the var cov matrix of aux estimates
var_cov=pd.read_csv("/home/jrodriguez/NH_HC/results/aux_model/var_cov.csv").values

#The W matrix in Wald metric
#Using inverse of diagonal of Var-Cov matrix of simulated moments
w_matrix  = np.zeros((var_cov.shape[0],var_cov.shape[0]))
for i in range(var_cov.shape[0]):
	w_matrix[i,i] = var_cov[i,i]**(-1)


#Creating a grid for the emax computation
dict_grid=gridemax.grid()

#For montercarlo integration
D=20

#Number of samples to produce
M=200


#How many hours is part- and full-time work
hours_p=20
hours_f=40

#Indicate if model includes a work requirement (wr), 
#and child care subsidy (cs) and a wage subsidy (ws)
wr=1
cs=1
ws=1

output_ins=estimate.Estimate(nperiods,param0,x_w,x_m,x_k,x_wmk,passign,
	agech0_a,agech0_b,d_childa,d_childb,nkids0,
	married0,D,dict_grid,M,N,moments_vector,w_matrix,hours_p,hours_f,
	wr,cs,ws)


start_time = time.time()
output=output_ins.optimizer()

time_opt=time.time() - start_time
print ('Done in')
print("--- %s seconds ---" % (time_opt))

def sym(a):
	return ((1/(1+np.exp(-a))) - 0.5)*2

#the list of estimated parameters
eta_opt = output.x[0]
alphap_opt = output.x[1]
alphaf_opt = output.x[2]
betaw0 = output.x[3]
betaw1 = output.x[4]
betaw2 = output.x[5]
betaw3 = np.exp(output.x[6])
betaw4 = output.x[7]
beta_s1 = output.x[8]
beta_s2 = output.x[9]
beta_s3 = output.x[10]
beta_emp_s = output.x[11]
gamma1_opt = output.x[12]
gamma2_opt = output.x[13]
gamma3_opt = output.x[14]
tfp_opt = output.x[15]
kappas_00 = output.x[16]
kappas_01 = output.x[17]
kappas_02 = output.x[18]
kappas_03 = output.x[19]
kappas_10 = output.x[20]
kappas_11 = output.x[21]
kappas_12 = output.x[22]
kappas_13 = output.x[23]
rho_theta_epsilon_opt = sym(output.x[24])
rho_theta_ab = sym(output.x[25])


betas_opt=np.array([eta_opt, alphap_opt,alphaf_opt,
	betaw0,betaw1,betaw2,betaw3,betaw4,
	beta_s1,beta_s2,beta_s3,beta_emp_s,
	gamma1_opt,gamma2_opt,gamma3_opt,tfp_opt,
	kappas_00,kappas_01,kappas_02,kappas_03,
	kappas_10,kappas_11,kappas_12,kappas_13,rho_theta_epsilon_opt,rho_theta_ab])

np.save('/home/jrodriguez/NH_HC/results/Model/estimation/betas_modelv25_twoch.npy',betas_opt)


