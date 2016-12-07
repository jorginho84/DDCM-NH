"""
execfile('master_sim.py')

(1) Defines a set of parameters and X's
(2) Defines a grid of state variables
(3) Obtains a dictionary with the set of emax functions
(4) Given (3), simulates fake data

The emax functions are interpolating instances (see int_linear.py for 
	more information)

(1). The parameters and X's are related to the specificaciones of the regressions
on marriage, number of kids, and the wage process. Make sure to match those in
"marriage_process/marriage_process.do";"kids_process/kids_process.do"; and
"wage_process/wage.do".

(2) and (3). Uses gridemax.py to construct the grid. Use this file to modify 
the size of the grid. Importantly, the variables in the grid must coincide
to those in (1). Then, it uses emax.py and int_linear.py to compute emax functions
that depends on the grid values. It returns a dictionary of emax functions, which
are instances of the class defined in int_linear

(4) The emax dictionary is an input in the class found in simdata.py.

pip2.7 install --user line_profiler


"""
from __future__ import division #omit for python 3.x
import numpy as np
import pandas as pd
import pickle
import itertools
import sys, os
from scipy import stats
from scipy import interpolate
import matplotlib.pyplot as plt
import time
#sys.path.append("C:\\Users\\Jorge\\Dropbox\\Chicago\\Research\\Human capital and the household\]codes\\model")
sys.path.append("/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample")
import utility as util
import gridemax
import int_linear
import emax as emax
import simdata as simdata

np.random.seed(100);
#Sample size
#N=315

betas_nelder=np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/betas_modelv2_nelder_v12.npy')

#Utility function
eta=betas_nelder[0]
alphap=betas_nelder[1]
alphaf=betas_nelder[2]

#wage process
wagep_betas=np.array([betas_nelder[3],betas_nelder[4],betas_nelder[5],
	betas_nelder[6],betas_nelder[7]]).reshape((5,1))

#Production function [young[cc0,cc1],old]
gamma1=[[betas_nelder[8],betas_nelder[10]],betas_nelder[12]]
gamma2=[[betas_nelder[9],betas_nelder[11]],betas_nelder[13]]
sigmatheta=0

#Measurement system: three measures for t=2, one for t=5
kappas=[[[betas_nelder[14],betas_nelder[15],betas_nelder[16],betas_nelder[17]]
,[betas_nelder[18],betas_nelder[19],betas_nelder[20],betas_nelder[21]],
[betas_nelder[22],betas_nelder[23],betas_nelder[24],betas_nelder[25]]],
[[betas_nelder[26],betas_nelder[27],betas_nelder[28],betas_nelder[29]]]]
#First measure is normalized. starting arbitrary values
lambdas=[[1,betas_nelder[30],betas_nelder[31]],[betas_nelder[32]]]



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
#Parameters: wage function.the last one is sigma. 
#see wage_process.do to see the order of the variables.
x_w=x_df[ ['age_ra', 'd_HS2', 'constant' ] ].values

#Data for marriage process
#Parameters: marriage. Last one is the constant
x_m=x_df[ ['age_ra', 'constant']   ].values
marriagep_betas=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/marriage_process/betas_m_v2.csv').values

#Data for fertility process (only at X0)
#Parameters: kids. last one is the constant
x_k=x_df[ ['age_ra', 'constant']   ].values
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
param=util.Parameters(alphap, alphaf, eta, gamma1, gamma2,sigmatheta,
	wagep_betas, marriagep_betas, kidsp_betas, eitc_list,afdc_list,snap_list,
	cpi,q,scalew,shapew,lambdas,kappas,pafdc,psnap)


#Creating a grid for the emax computation
dict_grid=gridemax.grid()

##############Computing EmaxT#####################
print ''
print ''
print 'Getting a dictionary of emax'
start_time = time.time()
print ''
print ''


D=50
emax_function_in=emax.Emaxt(param,D,dict_grid)
emax_dic=emax_function_in.recursive(8) #8 emax (t=1 to t=8)


time_emax=time.time() - start_time
print ''
print ''
print 'Done with procedure in:'
print("--- %s seconds ---" % (time_emax))
print ''
print ''


#########Simulating data###############
print ''
print ''
print 'Simulating fake data'
start_time = time.time()
print ''
print ''


sim_ins=simdata.SimData(N,param,emax_dic,x_w,x_m,x_k,x_wmk,passign,theta0,\
	nkids0,married0,agech0)
data_dic=sim_ins.fake_data(9) #9 periods (t=0 to t=8)


time_sim=time.time() - start_time
print ''
print ''
print 'Done with procedure in:'
print("--- %s seconds ---" % (time_sim))
print ''
print ''


ct=data_dic['Consumption']
income=data_dic['Income']
theta_t=data_dic['Theta']
cc_t=data_dic['Childcare']
hours_t=data_dic['Hours']
wage_t=data_dic['Wage']
ssrs_t2=data_dic['SSRS_t2']
ssrs_t5=data_dic['SSRS_t5']

#log theta in SD units
ltheta=np.log(theta_t)
np.mean(ltheta,axis=0)

#Impact of NH on logtheta (SD units) in time
ate_theta=np.mean(ltheta[passign[:,0]==1,:],axis=0) - np.mean(ltheta[passign[:,0]==0,:],axis=0)

#Impact on income
np.mean(ct,axis=0)
np.mean(income,axis=0)
ate_income=np.mean(income[passign[:,0]==1,:],axis=0) - np.mean(income[passign[:,0]==0,:],axis=0)
ate_ct=np.mean(ct[passign[:,0]==1,:],axis=0) - np.mean(ct[passign[:,0]==0,:],axis=0)

#Children's ranking
ssrs_freq_t2=np.zeros((N,3,5))
ssrs_freq_t5=np.zeros((N,5))
for j in range(1,6):
	ssrs_freq_t5[:,j-1]=ssrs_t5==j

for i in range(3):
	for j in range(1,6):
		ssrs_freq_t2[:,i,j-1]=ssrs_t2[:,i]==j


np.mean(ssrs_freq_t5,axis=0)
np.mean(ssrs_freq_t2[:,0,:],axis=0)
np.mean(ssrs_freq_t2[:,1,:],axis=0)
np.mean(ssrs_freq_t2[:,2,:],axis=0)


#Child care (inn t=0, all young)
np.mean(cc_t[agech0[:,0]<=5,:],axis=0)
ate_cc=np.mean(cc_t[(passign[:,0]==1) & (agech0[:,0]<=5),:],axis=0) - np.mean(cc_t[(passign[:,0]==0) & (agech0[:,0]<=5),:],axis=0)


#Labor supply
unemp_t=hours_t==0
part_t=hours_t==15
full_t=hours_t==30

np.mean(unemp_t,axis=0)



#ATE on employment
ate_emp=np.mean(1-unemp_t[passign[:,0]==1,:],axis=0) - np.mean(1-unemp_t[passign[:,0]==0,:],axis=0)


		
