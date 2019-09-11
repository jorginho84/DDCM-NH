"""
exec(open("/home/jrodriguez/NH_HC/codes/model_v2/experiments/elasticities/elast.py").read())

This file computes marshallian elasticities

"""
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
sys.path.append("/home/jrodriguez/NH_HC/codes/model_v2/experiments/elasticities")
from shock import Shock


np.random.seed(1)

betas_nelder = np.load("/home/jrodriguez/NH_HC/results/Model/estimation/betas_modelv41.npy")
var_cov_param = np.load('/home/jrodriguez/NH_HC/results/model_v2/estimation/sesv3_modelv41.npy')

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
sigma_z = [1,betas_nelder[18]]


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
param0=util.Parameters(alphap,alphaf,mu_c,
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




#Two models: one with shock = 0 and other where shock>0
shocks = [0,0.01]



###################################################
##Assuming no estimation errors###

def elast_gen(bs,shocks):

	eta=bs[0]
	alphap=bs[1]
	alphaf=bs[2]
	
	#wage process
	wagep_betas=np.array([bs[3],bs[4],bs[5],bs[6],
		bs[7]]).reshape((5,1))

	income_male_betas = np.array([bs[8],bs[9],
		bs[10]]).reshape((3,1))
	c_emp_spouse = bs[11]

	#Production function [young[cc0,cc1],old]
	gamma1 = bs[12]
	gamma2 = bs[13]
	gamma3 = bs[14]
	tfp = bs[15]
	sigma2theta = 1
	
	kappas = [bs[16],bs[17]]

	sigma_z = [1,bs[18]]

	rho_theta_epsilon =  bs[19]

	lambdas=[1,1]

	#Re-defines the instance with parameters 
	param = util.Parameters(alphap,alphaf,mu_c,
	eta,gamma1,gamma2,gamma3,
	tfp,sigma2theta,rho_theta_epsilon,wagep_betas,
	income_male_betas,c_emp_spouse,
	marriagep_betas, kidsp_betas, eitc_list,
	afdc_list,snap_list,cpi,fpl_list,
	lambdas,kappas,pafdc,psnap,mup,sigma_z)


	#The estimate class
	output_ins = estimate.Estimate(nperiods,param,x_w,x_m,x_k,x_wmk,passign,
	agech0,nkids0,married0,D,dict_grid,M,N,moments_vector,var_cov,hours_p,hours_f,
	wr,cs,ws)

	hours = np.zeros(N)
	childcare  = np.zeros(N)

	model_orig  = util.Utility(param,N,x_w,x_m,x_k,passign,nkids0,
	married0,hours,childcare,agech0,hours_p,hours_f,wr,cs,ws)

	#Obtaining emax instance: this is fixed throughout the exercise
	emax_instance = output_ins.emax(param,model_orig)

	choices_c = {}
	models = []
	for j in range(2):
		np.save('/home/jrodriguez/NH_HC/results/model_v2/experiments/NH/shock.npy',shocks[j])
		models.append(Shock(param,N,x_w,x_m,x_k,passign,
			nkids0,married0,hours,childcare,agech0,hours_p,hours_f,wr,cs,ws))
		choices_c['Choice_' + str(j)] = output_ins.samples(param,emax_instance,models[j])


	#Computing changes in % employment for control group
	h_sim_matrix = []
	employment = []
	wages = []
	full = []
	for j in range(2):
		h_sim_matrix.append(choices_c['Choice_' + str(j)]['hours_matrix'])
		employment.append(choices_c['Choice_' + str(j)]['hours_matrix']>0)
		full.append(choices_c['Choice_' + str(j)]['hours_matrix']==hours_f)
		wages.append(choices_c['Choice_' + str(j)]['wage_matrix'])


	#Extensive margin
	elast_extensive = np.zeros(M)
	for j in range(M):
		elast_periods = np.zeros(nperiods)

		for t in range(nperiods):
			
			elast_periods[t] =(np.mean(employment[1][:,t,j],axis=0) - np.mean(employment[0][:,t,j],axis=0))/(shocks[1]*np.mean((employment[0][:,t,j]),axis=0))
		
		elast_extensive[j] = np.mean(elast_periods)


	#Intensive margin
	elast_intensive = np.zeros(M)
	for j in range(M):
		elast_periods = np.zeros(nperiods)

		for t in range(nperiods):
			sample = (employment[0][:,t,j]==1)
			elast_periods[t] = np.mean((h_sim_matrix[1][sample,t,j] - h_sim_matrix[0][sample,t,j]),axis=0)/(shocks[1]*np.mean(h_sim_matrix[0][sample,t,j],axis=0))
		
		elast_intensive[j] = np.mean(elast_periods)

	return {'Extensive': elast_extensive, 'Intensive': elast_intensive }	
	



###################################################



def partial(psi,eps,S,shocks):
	"""
	This function computes gradient of elasticities w/r to parameters
	S: number of structural parameters
	psi: structural parameters
	eps: marginal difference

	"""
	#save results here
	db_dt_extensive = np.zeros(S)
	db_dt_intensive = np.zeros(S)

	for s in range(S):

		#evaluating at optimum
		psi_low = psi.copy()
		psi_high = psi.copy()

		#changing only relevant parameter, one at a time
		h = eps*np.absolute(psi[s])
		psi_low[s] = psi[s] - h
		psi_high[s] = psi[s] + h

		#Computing elasticities
		low = elast_gen(psi_low,shocks)
		high = elast_gen(psi_high,shocks)
		extensive_low = low['Extensive']
		extensive_high = high['Extensive']
		intensive_low = low['Intensive']
		intensive_high = high['Intensive']

		db_dt_extensive[s] = (np.mean(extensive_high - extensive_low)) / (psi_high[s]-psi_low[s])
		db_dt_intensive[s] = (np.mean(intensive_high - intensive_low)) / (psi_high[s]-psi_low[s])

	return {'der_extensive': db_dt_extensive, 'der_intensive': db_dt_intensive}


#Point estimates
elas = elast_gen(betas_nelder,shocks)


#SEs
npar = betas_nelder.shape[0]
derivatives = partial(betas_nelder,0.01,npar,shocks)
der_extensive = derivatives['der_extensive']
der_intensive = derivatives['der_intensive']
se_extensive = np.sqrt(np.dot(np.transpose(der_extensive),np.dot(var_cov_param,der_extensive)))
se_intensive = np.sqrt(np.dot(np.transpose(der_intensive),np.dot(var_cov_param,der_intensive)))


print ('')
print ('Extensive-margin elasticity')
print ('')
print ('Point estimate: ', np.mean(elas['Extensive']))
print ('SE: ', se_extensive)
print ('')
print ('')
print ('Intensive-margin elasticity')
print ('')
print ('Point estimate: ', np.mean(elas['Intensive']))
print ('SE: ', se_intensive)
print ('')








