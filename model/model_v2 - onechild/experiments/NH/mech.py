"""
exec(open("/home/jrodriguez/NH_HC/codes/model/experiments/NH/mech.py").read())

This file computes a decomposition analysis of variables that explain ATE on theta

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
sys.path.append("/home/jrodriguez/NH_HC/codes/model/experiments/NH")
from util2 import Prod2



np.random.seed(1)

betas_nelder=np.load('/home/jrodriguez/NH_HC/results/Model/estimation/betas_modelv24.npy')

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
X_aux=pd.read_csv('/home/jrodriguez/NH_HC/results/Model/sample_model.csv')
x_df=X_aux

#Sample size 
N=X_aux.shape[0]

#Data for wage process
#see wage_process.do to see the order of the variables.
x_w=x_df[ ['d_HS2', 'constant' ] ].values


#Data for marriage process
#Parameters: marriage. Last one is the constant
x_m=x_df[ ['age_ra', 'constant']   ].values
marriagep_betas=pd.read_csv('/home/jrodriguez/NH_HC/results/marriage_process/betas_m_v2.csv').values

#Data for fertility process (only at X0)
#Parameters: kids. last one is the constant
x_k=x_df[ ['age_ra', 'age_ra2', 'constant']   ].values
kidsp_betas=pd.read_csv('/home/jrodriguez/NH_HC/results/kids_process/betas_kids_v2.csv').values


#Minimum set of x's (for interpolation)
x_wmk=x_df[  ['age_ra','age_ra2', 'd_HS2', 'constant'] ].values

#Data for treatment status
passign=x_df[ ['d_RA']   ].values
#passign = np.random.binomial(1,0.5,(N,1))

#The EITC parameters
eitc_list = pickle.load( open("/home/jrodriguez/NH_HC/codes/model/simulate_sample/eitc_list.p", 'rb' ) )

#The AFDC parameters
afdc_list = pickle.load( open("/home/jrodriguez/NH_HC/codes/model/simulate_sample/afdc_list.p", 'rb' ) )

#The SNAP parameters
snap_list = pickle.load( open("/home/jrodriguez/NH_HC/codes/model/simulate_sample/snap_list.p", 'rb' ) ) 


#CPI index
cpi =  pickle.load( open("/home/jrodriguez/NH_HC/codes/model/simulate_sample/cpi.p", 'rb' ) )


#number of kids at baseline
nkids0=x_df[ ['nkids_baseline']   ].values

#marital status at baseline
married0=x_df[ ['d_marital_2']   ].values

#age of child at baseline
#age of child at baseline
agech0_a=x_df[['age_t0A']].values[:,0]
agech0_b=x_df[['age_t0B']].values[:,0]
d_childb=x_df[['d_childB']].values
d_childa=x_df[['d_childA']].values

agech_a = np.zeros((N,nperiods))
agech_b = np.zeros((N,nperiods))

for periodt in range(nperiods):
	agech_a[d_childa[:,0] == 1,periodt] = agech0_a[d_childa[:,0] == 1] + periodt
	agech_b[d_childb[:,0] == 1,periodt] = agech0_b[d_childb[:,0] == 1] + periodt


agech = np.concatenate((agech_a[d_childa[:,0] == 1,:],
	agech_b[d_childb[:,0] == 1,:]),axis=0)


#Defines the instance with parameters
param0 = util.Parameters(alphap,alphaf,eta,gamma1,gamma2,gamma3,
	tfp,sigma2theta,varphi,rho_theta_epsilon,rho_theta_ab,wagep_betas,
	income_male_betas,c_emp_spouse,
	marriagep_betas, kidsp_betas, eitc_list,
	afdc_list,snap_list,cpi,lambdas,kappas,pafdc,psnap,mup)


###Auxiliary estimates###
moments_vector=pd.read_csv('/home/jrodriguez/NH_HC/results/aux_model/moments_vector.csv').values

#This is the var cov matrix of aux estimates
var_cov=pd.read_csv('/home/jrodriguez/NH_HC/results/aux_model/var_cov.csv').values

#The vector of aux standard errors
#Using diagonal of Var-Cov matrix of simulated moments
se_vector  = np.sqrt(np.diagonal(var_cov))


#Creating a grid for the emax computation
dict_grid=gridemax.grid()

#For montercarlo integration
D = 20		

#Number of samples to produce
M = 200

#How many hours is part- and full-time work
hours_p=20
hours_f=40

#Indicate if model includes a work requirement (wr), 
#and child care subsidy (cs) and a wage subsidy (ws)
wr=1
cs=1
ws=1

#The estimate class
output_ins = estimate.Estimate(nperiods,param0,x_w,x_m,x_k,x_wmk,passign,
	agech0_a,agech0_b,d_childa,d_childb,nkids0,
	married0,D,dict_grid,M,N,moments_vector,var_cov,hours_p,hours_f,
	wr,cs,ws)

#The model (utility instance)
hours = np.zeros(N)
childcare  = np.zeros(N)

model  = util.Utility(param0,N,x_w,x_m,x_k,passign,nkids0,
	married0,hours,childcare,childcare,
	agech0_a,agech0_b,d_childa,d_childb,hours_p,hours_f,wr,cs,ws)

#Obtaining emax instance: this is fixed throughout the exercise
emax_instance = output_ins.emax(param0,model)

#Original choices (dictionary)
choices = output_ins.samples(param0,emax_instance,model)


#The E[Log] of consumption, leisure, and child care to normalize E[log theta]=0
ec = np.mean(np.mean(np.log(choices['consumption_matrix']),axis=2),axis=0)
hours_m = choices['hours_matrix'].copy()
boo_p = hours_m == hours_p
boo_f = hours_m == hours_f
boo_u = hours_m == 0
cc_a = choices['childcare_a_matrix'].copy()
cc_b = choices['childcare_b_matrix'].copy()
ecc_a = np.mean(np.mean(cc_a,axis=2),axis=0)
ecc_b = np.mean(np.mean(cc_a,axis=2),axis=0)


tch_a = np.zeros((N,nperiods,M))
tch_b = np.zeros((N,nperiods,M))
for t in range(nperiods):
	tch_a[agech_a[:,t]<=5,t,:] = cc_a[agech_a[:,t]<=5,t,:]*(168 - hours_f) + (1-cc_a[agech_a[:,t]<=5,t,:])*(168 - hours_m[agech_a[:,t]<=5,t,:])
	tch_a[agech_a[:,t]>5,t,:] = 133 - hours_m[agech_a[:,t]>5,t,:]

	tch_b[agech_b[:,t]<=5,t,:] = cc_b[agech_b[:,t]<=5,t,:]*(168 - hours_f) + (1-cc_b[agech_b[:,t]<=5,t,:])*(168 - hours_m[agech_b[:,t]<=5,t,:])
	tch_b[agech_b[:,t]>5,t,:] = 133 - hours_m[agech_b[:,t]>5,t,:]

el_a = np.mean(np.mean(np.log(tch_a),axis=2),axis=0)
el_b = np.mean(np.mean(np.log(tch_b),axis=2),axis=0)
e_age_a = np.mean(agech_a<=5,axis=0)
e_age_b = np.mean(agech_b<=5,axis=0)
np.save('/home/jrodriguez/NH_HC/results/Model/experiments/NH/ec.npy',ec)
np.save('/home/jrodriguez/NH_HC/results/Model/experiments/NH/el_a.npy',el_a)
np.save('/home/jrodriguez/NH_HC/results/Model/experiments/NH/el_b.npy',el_b)
np.save('/home/jrodriguez/NH_HC/results/Model/experiments/NH/ecc_a.npy',ecc_a)
np.save('/home/jrodriguez/NH_HC/results/Model/experiments/NH/ecc_b.npy',ecc_b)
np.save('/home/jrodriguez/NH_HC/results/Model/experiments/NH/e_age_a.npy',e_age_a)
np.save('/home/jrodriguez/NH_HC/results/Model/experiments/NH/e_age_b.npy',e_age_b)

#E[ln \theta] by period
e_lnt_a = np.mean(np.mean(np.log(choices['theta_matrix_a'][d_childa[:,0]==1,:,:]),axis=0),axis=1)
e_lnt_b = np.mean(np.mean(np.log(choices['theta_matrix_b'][d_childb[:,0]==1,:,:]),axis=0),axis=1)
sd_lnt_a = np.mean(np.std(np.log(choices['theta_matrix_a'][d_childb[:,0]==1,:,:]),axis=0),axis=1)
sd_lnt_a = np.mean(np.std(np.log(choices['theta_matrix_b'][d_childb[:,0]==1,:,:]),axis=0),axis=1)


#Obtaining counterfactual samples with the same emax
choices_c = {}
models = []
for j in range(2):
	passign_aux=j*np.ones((N,1))
	models.append(Prod2(param0,N,x_w,x_m,x_k,passign,nkids0,
	married0,hours,childcare,childcare,
	agech0_a,agech0_b,d_childa,d_childb,hours_p,hours_f,wr,cs,ws))
	output_ins.__dict__['passign'] = passign_aux
	choices_c['Choice_' + str(j)] = output_ins.samples(param0,emax_instance,models[j])

##################################################
#ATE on theta.
theta_matrix_a = np.log(choices['theta_matrix_a'])
theta_matrix_b = np.log(choices['theta_matrix_b'])
theta_matrix = np.concatenate((theta_matrix_a[d_childa[:,0]==1,:,:],
	theta_matrix_b[d_childb[:,0]==1,:,:]),axis=0)

passign_aux = np.concatenate((passign[d_childa[:,0]==1,0],
	passign[d_childb[:,0]==1,0]),axis=0)

ltheta = np.zeros((theta_matrix.shape[0],nperiods,M))
sd_matrix = np.zeros((nperiods,M))
for j in range (M):
	for t in range(nperiods):
		sd_matrix[t,j] = np.std(theta_matrix[:,t,j],axis=0)
		ltheta[:,t,j] = (theta_matrix[:,t,j] - np.mean(theta_matrix[:,t,j],axis=0))/np.std(theta_matrix[:,t,j],axis=0)

ate_theta_sd = np.mean(np.mean(ltheta[passign_aux==1,:,:],axis=0) - np.mean(ltheta[passign_aux==0,:,:],axis=0),axis=1)

theta_sim_matrix = []
for j in range(2):
	#theta_sim_matrix_a.append(choices_c['Choice_' + str(j)]['theta_matrix_a'])
	#theta_sim_matrix_b.append(choices_c['Choice_' + str(j)]['theta_matrix_b'])
	theta_a = choices_c['Choice_' + str(j)]['theta_matrix_a'][d_childa[:,0]==1,:,:]
	theta_b = choices_c['Choice_' + str(j)]['theta_matrix_b'][d_childb[:,0]==1,:,:]

	theta_sim_matrix.append(np.concatenate((theta_a,theta_b),axis=0))

#For measuring in SD units
theta_sd = [np.zeros((theta_matrix.shape[0],nperiods,M)),np.zeros((theta_matrix.shape[0],nperiods,M))]

for j in range(M):
	for t in range(nperiods):
		for k in range(2):
			theta_sd[k][:,t,j] = np.log(theta_sim_matrix[k][:,t,j])/sd_matrix[t,j]


#Choices
cc_sim_matrix_a = []
cc_sim_matrix_b = []
for j in range(2):
	cc_sim_matrix_a.append(choices_c['Choice_' + str(j)]['childcare_a_matrix'])
	cc_sim_matrix_b.append(choices_c['Choice_' + str(j)]['childcare_b_matrix'])

ct_sim_matrix = []
for j in range(2):
	ct_sim_matrix.append(choices_c['Choice_' + str(j)]['consumption_matrix'])

#impact on period 0
ate_ct_sim = np.mean(np.mean(ct_sim_matrix[1][:,0,:] - ct_sim_matrix[0][:,0,:],axis=1),axis=0)

income_sim_matrix = []
for j in range(2):
	income_sim_matrix.append(choices_c['Choice_' + str(j)]['income_matrix'])

ate_income_sim = np.mean(np.mean(income_sim_matrix[1][:,0,:] - income_sim_matrix[0][:,0,:],axis=1),axis=0)


h_sim_matrix = []
for j in range(2):
	h_sim_matrix.append(choices_c['Choice_' + str(j)]['hours_matrix'])

ate_theta_sim = np.zeros((nperiods,M))
ate_theta_sim_sd = np.zeros((nperiods,M))
for j  in range(M):
	for t in range(nperiods):
		ate_theta_sim_sd[t,j] = 	np.mean(theta_sd[1][:,t,j] - theta_sd[0][:,t,j],axis=0)
		ate_theta_sim[t,j] = np.mean(theta_sim_matrix[1][:,t,j] - theta_sim_matrix[0][:,t,j],axis=0)

np.mean(ate_theta_sim_sd,axis=1)
np.mean(ate_theta_sim,axis=1)



#Computing contribution to ATE theta by age [young,old,overall]
ate_cont_theta  = np.zeros((nperiods-1,M))
ate_cont_lt  = np.zeros((nperiods-1,M))
ate_cont_cc  = np.zeros((nperiods-1,M))
ate_cont_ct  = np.zeros((nperiods-1,M))

#the sample
boo_y = agech[:,2] <= 6

for periodt in range(nperiods-1):									

	for j in range(M):
		#theta0
		theta0 = []
		theta_00 = []
		theta_01 = []
		theta_00.append(choices_c['Choice_' + str(0)]['theta_matrix_a'][:,periodt,j])
		theta_00.append(choices_c['Choice_' + str(0)]['theta_matrix_b'][:,periodt,j])
		theta_01.append(choices_c['Choice_' + str(1)]['theta_matrix_a'][:,periodt,j])
		theta_01.append(choices_c['Choice_' + str(1)]['theta_matrix_b'][:,periodt,j])
		theta0.append(theta_00)
		theta0.append(theta_01)

		#the theta contribution
		ltheta_th1 = models[1].thetat(periodt,theta0[1],
			h_sim_matrix[0][:,periodt,j],cc_sim_matrix_a[0][:,periodt,j],
			cc_sim_matrix_b[0][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])
		ltheta_th0 = models[0].thetat(periodt,theta0[0],
			h_sim_matrix[0][:,periodt,j],cc_sim_matrix_a[0][:,periodt,j],
			cc_sim_matrix_b[0][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])

		ltheta_th1_aux = np.concatenate((ltheta_th1[0][d_childa[:,0]==1],
			ltheta_th1[1][d_childb[:,0]==1]),axis=0)

		ltheta_th0_aux = np.concatenate((ltheta_th0[0][d_childa[:,0]==1],
			ltheta_th0[1][d_childb[:,0]==1]),axis=0)

		ate_cont_theta[periodt,j] = np.mean(np.log(ltheta_th1_aux[boo_y]) - np.log(ltheta_th0_aux[boo_y]))/sd_matrix[periodt,j]
		

		#The leisure contribution
		ltheta_th1 = models[1].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[1][:,periodt,j],cc_sim_matrix_a[0][:,periodt,j],
			cc_sim_matrix_b[0][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])
		ltheta_th0 = models[0].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[0][:,periodt,j],cc_sim_matrix_a[0][:,periodt,j],
			cc_sim_matrix_b[0][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])
		
		ltheta_th1_aux = np.concatenate((ltheta_th1[0][d_childa[:,0]==1],
			ltheta_th1[1][d_childb[:,0]==1]),axis=0)

		ltheta_th0_aux = np.concatenate((ltheta_th0[0][d_childa[:,0]==1],
			ltheta_th0[1][d_childb[:,0]==1]),axis=0)


		ate_cont_lt[periodt,j] = np.mean(np.log(ltheta_th1_aux[boo_y]) - np.log(ltheta_th0_aux[boo_y]))/sd_matrix[periodt,j]
		


		
		#The CC contribution
		ltheta_th1 = models[1].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[1][:,periodt,j],cc_sim_matrix_a[1][:,periodt,j],
			cc_sim_matrix_b[1][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])
		ltheta_th0 = models[0].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[1][:,periodt,j],cc_sim_matrix_a[0][:,periodt,j],
			cc_sim_matrix_b[0][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])
		
		ltheta_th1_aux = np.concatenate((ltheta_th1[0][d_childa[:,0]==1],
			ltheta_th1[1][d_childb[:,0]==1]),axis=0)

		ltheta_th0_aux = np.concatenate((ltheta_th0[0][d_childa[:,0]==1],
			ltheta_th0[1][d_childb[:,0]==1]),axis=0)

		ate_cont_cc[periodt,j] = np.mean(np.log(ltheta_th1_aux[boo_y]) - np.log(ltheta_th0_aux[boo_y]))/sd_matrix[periodt,j]
		

	
		#The consumption contribution
		ltheta_th1 = models[1].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[1][:,periodt,j],cc_sim_matrix_a[1][:,periodt,j],
			cc_sim_matrix_b[1][:,periodt,j],
			ct_sim_matrix[1][:,periodt,j])
		ltheta_th0 = models[0].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[1][:,periodt,j],cc_sim_matrix_a[1][:,periodt,j],
			cc_sim_matrix_b[1][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])

		ltheta_th1_aux = np.concatenate((ltheta_th1[0][d_childa[:,0]==1],
			ltheta_th1[1][d_childb[:,0]==1]),axis=0)

		ltheta_th0_aux = np.concatenate((ltheta_th0[0][d_childa[:,0]==1],
			ltheta_th0[1][d_childb[:,0]==1]),axis=0)

		ate_cont_ct[periodt,j] = np.mean(np.log(ltheta_th1_aux[boo_y]) - np.log(ltheta_th0_aux[boo_y]))/sd_matrix[periodt,j]
		
