"""
execfile('fit.py')

This file compares simulated and observed target moments

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
import openpyxl
sys.path.append("/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/estimation")
import estimate_timing as estimate


np.random.seed(1)

betas_nelder=np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/betas_modelv2_nelder_v9.npy')

#Utility function
eta=betas_nelder[0]
alphap=betas_nelder[1]
alphaf=betas_nelder[2]

#wage process
wagep_betas=np.array([betas_nelder[3],betas_nelder[4],betas_nelder[5],
	betas_nelder[6],betas_nelder[7]]).reshape((5,1))


#Production function [young[cc0,cc1],old]
gamma1=[[0.6,0.7],0.7]
gamma2=[[0.3,0.4],0.4]
sigmatheta=0

#Measurement system: three measures for t=2, one for t=5
kappas=[[[betas_nelder[14],betas_nelder[15],betas_nelder[16],betas_nelder[17]]
,[betas_nelder[18],betas_nelder[19],betas_nelder[20],betas_nelder[21]],
[betas_nelder[22],betas_nelder[23],betas_nelder[24],betas_nelder[25]]],
[[betas_nelder[26],betas_nelder[27],betas_nelder[28],betas_nelder[29]]]]
lambdas=[[betas_nelder[30],betas_nelder[31],betas_nelder[32]],[betas_nelder[33]]]


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



###Auxiliary estimates### (pending)
#The betas of child care and hours regressions
beta_cc_aux=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/beta_childcare_v2.csv').values
beta_cc=beta_cc_aux[1].reshape((1,1))
beta_h2=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/beta_level_hours2_v2.csv').values
beta_h3=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/beta_level_hours3_v2.csv').values

#betas in wage process
beta_wage=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/wage_process/betas_v2.csv').values

#betas in prod function
beta_kappas_t2_data=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/prob_inc_t2.csv').values
beta_lambdas_t2_data=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/prob_diff.csv').values
beta_inputs_old=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/inputs_moments_old.csv').values
beta_inputs_young_cc0=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/inputs_moments_young_cc0.csv').values
beta_inputs_young_cc1=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/inputs_moments_young_cc1.csv').values
beta_kappas_t5_data=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/prob_inc_t5.csv').values
beta_lambdas_t5_data=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/prob_diff_t5.csv').values

betas_dic={'beta_cc':beta_cc,'beta_h2':beta_h2,'beta_h3':beta_h3,
'beta_wage':beta_wage,'beta_kappas_t2':beta_kappas_t2_data,
'beta_lambdas_t2':beta_lambdas_t2_data,'beta_inputs_old':beta_inputs_old,
'beta_inputs_young_cc0':beta_inputs_young_cc0,
'beta_inputs_young_cc1':beta_inputs_young_cc1,
'beta_kappas_t5':beta_kappas_t5_data,'beta_lambdas_t5':beta_lambdas_t5_data}

#For the W matrix in Wald metric
sigma_beta_cc_aux=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/sigma_childcare_v2.csv').values
sigma_beta_cc=sigma_beta_cc_aux[1]
sigma_beta_h2=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/sigma_level_hours2_v2.csv').values
sigma_beta_h3=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/sigma_level_hours3_v2.csv').values

sigma_beta_wage=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/wage_process/sigma_v2.csv').values

sigma_beta_kappas_t2_data=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/sigma_prob_inc_t2.csv').values
sigma_beta_lambdas_t2_data=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/sigma_prob_diff.csv').values
sigma_beta_inputs_old=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/sigma_inputs_moments_old.csv').values
sigma_beta_inputs_young_cc0=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/sigma_inputs_moments_young_cc0.csv').values
sigma_beta_inputs_young_cc1=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/sigma_inputs_moments_young_cc1.csv').values
sigma_beta_kappas_t5_data=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/sigma_prob_inc_t5.csv').values
sigma_beta_lambdas_t5_data=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/sigma_prob_diff_t5.csv').values

sigma_dic={'sigma_beta_cc':sigma_beta_cc,'sigma_beta_h2':sigma_beta_h2,
'sigma_beta_h3':sigma_beta_h3,'sigma_beta_wage':sigma_beta_wage,
'sigma_beta_kappas_t2':sigma_beta_kappas_t2_data,
'sigma_beta_lambdas_t2':sigma_beta_lambdas_t2_data,
'sigma_beta_inputs_old':sigma_beta_inputs_old,
'sigma_beta_inputs_young_cc0':sigma_beta_inputs_young_cc0,
'sigma_beta_inputs_young_cc1':sigma_beta_inputs_young_cc1,
'sigma_beta_kappas_t5':sigma_beta_kappas_t5_data,
'sigma_beta_lambdas_t5':sigma_beta_lambdas_t5_data}


#Creating a grid for the emax computation
dict_grid=gridemax.grid()

#For montercarlo integration
D=50

#For II procedure
M=1000

output_ins=estimate.Estimate(param0,x_w,x_m,x_k,x_wmk,passign,agech0,theta0,nkids0,
	married0,D,dict_grid,M,N,betas_dic,sigma_dic)

#Obtaining emax instances, samples, and betas for M samples
emax_instance = output_ins.emax(param0)
choices = output_ins.samples(param0,emax_instance)
dic_betas = output_ins.aux_model(choices)

#Getting the simulated betas
#utility_aux
beta_childcare=np.mean(dic_betas['beta_childcare'],axis=0) #1x1
beta_hours2=np.mean(dic_betas['beta_hours2'],axis=0) #1x1
beta_hours3=np.mean(dic_betas['beta_hours3'],axis=0) #1x1
beta_wagep=np.mean(dic_betas['beta_wagep'],axis=1) # 5 x 1
beta_kappas_t2=np.mean(dic_betas['beta_kappas_t2'],axis=2) #4 x 3
beta_lambdas_t2=np.mean(dic_betas['beta_lambdas_t2'],axis=1) #2 x 1
beta_kappas_t5=np.mean(dic_betas['beta_kappas_t5'],axis=1) #4 x 1
beta_lambdas_t5=np.mean(dic_betas['beta_lambdas_t5'],axis=1) #1 x 1
beta_inputs_old_sim=np.mean(dic_betas['beta_inputs_old'],axis=1) #3 x 1
beta_inputs_young_cc0_sim=np.mean(dic_betas['beta_inputs_young_cc0'],axis=1) #3 x 1
beta_inputs_young_cc1_sim=np.mean(dic_betas['beta_inputs_young_cc1'],axis=1) #3 x 1
"""
#Data equivalent
beta_childcare_data=self.betas_dic['beta_cc']
beta_hours2_data=self.betas_dic['beta_h2']
beta_hours3_data=self.betas_dic['beta_h3']
beta_wagep_data=self.betas_dic['beta_wage']
beta_kappas_t2_data=self.betas_dic['beta_kappas_t2']
beta_lambdas_t2_data=self.betas_dic['beta_lambdas_t2']
beta_kappas_t5_data=self.betas_dic['beta_kappas_t5']
beta_lambdas_t5_data=self.betas_dic['beta_lambdas_t5']
beta_inputs_old_data=self.betas_dic['beta_inputs_old']
beta_inputs_young_cc0_data=self.betas_dic['beta_inputs_young_cc0']
beta_inputs_young_cc1_data=self.betas_dic['beta_inputs_young_cc1']

#W matrix
sigma_beta_cc=self.sigma_dic['sigma_beta_cc']
sigma_beta_h2=self.sigma_dic['sigma_beta_h2']
sigma_beta_h3=self.sigma_dic['sigma_beta_h3']
sigma_beta_wage=self.sigma_dic['sigma_beta_wage']
sigma_beta_kappas_t2=self.sigma_dic['sigma_beta_kappas_t2']
sigma_beta_lambdas_t2=self.sigma_dic['sigma_beta_lambdas_t2']
sigma_beta_kappas_t5=self.sigma_dic['sigma_beta_kappas_t5']
sigma_beta_lambdas_t5=self.sigma_dic['sigma_beta_lambdas_t5']
sigma_beta_inputs_old=self.sigma_dic['sigma_beta_inputs_old']
sigma_beta_inputs_young_cc0=self.sigma_dic['sigma_beta_inputs_young_cc0']
sigma_beta_inputs_young_cc1=self.sigma_dic['sigma_beta_inputs_young_cc1']
"""

########Opening workbook#######
wb=openpyxl.load_workbook('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/fit.xlsx')
ws = wb["new_moments"]

#A. Labor supply and child care decisions
list_aux = [beta_childcare,beta_hours2,beta_hours3]
list_obs = [beta_cc,beta_h2,beta_h3]
list_sig = [sigma_beta_cc,sigma_beta_h2,sigma_beta_h3]
for c in range(3):
	sim_moment = ws.cell('E' + str(c + 4))
	obs_moment = ws.cell('G' + str(c + 4))
	obs_sigma = ws.cell('I' + str(c + 4))
	sim_moment.value = np.float(list_aux[c])
	obs_moment.value = np.float(list_obs[c])
	obs_sigma.value = np.float(list_sig[c]**.5)


#B. Log wage equation
for c in range(5):
	sim_moment = ws.cell('E' + str(c + 9))
	obs_moment = ws.cell('G' + str(c + 9))
	obs_sigma = ws.cell('I' + str(c + 9))
	sim_moment.value = np.float(beta_wagep[c])
	obs_moment.value = np.float(beta_wage[c,0])
	obs_sigma.value = np.float(sigma_beta_wage[c,0]**.5)

#C. Measures of academic achievement and family choices

#C.1 and C.2 Age>5 and Age<=5
list_aux = [beta_inputs_old_sim, beta_inputs_young_cc0_sim, 
beta_inputs_young_cc1_sim]
list_obs = [beta_inputs_old, beta_inputs_young_cc0, 
beta_inputs_young_cc1]
list_sig = [sigma_beta_inputs_old, sigma_beta_inputs_young_cc0, 
sigma_beta_inputs_young_cc1]

for j in range(3):
	if j==0:
		pos = 18
	elif j==1:
		pos = 23
	else:
		pos = 26
	
	for c in range(3): # 3 moments each
		sim_moment = ws.cell('E' + str(c + pos))
		obs_moment = ws.cell('G' + str(c + pos))
		obs_sigma = ws.cell('I' + str(c + pos))
		sim_moment.value = np.float(list_aux[j][c])
		obs_moment.value = np.float(list_obs[j][c,0])
		obs_sigma.value = np.float(list_sig[j][c,0]**.5)

ws = wb["new_moments_2"]

#A. t=2, kappas
it = 5
for c in range(4):
	for m in range(3):
 		sim_moment = ws.cell('E' + str(it))
 		obs_moment = ws.cell('G' + str(it))
		obs_sigma = ws.cell('I' + str(it))
		sim_moment.value = np.float(beta_kappas_t2[c,m])
		obs_moment.value = np.float(beta_kappas_t2_data[c,m])
		obs_sigma.value = np.float(sigma_beta_kappas_t2_data[c,m]**.5)

		it = it + 1

#A. t=2, lambdas
for c in range(2):
	sim_moment = ws.cell('E' + str(c + 17))
	obs_moment = ws.cell('G' + str(c + 17))
	obs_sigma = ws.cell('I' + str(c + 17))
	sim_moment.value = np.float(beta_lambdas_t2[c])
	obs_moment.value = np.float(beta_lambdas_t2_data[c,0])
	obs_sigma.value = np.float(sigma_beta_lambdas_t2_data[c,0]**.5)

#B. t=5, kappas
for c in range(4):
	sim_moment = ws.cell('E' + str(c + 21))
	obs_moment = ws.cell('G' + str(c + 21))
	obs_sigma = ws.cell('I' + str(c + 21))
	sim_moment.value = np.float(beta_kappas_t5[c])
	obs_moment.value = np.float(beta_kappas_t5_data[c,0])
	obs_sigma.value = np.float(sigma_beta_kappas_t5_data[c,0]**.5)

#B. t=5, lambda
sim_moment = ws.cell('E' + str(25))
obs_moment = ws.cell('G' + str(25))
obs_sigma = ws.cell('I' + str(25))
sim_moment.value = np.float(beta_lambdas_t5[0])
obs_moment.value = np.float(beta_lambdas_t5_data[0,0])
obs_sigma.value = np.float(sigma_beta_lambdas_t5_data[0,0]**.5)



wb.save('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/fit.xlsx')