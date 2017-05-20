"""
execfile('fit.py')

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

betas_nelder=np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/betas_modelv7_v2_e5.npy')

#Utility function
eta=0.05
alphap=-0.02
alphaf=-0.8
alpha_cc=-0.3
alpha_home_hf=-0.08


#wage process
wagep_betas=np.array([betas_nelder[4],betas_nelder[5],betas_nelder[6],
	betas_nelder[7],betas_nelder[8],betas_nelder[9]]).reshape((6,1))


#Production function [young,old]
gamma1=0.9
gamma2= 0.05
gamma3= 0.4
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
param0=util.Parameters(alphap, alphaf, eta, alpha_cc,alpha_home_hf,	gamma1, gamma2, 
	gamma3,tfp,sigmatheta,
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
dic_betas = output_ins.aux_model(choices)

#Getting the simulated betas
#utility_aux
beta_childcare=np.mean(dic_betas['beta_childcare'],axis=0) #1x1
beta_hours1=np.mean(dic_betas['beta_hours1'],axis=0) #1x1
beta_hours2=np.mean(dic_betas['beta_hours2'],axis=0) #1x1
beta_hours3=np.mean(dic_betas['beta_hours3'],axis=0) #1x1
beta_cc_home=np.mean(dic_betas['beta_cc_home'],axis=0) #1x1
beta_wagep=np.mean(dic_betas['beta_wagep'],axis=1) # 6 x 1
beta_kappas_t2=np.mean(dic_betas['beta_kappas_t2'],axis=1) #4 x 3
beta_kappas_t5=np.mean(dic_betas['beta_kappas_t5'],axis=1) #4 x 1
beta_inputs=np.mean(dic_betas['beta_inputs'],axis=1) #4 x 1

#################################################################################
#################################################################################
#FIGURE: ATE ON CONSUMPTION PC#
execfile('/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/fit/ate_inc.py')

#################################################################################
#################################################################################
#FIGURE: ATE ON CHILD CARE#
execfile('/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/fit/ate_cc.py')


#################################################################################
#################################################################################
#FIGURE: ATE ON EMPLOYMENT#
execfile('/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/fit/ate_emp.py')

#################################################################################
#################################################################################
#FIGURE: ATE ON THETA#
execfile('/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/fit/ate_theta.py')


#################################################################################
#################################################################################
#TABLE: COMPARING OPROBITS#
execfile('/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/fit/oprobit.py')

#################################################################################
#################################################################################
#TABLE FIT: target moments#
execfile('/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/fit/table_aux.py')


#################################################################################
#################################################################################

#TABLE: model validation#


ate_part_obs_2=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ate_part_2.csv').values
se_ate_part_obs_2=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/se_ate_part_2.csv').values
ate_full_obs_2=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ate_full_2.csv').values
se_ate_full_obs_2=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/se_ate_full_2.csv').values

ate_inc_obs_2=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ate_inc_2.csv').values
se_ate_inc_obs_2=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/se_ate_inc_2.csv').values

#these ones are the same as the figure (only 2 data points)
ate_cc_obs=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ate_cc.csv').values
se_ate_cc_obs=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/se_ate_cc.csv').values

#from oprobits: beta_t2, beta_t5, betas_t2_obs, betas_t5_obs

#Simulated before/after
ate_cc_2 = [np.mean(ate_cc[0:3]), np.mean(ate_cc[3:])]
ate_inc_2 = [np.mean(ate_inc[0:3])/1000, np.mean(ate_inc[3:])/1000]
ate_part_2 = [np.mean(ate_part[0:3]), np.mean(ate_part[3:])]
ate_full_2 = [np.mean(ate_full[0:3]), np.mean(ate_full[3:])]

#The table

#The list of statistics
sim_list = [ate_cc_2,ate_inc_2,ate_part_2,ate_full_2,[beta_t2[0],beta_t5[0]]]
obs_list = [ate_cc_obs,ate_inc_obs_2/1000,ate_part_obs_2,ate_full_obs_2,np.array([[betas_t2_obs[0,0]], [betas_t5_obs[0,0]]])]
obs_list_se = [se_ate_cc_obs,se_ate_inc_obs_2/1000,se_ate_part_obs_2,se_ate_full_obs_2,np.array([[ses_betas_t2_obs[0,0]],[ses_betas_t5_obs[0,0]]])]
var_list = ['Child care', 'Consumption', 'Part-time', 'Full-time', 'SSRS']

with open('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/table_validation.tex','w') as f:
	f.write(r'\begin{tabular}{llccccc}'+'\n')
	f.write(r'\hline' + '\n')
	f.write(r' && \multicolumn{2}{c}{\textbf{During NH}} & & \multicolumn{2}{c}{\textbf{After NH}} \bigstrut[t]\\' + '\n')
	f.write(r'&& \textbf{Model} & \textbf{Data} &  & \textbf{Model} & \textbf{Data} \bigstrut[b]\\'+'\n')
	f.write(r'\cline{1-1}\cline{3-4}\cline{6-7} & &  &  && &  \bigstrut[t]\\'+'\n')
	

	for j in range(5):
		#ATE
		f.write(r'\textbf{'+var_list[j]+r'} &       & ' + 
			'{:04.3f}'.format(sim_list[j][0]) + 
			r'  & '+ '{:04.3f}'.format(obs_list[j][0,0])+r'  &  & ' +  
			'{:04.3f}'.format(sim_list[j][1]) + 
			r'  & '+ '{:04.3f}'.format(obs_list[j][1,0])+r' \\'+'\n')
		f.write(r' & & & ( '+ '{:04.3f}'.format(obs_list_se[j][0,0])+ 
			r' ) &   &  & ('+ '{:04.3f}'.format(obs_list_se[j][1,0]) +r') \\'+'\n')
		f.write(r'      &       &       &       &       &       &  \\'+'\n')

	f.write(r'\hline'+'\n')
	f.write(r'\end{tabular}' + '\n')
	f.close()

