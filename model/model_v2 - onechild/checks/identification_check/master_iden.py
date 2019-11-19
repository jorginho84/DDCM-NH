"""
exec(open("/home/jrodriguez/NH_HC/codes/model_v2/checks/identification_check/master_iden.py").read())

This file computes the objective function across different parameters values
around the optimum.


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
from pathos.multiprocessing import ProcessPool
from scipy import interpolate
import matplotlib
matplotlib.use('Agg') # Force matplotlib to not use any Xwindows backend.
import matplotlib.pyplot as plt
sys.path.append("/home/jrodriguez/NH_HC/codes/model_v2/simulate_sample")
import utility as util
import gridemax
import time
import int_linear
import emax as emax
import simdata as simdata
sys.path.append("/home/jrodriguez/NH_HC/codes/model_v2/estimation")
import estimate as estimate

np.random.seed(1)

#Number of periods where all children are less than or equal to 18
nperiods = 8

exec(open("/home/jrodriguez/NH_HC/codes/model_v2/checks/identification_check/load_param.py").read())


###Auxiliary estimates### 
moments_vector=pd.read_csv("/home/jrodriguez/NH_HC/results/model_v2/aux_model/moments_vector.csv").values

#This is the var cov matrix of aux estimates
var_cov = pd.read_csv("/home/jrodriguez/NH_HC/results/model_v2/aux_model/var_cov.csv").values

#The W matrix in Wald metric
#Using diagonal of Var-Cov matrix of simulated moments
w_matrix  = np.zeros((var_cov.shape[0],var_cov.shape[0]))
for i in range(var_cov.shape[0]):
	w_matrix[i,i] = var_cov[i,i]


#Creating a grid for the emax computation
dict_grid=gridemax.grid()

#How many hours is part- and full-time work
hours_p = 15
hours_f = 40

#For montercarlo integration
D = 50

#For II procedure
M = 300

#Indicate if model includes a work requirement (wr), 
#and child care subsidy (cs) and a wage subsidy (ws)
wr = 1
cs = 1
ws = 1

#The model (utility instance)
hours = np.zeros(N)
childcare  = np.zeros(N)

model  = util.Utility(param0,N,x_w,x_m,x_k,passign,nkids0,
	married0,hours,childcare,agech0,hours_p,hours_f,wr,cs,ws)

#The instance for computing samples
output_ins = estimate.Estimate(nperiods,param0,x_w,x_m,x_k,x_wmk,passign,
	agech0,nkids0,married0,D,dict_grid,M,N,moments_vector,var_cov,hours_p,hours_f,
	wr,cs,ws)

def sym(a):
	return ((1/(1+np.exp(-a))) - 0.5)*2

font_size = 20


#########################################################
#Utility function

####ETA###
exec(open("/home/jrodriguez/NH_HC/codes/model_v2/checks/identification_check/eta.py").read())

####Part-time work###
#exec(open("/home/jrodriguez/NH_HC/codes/model_v2/checks/identification_check/alphap.py").read())

####Full-time work###
#exec(open("/home/jrodriguez/NH_HC/codes/model_v2/checks/identification_check/alphaf.py").read())

#########################################################
#Wage offer

####high school###
#exec(open("/home/jrodriguez/NH_HC/codes/model_v2/checks/identification_check/highschool_wage.py").read())

####trend###
#exec(open("/home/jrodriguez/NH_HC/codes/model_v2/checks/identification_check/logt_wage.py").read())

####constant_wage###
#exec(open("/home/jrodriguez/NH_HC/codes/model_v2/checks/identification_check/constant_wage.py").read())

####sigma2###
#exec(open("/home/jrodriguez/NH_HC/codes/model_v2/checks/identification_check/sigma_wage.py").read())

####rho###
#exec(open("/home/jrodriguez/NH_HC/codes/model_v2/checks/identification_check/rho_wage.py").read())

#########################################################
#Spouse income: high school
#exec(open("/home/jrodriguez/NH_HC/codes/model_v2/checks/identification_check/highschool_spouse.py").read())

#Spouse income: constant
#exec(open("/home/jrodriguez/NH_HC/codes/model_v2/checks/identification_check/constant_spouse.py").read())

#Spouse income: sigma2
#exec(open("/home/jrodriguez/NH_HC/codes/model_v2/checks/identification_check/sigma_spouse.py").read())

#Employment spouse
#exec(open("/home/jrodriguez/NH_HC/codes/model_v2/checks/identification_check/employment_spouse.py").read())

#########################################################
#Production function



####\gamma_1###
#exec(open("/home/jrodriguez/NH_HC/codes/model_v2/checks/identification_check/gamma1.py").read())

####\gamma_2###
exec(open("/home/jrodriguez/NH_HC/codes/model_v2/checks/identification_check/gamma2.py").read())

#***
####rho0###
#exec(open("/home/jrodriguez/NH_HC/codes/model_v2/checks/identification_check/rho0.py").read())

####rho1###
#exec(open("/home/jrodriguez/NH_HC/codes/model_v2/checks/identification_check/rho0.py").read())

#***
####TFP###
#exec(open("/home/jrodriguez/NH_HC/codes/model_v2/checks/identification_check/tfp.py").read())

##Kappas##
#exec(open("/home/jrodriguez/NH_HC/codes/model_v2/checks/identification_check/kappas.py").read())


#########################################################
#Initial theta

#***
####corr_theta0###
#exec(open("/home/jrodriguez/NH_HC/codes/model_v2/checks/identification_check/corr_theta0.py").read())

