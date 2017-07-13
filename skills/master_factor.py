"""
This file estimates a factor model from ordered measures

execfile('master_factor.py')
"""
from __future__ import division #omit for python 3.x
import numpy as np
import pandas as pd
from numba import jit
import sys, os
from scipy import stats
from scipy.optimize import minimize
from scipy.optimize import fmin_bfgs
from scipy.stats import norm
from datetime import datetime
from pathos.multiprocessing import ProcessPool
sys.path.append("/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/skills")
import factor



#############################################################################
#############################################################################
#The data

#Measures data
data = []
for k in [2,5,8]:
	data.append( pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Skills/data_measures_y'+str(k)+ '.csv'))

#the list of measures
M = []
M.append( data[0][ ['tq17a', 'tq17b', 'tq17c', 'tq17d', 'tq17e', 'tq17f', 'tq17g', 
'tq17h', 'tq17i', 'tq17j']   ].values)

M.append( data[1][ ['t2q17a', 't2q17b', 't2q17c', 't2q17d',
 't2q17e', 't2q17f', 't2q17g', 't2q17h', 't2q17i', 't2q17j']   ].values)

M.append( data[2][ ['etsq13a', 'etsq13b', 'etsq13c', 'etsq13d', 'etsq13e',
 'etsq13f', 'etsq13g', 'etsq13h', 'etsq13i', 'etsq13j']   ].values)

#the list of p_assign, sample sizes, and number of measures
d_ra =[]
n= []
n_m = []
n_r = 5
emp_baseline = []
d_young = []


for k in range(3):
	d_ra.append(data[k][ ['d_RA']   ].values)
	n.append( M[k].shape[0])
	n_m.append(M[k].shape[1])

#############################################################################
#############################################################################
#The initial parameters for estimation

betas_init=np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Skills/factor_betas_v1.npy')

#the initial values [2,5,8] years after RA
lambda_opt = []
kappa_opt = []
p_0 = []
mu_0 = []
sig_theta_0 = []
p_1 = []
mu_1 = []
sig_theta_1 = []

for k in range(3):
	lambda_opt.append(betas_init[0:(n_m[k]-1)].reshape((n_m[k]-1,1))) #factor loadings
	kappa_opt_aux=np.zeros((n_r-1,n_m[k])) #4 cutoffs x # measures

	ind  = n_m[k]-1

	for v in range(n_m[k]):#the measure loop
		kappa_opt_aux[:,v]=betas_init[ind:ind+(n_r-1)]#add 4 cutoffs
		ind = ind + (n_r-1)
	kappa_opt.append(kappa_opt_aux)


	#These are parameters of the control group
	
	p_0.append(np.array([[np.exp(betas_init[ind])/(1+np.exp(betas_init[ind]))]]) )#to ensure 0<p<1
	mu_0.append(np.array([[betas_init[ind+1]]]))
	sig_theta_0.append(np.exp(betas_init[ind+1:ind+3]).reshape((2,1)))

	#These are parameters of the treatment group
	p_1.append(np.array([[np.exp(betas_init[ind])/(1+np.exp(betas_init[ind]))]]) )#to ensure 0<p<1
	mu_1.append(np.array([[betas_init[ind+1]],[0.7]]))
	sig_theta_1.append(np.exp(betas_init[ind+1:ind+3]).reshape((2,1)))

#############################################################################
#############################################################################
#Estimation

def gen_est(k):

	output_ins = factor.Factor(n[k],n_m[k],n_r,M[k],d_ra[k],lambda_opt[k],
		kappa_opt[k],p_0[k],mu_0[k],sig_theta_0[k],
		p_1[k],mu_1[k],sig_theta_1[k])
	output=output_ins.optimizer()
	return output.x

#Estimation (3 years in parallel)
print ''
print 'Start optimizer'
start=datetime.now()
pool = ProcessPool(nodes=3)
betas = pool.map(gen_est,range(3))

#stop the clock
elapsed=datetime.now()-start
print 'Estimation done in', elapsed.total_seconds()

    
np.save('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Skills/factor_betas_y2.npy',betas[0])
np.save('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Skills/factor_betas_y5.npy',betas[1])
np.save('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Skills/factor_betas_y8.npy',betas[2])

