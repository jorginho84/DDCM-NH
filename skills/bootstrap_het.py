"""
This file tests mean equality between treatment and control groups across sub-samples using
bootstrap.

It uses previous estimates of cutoffs


execfile('bootstrap.py')

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
import factor_het as factor


#################################################################################
#################################################################################
#Collecting data


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
	emp_baseline.append(data[k][ ['emp_baseline'] ].values)
	d_young.append(data[k][ ['d_young'] ].values)


#############################################################################
#############################################################################
#The initial parameters for estimation

betas_init = []
for k in [2,5,8]:
	betas_init.append(np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Skills/factor_betas_y'+str(k) +'.npy'))


#the initial values [2,5,8] years after RA
lambdas = []
kappas = []
p_0 = []
mu_0 = []
sig_theta_0 = []
p_1 = []
mu_1 = []
sig_theta_1 = []


for k in range(3):
	lambdas.append(betas_init[k][0:(n_m[k]-1)].reshape((n_m[k]-1,1)) )#factor loadings
	kappas_aux=np.zeros((n_r-1,n_m[k])) #4 cutoffs x # measures

	ind  = n_m[k]-1

	for v in range(n_m[k]):#the measure loop
		kappas_aux[:,v]=betas_init[k][ind:ind+(n_r-1)]#add 4 cutoffs
		ind = ind + (n_r-1)
	kappas.append(kappas_aux)


#These are parameters of the control group
	p_0.append(np.array([[np.exp(betas_init[k][ind])/(1+np.exp(betas_init[k][ind]))]]) )#to ensure 0<p<1
	mu_0.append(np.array([[betas_init[k][ind+1]]]))

	ind = ind +1
	sig_theta_0.append(np.exp(betas_init[k][ind:ind+2]).reshape((2,1)))

	#These are parameters of the treatment group
	p_1.append(np.array([[np.exp(betas_init[k][ind])/(1+np.exp(betas_init[k][ind]))]]) )#to ensure 0<p<1
	mu_1.append(np.array([[betas_init[k][ind+1]],[0.7]]))

	ind = ind +1
	sig_theta_1.append(np.exp(betas_init[k][ind:ind+2]).reshape((2,1)))



#how many samples
num_samples=2
np.random.seed(2)

##CHOSE THE SAMPLE##
boo_all = []
boo_unemp = []
boo_emp = []
boo_young = []
boo_old = []

for k in range(3):
	boo_all.append(np.ones((n[k],),dtype=bool))
	boo_unemp.append(emp_baseline[k][:,0]==0)
	boo_emp.append(emp_baseline[k][:,0]==1)
	boo_young.append(d_young[k][:,0]==1)
	boo_old.append(d_young[k][:,0]==1)

#obtaining 3 different resamples (not block-bootstrap since I have diff Ns)
idx = []
for k in range(3):
	idx.append(np.random.randint(0, n[k], (num_samples,n[k])))

#Bootstrap samples (only in measure (y) and d_RA (x))
M_big = []
dra_big = []
for k in range(3):
	M_big.append(M[k][idx[k],:])
	dra_big.append(d_ra[k][idx[k],:])

#Sub-sample analysis

list_sample = [boo_unemp,boo_emp,boo_young,boo_old]
list_sample_label = ['Unemployed at baseline','Employed at baseline','Young','Old']


def gen_est(j):

	#by list_sample and then by year in each sample
	mu_list = []

	for ll in range(len(list_sample)):#the sample list

		mus = []
		for k in range(3): #the year loop
			nsample = M_big[k][j,list_sample[ll][k],:].shape[0]
			output_ins = factor.Factor(nsample,n_m[k],n_r,M_big[k][j,list_sample[ll][k],:],
				dra_big[k][j,list_sample[ll][k],:],lambdas[k],kappas[k],p_0[k],mu_0[k],
				sig_theta_0[k],	p_1[k],mu_1[k],sig_theta_1[k])
			
			output=output_ins.optimizer()
			betas_opt = output.x

			#recovering parameters
			lambda_aux=betas_opt[0:(n_m[k]-1)].reshape((n_m[k]-1,1)) #factor loadings
			kappa_aux=np.zeros((n_r-1,n_m[k])) #4 cutoffs x # measures

			ind  = n_m[k]-1

			for v in range(n_m[k]):#the measure loop
				kappa_aux[:,v]=betas_opt[ind:ind+(n_r-1)]#add 4 cutoffs
				ind = ind + (n_r-1)


			#These are parameters of the control group
			p_0_aux=betas_opt[ind]
			p_0_aux=np.array([[np.exp(p_0_aux)/(1+np.exp(p_0_aux))]]) #to ensure 0<p<1

			ind = ind + 1
			mu_0_aux=np.array([[betas_opt[ind]]])

			ind = ind +1
			sig_theta_0_aux=np.exp(betas_opt[ind:ind+2]).reshape((2,1))

			#These are parameters of the treatment group
			ind = ind +2
			p_1_aux=betas_opt[ind]
			p_1_aux=np.array([[np.exp(p_1_aux)/(1+np.exp(p_1_aux))]]) #to ensure 0<p<1
			
			ind = ind + 1
			mu_1_aux=np.array([[betas_opt[ind]],[betas_opt[ind+1]]])

			ind = ind +2
			sig_theta_1_aux=np.exp(betas_opt[ind:ind+2]).reshape((2,1))

			#Producing mean of Theta
			mus.append(p_1_aux[0,0]*mu_1_aux[0,0] + (1-p_1_aux[0,0])*mu_1_aux[1,0])

	return mus
	

#Obtaining bootstrap

for k in range(1):
	mus = gen_est(k)
#pool = ProcessPool(nodes=2)
#mu_t_data = pool.map(gen_est,range(num_samples))

mus = np.zeros((3,num_samples))

for k in range(3): #year loop
	mus[k,:] = np.array(mu_t_data[k])

#A t-test
np.mean(mus[0])/np.std(mus[0])

pval = (1-norm.cdf(np.mean(mus[0])/np.std(mus[0])))




