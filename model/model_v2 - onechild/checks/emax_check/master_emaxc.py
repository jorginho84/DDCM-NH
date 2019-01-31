"""
exec(open("/home/jrodriguez/NH_HC/codes/model/checks/emax_check/master_emaxc.py").read())

This file compares the interpolated with true emax values.
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
sys.path.append("/home/jrodriguez/NH_HC/codes/model/checks/emax_check")
import simdata_v2 as simdata
import emax_v2 as emax

np.random.seed(1)

betas_nelder=np.load('/home/jrodriguez/NH_HC/results/Model/estimation/betas_modelv23.npy')

#Number of periods where all children are less than or equal to 18
nperiods = 8

#Utility function
eta = betas_nelder[0]
alphap = betas_nelder[1]
alphaf = betas_nelder[2]

#wage process: female
wagep_betas = np.array([betas_nelder[3],betas_nelder[4],betas_nelder[5],
	betas_nelder[6],betas_nelder[7]]).reshape((5,1))

#income process: male
income_male_betas = np.array([6.8,.33,.32]).reshape((3,1))

#Production function
gamma1 = betas_nelder[8]
gamma2 = betas_nelder[9]
gamma3 = betas_nelder[10]
tfp = betas_nelder[11]
gamma_spouse = .05
sigma2theta = 1
varphi = 0.5

kappas=[[betas_nelder[12],betas_nelder[13],betas_nelder[14],betas_nelder[15]],
[betas_nelder[16],betas_nelder[17],betas_nelder[18],betas_nelder[19]]]

#initial theta
rho_theta_epsilon = betas_nelder[20]
rho_theta_ab = 0.2


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
x_wmk=x_df[  ['age_ra','age_ra2', 'd_HS2', 'constant'] ].values

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
"""
#Assuming random start
theta0_a=np.exp(np.random.randn(N))
theta0_b=np.exp(np.random.randn(N))
epsilon0=np.random.randn(N)

#number of kids at baseline
nkids0=x_df[ ['nkids_baseline']   ].values

#marital status at baseline
married0=x_df[ ['d_marital_2']   ].values

#age of child at baseline
agech0_a=x_df[['age_t0A']].values[:,0]
agech0_b=x_df[['age_t0B']].values[:,0]
d_childb=x_df[['d_childB']].values
d_childa=x_df[['d_childA']].values
"""

#Defines the instance with parameters
param0=util.Parameters(alphap,alphaf,eta,gamma1,gamma2,gamma3,
	tfp,sigma2theta,varphi,rho_theta_epsilon,rho_theta_ab,wagep_betas,income_male_betas,
	marriagep_betas, kidsp_betas, eitc_list,
	afdc_list,snap_list,cpi,lambdas,kappas,pafdc,psnap,mup)

#For montercarlo integration
D=20

#How many hours is part- and full-time work
hours_p=15
hours_f=40

hours = np.zeros(N)
childcare = np.zeros(N)
wr,cs,ws=1,1,1

######################################################################
#Creating a grid for the emax computation
#The interpolated dataset
dict_grid=gridemax.grid()
#choices
J = 3*2*2

#New data: new set of initial state variables
passign = dict_grid['passign']
theta0_a = dict_grid['theta0_a']
theta0_b = dict_grid['theta0_b']
nkids0 = dict_grid['nkids0']
married0 = dict_grid['married0']
x_w = dict_grid['x_w']
x_m = dict_grid['x_m']
x_k = dict_grid['x_k']
x_wmk = dict_grid['x_wmk']
agech0_a = dict_grid['agech_a'][:,0]
agech0_b = dict_grid['agech_b'][:,0]
d_childa = dict_grid['d_childa']
d_childb = dict_grid['d_childb']
epsilon0 = dict_grid['epsilon_1']
		
N = nkids0.shape[0]

#This is an arbitrary initialization of Utility class
model = util.Utility(param0,N,x_w,x_m,x_k,passign,nkids0,married0,hours,childcare,childcare,
	agech0_a,agech0_b,d_childa,d_childb,hours_p,hours_f,wr,cs,ws)

#The betas of original and recovering true values
np.random.seed(2)
emax_function_in=emax.Emaxt(param0,D,dict_grid,hours_p,hours_f,wr,cs,ws,model)
emax_dic_true = emax_function_in.recursive()
emax_t1_true = emax_dic_true[8][1]['emax1'] #true emax values.

#this is the true Emaxs values
emax_true_values = np.zeros((N,10,nperiods,J))
for periodt in range(0,nperiods):
	for j in range(J):
		for age in range(1,11):
			emax_true_values[:,10-age,periodt,j] = emax_dic_true[10-age][1]['emax'+str(periodt+1)][:,j]



#arbitrary state variables to interpolate
data_int_ex=np.concatenate(( np.reshape(np.log(theta0_a),(N,1)),
	np.reshape(np.log(theta0_b),(N,1)),
	nkids0,married0,
	np.reshape(np.square(np.log(theta0_a)),(N,1)),
	np.reshape(np.square(np.log(theta0_b)),(N,1)),
	passign,np.reshape(epsilon0,(N,1)),
	np.reshape(np.square(epsilon0),(N,1)),
	x_wmk), axis=1)

#take emax of the youngest possible child
#this is the interpolated emax values
emax_t1_int = np.zeros((N,J))
for j in range(J):
	emax_betas  = emax_dic_true[8][0]['emax1'][j].copy()
	emax_ins = int_linear.Int_linear() #arbitrary initializacion
	emax_t1_int[:,j] = emax_ins.int_values(data_int_ex,emax_betas)
	


#The true emax values (these are the value used for computing interpolation )
#true_grid = { 'passign': dict_grid['passign'],'theta0': dict_grid['theta0'],
#	 'nkids0': dict_grid['nkids0'] , 'married0': dict_grid['married0'], 
#		'x_w': dict_grid['x_w'], 'x_m':dict_grid['x_m'], 
#		'x_k': dict_grid['x_k'], 'x_wmk': dict_grid['x_wmk'], 
#		'agech':dict_grid['agech'], 
#		'epsilon_1': dict_grid['epsilon_1'] }

#emax_function_in_true = emax.Emaxt(param0,D,true_grid,hours_p,hours_f,wr,cs,ws,model)
#emax_dic_true = emax_function_in_true.recursive()
#emax_t1_true = emax_dic_true[9][1]['emax1'] #(ngrid,n_choices)


######################################################################
#Analysis
print ('average of emax interpolated', np.mean(emax_t1_int,axis=0))
print ('average of emax true', np.mean(emax_t1_true,axis=0))


#Comparing 1-1
print ('')
print ('This is RMSE (in true SD units)', (np.sum((emax_t1_int - emax_t1_true)**2,axis=0)/N )**.5/ np.std(emax_t1_true,axis=0))
print ('')
#######################################################################

#Choices based on True EMAX
np.random.seed(1)
sim_ins_true=simdata.SimData(N,param0,emax_dic_true,x_w,x_m,x_k,x_wmk,passign,nkids0,married0,
	agech0_a,agech0_b,d_childa,d_childb,hours_p,hours_f,wr,cs,ws,model,1,emax_true_values)
data_dic_true=sim_ins_true.fake_data(8) #9 periods (t=0 to t=8)
hours_t=data_dic_true['Hours']
unemp_t=hours_t==0
part_t=hours_t==hours_p
full_t=hours_t==hours_f



#Choices based on Interpolated EMAX
np.random.seed(1)
sim_ins=simdata.SimData(N,param0,emax_dic_true,x_w,x_m,x_k,x_wmk,passign,nkids0,married0,
	agech0_a,agech0_b,d_childa,d_childb,hours_p,hours_f,wr,cs,ws,model,0,emax_true_values)
data_dic_int=sim_ins.fake_data(8) #9 periods (t=0 to t=8)



hours_t=data_dic_int['Hours']
unemp_t=hours_t==0
part_t=hours_t==hours_p
full_t=hours_t==hours_f

print ('')
print ('This is pr(unemp) true', np.mean(unemp_t,axis=0))
print ('This is pr(part) true', np.mean(full_t,axis=0))
print ('This is pr(full) true',np.mean(part_t,axis=0))
print ('')
print ('This is pr(unemp) interpolated', np.mean(unemp_t,axis=0))
print ('This is pr(part) interpolated', np.mean(full_t,axis=0))
print ('This is pr(full) interpolated',np.mean(part_t,axis=0))
print ('')