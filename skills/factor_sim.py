"""
execfile('factor_sim.py')

This file simulates the distribution of skills of treatment and control groups
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
from scipy.stats import gaussian_kde
from datetime import datetime
import subprocess
from pathos.multiprocessing import ProcessPool
import matplotlib
matplotlib.use('Agg') # Force matplotlib to not use any Xwindows backend.
import matplotlib.pyplot as plt
sys.path.append("/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/skills")
import factor

#Measures data
data_y2 = pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Skills/data_measures_y2.csv')

M = data_y2[ ['tq17a', 'tq17b', 'tq17c', 'tq17d', 'tq17e', 'tq17f', 'tq17g', 
'tq17h', 'tq17i', 'tq17j']   ].values

d_ra = data_y2[ ['d_RA']   ].values

n = M.shape[0]
n_m = M.shape[1]
n_r = 5

#initial values
betas_init = []
for k in [2,5,8]:
	betas_init.append(np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Skills/factor_betas_y'+str(k) +'.npy'))

#saving data here
theta = []
#size of artificial sample
N = 100000

for k in range(3):
	lambda_opt=betas_init[k][0:(n_m-1)].reshape((n_m-1,1)) #factor loadings
	kappa_opt=np.zeros((n_r-1,n_m)) #4 cutoffs x # measures

	ind  = n_m-1

	for v in range(n_m):#the measure loop
		kappa_opt[:,v]=betas_init[k][ind:ind+(n_r-1)]#add 4 cutoffs
		ind = ind + (n_r-1)


	#These are parameters of the control group
	p_0=betas_init[k][ind]
	p_0=np.array([[np.exp(p_0)/(1+np.exp(p_0))]]) #to ensure 0<p<1

	ind = ind + 1 
	mu_0=np.array([[betas_init[k][ind]]])

	ind = ind +1
	sig_theta_0=np.exp(betas_init[k][ind:ind+2]).reshape((2,1))

	#These are parameters of the treatment group
	ind = ind +2
	p_1=betas_init[k][ind]
	p_1=np.array([[np.exp(p_1)/(1+np.exp(p_1))]]) #to ensure 0<p<1

	ind = ind + 1
	mu_1=np.array([[betas_init[k][ind]],[betas_init[k][ind+1]]])

	ind = ind +2
	sig_theta_1=np.exp(betas_init[k][ind:ind+2]).reshape((2,1))



	#################


	#prob of being in the treatment group
	p_ra = np.random.binomial(1,np.mean(d_ra),size=(N))

	#prob of being of distribution types
	p0 = np.random.binomial(1,p_0[0,0],size=(N))
	p1 = np.random.binomial(1,p_1[0,0],size=(N))

	#Factor:
	m0_1 = -p_0[0,0]*mu_0[0,0]/(1-p_0[0,0])

	theta_aux = (1-p_ra)*(p0*np.random.normal(mu_0[0,0],sig_theta_0[0,0]**0.5,size=(N,)) +(1-p0)*
	np.random.normal(m0_1,sig_theta_0[1,0]**0.5,size=(N,)) )
	theta.append( theta_aux  + p_ra*(p1*np.random.normal(mu_1[0,0],sig_theta_1[0,0]**0.5,size=(N,)) +(1-p1)*
		np.random.normal(mu_1[1,0],sig_theta_1[1,0]**0.5,size=(N,)) ))

#Plots


#data
data_frame = pd.DataFrame({'theta_y2': theta[0],'theta_y5': theta[1], 'theta_y8': theta[2],
 'd_RA': p_ra})
data_frame.to_stata('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Skills/theta_sample.dta')


#plotting in stata
dofile = "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/skills/kden.do"
cmd = ["stata-mp", "do", dofile]
subprocess.call(cmd)

