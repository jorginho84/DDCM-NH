"""
execfile('master_iden.py')

This file computes the objective function across different parameters values
around the optimum.


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
from pathos.multiprocessing import ProcessPool
from scipy import interpolate
import matplotlib
matplotlib.use('Agg') # Force matplotlib to not use any Xwindows backend.
import matplotlib.pyplot as plt
#sys.path.append("C:\\Users\\Jorge\\Dropbox\\Chicago\\Research\\Human capital and the household\]codes\\model")
sys.path.append("/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample")
import utility as util
import gridemax
import time
import int_linear
import emax as emax
import simdata as simdata
sys.path.append("/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/estimation")
import estimate as estimate

np.random.seed(1)

execfile('/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/checks/identification_check/load_param.py')

###Auxiliary estimates### 
moments_vector=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/moments_vector.csv').values

#This is the var cov matrix of aux estimates
var_cov=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/var_cov.csv').values

#The W matrix in Wald metric
#Using diagonal of Var-Cov matrix of simulated moments
w_matrix  = np.zeros((var_cov.shape[0],var_cov.shape[0]))
for i in range(var_cov.shape[0]):
	w_matrix[i,i] = var_cov[i,i]


#Creating a grid for the emax computation
dict_grid=gridemax.grid()

#How many hours is part- and full-time work
hours_p=15
hours_f=40

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

#The model (utility instance)
hours = np.zeros(N)
childcare  = np.zeros(N)

model  = util.Utility(param0,N,x_w,x_m,x_k,passign,
	nkids0,married0,hours,childcare,agech0,hours_p,hours_f,wr,cs,ws)

#The instance for computing samples
output_ins=estimate.Estimate(param0,x_w,x_m,x_k,x_wmk,passign,agech0,nkids0,
	married0,D,dict_grid,M,N,moments_vector,w_matrix,hours_p,hours_f,
	wr,cs,ws)

def sym(a):
	return ((1/(1+np.exp(-a))) - 0.5)*2



#########################################################
####ETA###
#execfile('/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/checks/identification_check/eta.py')


#########################################################
####Part-time work###
#execfile('/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/checks/identification_check/alphap.py')

#########################################################
####Full-time work###
#execfile('/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/checks/identification_check/alphaf.py')


#########################################################
####\gamma_1###
#execfile('/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/checks/identification_check/gamma1.py')

#########################################################
####\gamma_2 (young)###
#execfile('/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/checks/identification_check/gamma2_young.py')

#########################################################
####\gamma_3###
#execfile('/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/checks/identification_check/gamma3.py')


#########################################################
####\tfp###
#execfile('/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/checks/identification_check/tfp.py')


#########################################################
####constant^2_wage###
#execfile('/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/checks/identification_check/constant_wage.py')


#########################################################
####sigma^2_wage###
#execfile('/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/checks/identification_check/sigma2_wage.py')


#########################################################
####kappas

#SSRS, t=2, kappa1
#execfile('/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/checks/identification_check/kappa_1_t2.py')


#def sample_graph(j):
#	execfile(j)
#	return 1

#sys.path.append("/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/checks/identification_check")
#pool = ProcessPool(nodes=3)	
#dics = pool.map(sample_graph,['kappa_t2_m1_k2.py','kappa_t2_m2_k3.py', 'kappa_t2_m2_k3.py'])