"""

exec(open("/home/jrodriguez/NH_HC/codes/model_v2/fit/fit.py").read())

This file computes stats to validate model

It uses:
ate_theta.py
oprobit.py
table_aux.py
ate_emp.py
ate_cc.py
ssrs_obs.do
ssrs_sim.do
ate_cc.do
ate_emp.do

"""
#from __future__ import division #omit for python 3.x#
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
import tracemalloc
import matplotlib
matplotlib.use('Agg') # Force matplotlib to not use any Xwindows backend.
import matplotlib.pyplot as plt
import subprocess
#sys.path.append("C:\\Users\\Jorge\\Dropbox\\Chicago\\Research\\Human capital and the household\]codes\\model")
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

betas_nelder = np.load("/home/jrodriguez/NH_HC/results/Model/estimation/betas_modelv54.npy")


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
gamma1 = 0.95
gamma2 = betas_nelder[13]
gamma3 = betas_nelder[14]
tfp = betas_nelder[15]
sigma2theta = 1

kappas = [0,0]

#first sigma is normalized
sigma_z = [0.15,0.15]

#initial theta
rho_theta_epsilon = betas_nelder[18]


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
nkids0 = x_df[ ['nkids_baseline']   ].values

#marital status at baseline
married0 = x_df[ ['d_marital_2']   ].values

#age of child at baseline
agech0 = x_df[['age_t0']].values

#Defines the instance with parameters
param0 = util.Parameters(alphap,alphaf,mu_c,
	eta,gamma1,gamma2,gamma3,
	tfp,sigma2theta,rho_theta_epsilon,wagep_betas,
	income_male_betas,c_emp_spouse,
	marriagep_betas, kidsp_betas, eitc_list,
	afdc_list,snap_list,cpi,fpl_list,
	lambdas,kappas,pafdc,psnap,mup,sigma_z)


###Auxiliary estimates###
moments_vector = pd.read_csv("/home/jrodriguez/NH_HC/results/model_v2/aux_model/moments_vector.csv").values

#This is the var cov matrix of aux estimates
var_cov = pd.read_csv("/home/jrodriguez/NH_HC/results/model_v2/aux_model/var_cov.csv").values

#The vector of aux standard errors
#Using diagonal of Var-Cov matrix of simulated moments
se_vector  = np.sqrt(np.diagonal(var_cov))

#Creating a grid for the emax computation
dict_grid = gridemax.grid(800)

#For montercarlo integration
D = 25	
 
#For II procedure
M = 10

#How many hours is part- and full-time work
hours_p = 15
hours_f = 40

#Indicate if model includes a work requirement (wr), 
#and child care subsidy (cs) and a wage subsidy (ws)
wr=1
cs=1
ws=1


output_ins = estimate.Estimate(nperiods,param0,x_w,x_m,x_k,x_wmk,passign,
	agech0,nkids0,married0,D,dict_grid,M,N,moments_vector,var_cov,hours_p,hours_f,
	wr,cs,ws)

#The model (utility instance)
hours = np.zeros(N)
childcare  = np.zeros(N)

model  = util.Utility(param0,N,x_w,x_m,x_k,passign,nkids0,
	married0,hours,childcare,agech0,hours_p,hours_f,wr,cs,ws)

#Obtaining emax instances, samples, and betas for M samples
np.random.seed(1)


print('')
print('')
print('Getting a dictionary of emax')
start_emax = time.time()
print('')
print('')

emax_instance = output_ins.emax(param0,model)

time_emax=time.time() - start_emax
print('')
print('')
print('Done with emax in:')
print("--- %s seconds ---" % (time_emax))
print('')
print('')
choices = output_ins.samples(param0,emax_instance,model)
dic_betas = output_ins.aux_model(choices)

np.mean(choices['income_matrix'])



#Getting the simulated betas
#utility_aux
beta_childcare = np.mean(dic_betas['beta_childcare'],axis=0) #1x1
beta_hours1 = np.mean(dic_betas['beta_hours1'],axis=0) #1x1
beta_hours2 = np.mean(dic_betas['beta_hours2'],axis=0) #1x1
beta_wagep = np.mean(dic_betas['beta_wagep'],axis=1) # 6 x 1
beta_inputs = np.mean(dic_betas['beta_inputs'],axis=1) #5 x 1
betas_init_prod = np.mean(dic_betas['betas_init_prod'],axis=1) #1 x 1
beta_wage_spouse = np.mean(dic_betas['beta_wage_spouse'],axis=1)
beta_emp_spouse = np.mean(dic_betas['beta_emp_spouse'],axis=0)


#sample: age of the youngest child is six years or less by t=2
boo_sample = (agech0[:,0]<= 4)

hours = choices['hours_matrix'][:,0,0].copy()
full = hours == hours_f
part = hours == hours_p
work = hours > 0

cc = choices['childcare_matrix'][:,0,0].copy()

tch = np.zeros(N)
boo_p = hours == hours_p
boo_f = hours == hours_f
boo_u = hours == 0

tch[agech0[:,0]<=5] = cc[agech0[:,0]<=5]*(168 - hours_f) + (1-cc[agech0[:,0]<=5])*(168 - hours[agech0[:,0]<=5] ) 
tch[agech0[:,0]>5] = 133 - hours[agech0[:,0]>5]

np.corrcoef(tch,np.log(choices['income_matrix'][:,0,0]))

#proportion of individuals working part- and full-time across years
np.mean(np.mean(full[passign[:,0]==0,:,:],axis=2),axis=0)

#wages across years for working
wages = np.log(choices['wage_matrix'])
np.mean(np.mean(wages[passign[:,0]==0,:,:],axis=2),axis=0)


#################################################################################
#################################################################################
#FIGURE: ATE ON INCOME#
exec(open("/home/jrodriguez/NH_HC/codes/model_v2/fit/ate_inc.py").read())


#################################################################################
#################################################################################
#FIGURE: ATE ON CHILD CARE#
exec(open("/home/jrodriguez/NH_HC/codes/model_v2/fit/ate_cc.py").read())


#################################################################################
#################################################################################
#FIGURE: ATE ON EMPLOYMENT#
exec(open('/home/jrodriguez/NH_HC/codes/model_v2/fit/ate_emp.py').read())


#################################################################################
#################################################################################
#TABLE: COMPARING OPROBITS#
exec(open('/home/jrodriguez/NH_HC/codes/model_v2/fit/oprobit.py').read())


#################################################################################
#################################################################################
#FIGURE: ATE ON THETA#
exec(open('/home/jrodriguez/NH_HC/codes/model_v2/fit/ate_theta.py').read())


#################################################################################
#################################################################################
#TABLE FIT: target moments#
exec(open("/home/jrodriguez/NH_HC/codes/model_v2/fit/table_aux.py").read())

#GRAPHS FIT: target moments#

#################################################################################
#################################################################################
"""
#TABLE: model validation#
ate_hours_obs_2=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/model_v2/fit/ate_hours.csv').values
se_ate_hours_obs_2=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/model_v2/fit/se_ate_hours.csv').values

ate_inc_obs_2=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/model_v2/fit/ate_inc_2.csv').values
se_ate_inc_obs_2=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/model_v2/fit/se_ate_inc_2.csv').values

#these ones are the same as the figure (only 2 data points)
ate_cc_obs=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/model_v2/fit/ate_cc.csv').values
se_ate_cc_obs=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/model_v2/fit/se_ate_cc.csv').values

#Simulated: only during NH
ate_hours_2 = [np.mean(ate_hours[0]),np.mean(ate_hours[1])]
ate_cc_2 = ate_cc[1]

#The list of statistics
sim_list = [ate_hours_2[0],ate_hours_2[1],ate_cc_2,ate_inc[1]]
obs_list = [ate_hours_obs_2[0,0],ate_hours_obs_2[1,0],ate_cc_obs[0,0],ate_inc_obs_2[0,0]]
obs_list_se = [se_ate_hours_obs_2[0,0],se_ate_hours_obs_2[1,0],se_ate_cc_obs[0,0],se_ate_inc_obs_2[0,0]]
var_list = [r'Hours worked ($t=0$)', r'Hours worked ($t=1$)', r'Child care ($t=1$)',r'Log consumption ($t=1$)']

#writing the table
with open('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/model_v2/fit/table_validation.tex','w') as f:
	f.write(r'\begin{tabular}{llccc}'+'\n')
	f.write(r'\hline' + '\n')
	f.write(r'\textbf{Treatment effect} && \textbf{Simulated} && \textbf{Observed} \bigstrut\\' + '\n')
	f.write(r'\cline{1-1}\cline{3-3}\cline{5-5}&&&&  \bigstrut[t]\\' + '\n')
	for j in range(len(sim_list)):
		f.write(var_list[j]+' && ' + 
			'{:04.3f}'.format(sim_list[j]) + 
			r'  & &'+ '{:04.3f}'.format(obs_list[j])+r' \\'+'\n')
		f.write(r' & & & & ( '+ '{:04.3f}'.format(obs_list_se[j])+ r' )\\'+'\n')
		f.write(r'  &       &       &       &  \\'+'\n')

	

	f.write(r'\hline'+'\n')
	f.write(r'\end{tabular}' + '\n')
	f.close()

"""

