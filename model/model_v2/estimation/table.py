"""
execfile('table.py')

This file stores the estimated coefficients in an excel table.

Before running, have var-cov matrix of estimated parameters (se.py in ses folder)


"""

from __future__ import division #omit for python 3.x
import numpy as np
import pandas as pd
import itertools
import sys, os
from joblib import Parallel, delayed
from scipy import stats
from scipy import interpolate
import matplotlib
matplotlib.use('Agg') # Force matplotlib to not use any Xwindows backend.
import matplotlib.pyplot as plt
import time
import openpyxl

#Betas and var-cov matrix
betas_nelder=np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/betas_modelv3_nelder_v22_v4.npy')
var_cov=np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/estimation/ses_v12.npy')
se_vector  = np.sqrt(np.diagonal(var_cov))

#Utility function
eta_opt=betas_nelder[0]
alphap_opt=betas_nelder[1]
alphaf_opt=betas_nelder[2]

sigma_eta_opt=se_vector[0]
sigma_alphap_opt=se_vector[1]
sigma_alphaf_opt=se_vector[2]

#wage process
wagep_betas=np.array([betas_nelder[3],betas_nelder[4],betas_nelder[5],
	betas_nelder[6],betas_nelder[7]]).reshape((5,1))

sigma_wagep_betas=np.array([se_vector[3],se_vector[4],se_vector[5],
	se_vector[6],se_vector[7]]).reshape((5,1))


#Production function [young[cc0,cc1],old]
gamma1=[[betas_nelder[8],betas_nelder[10]],betas_nelder[12]]
gamma2=[[betas_nelder[9],betas_nelder[11]],betas_nelder[13]]
tfp = betas_nelder[14]

sigma_gamma1=[[se_vector[8],se_vector[10]],se_vector[12]]
sigma_gamma2=[[se_vector[9],se_vector[11]],se_vector[13]]
sigma_tfp = se_vector[14]

#Measurement system: three measures for t=2, one for t=5
kappas=[[betas_nelder[15],betas_nelder[16],betas_nelder[17],betas_nelder[18]],
[betas_nelder[19],betas_nelder[20],betas_nelder[21],betas_nelder[22]]]

sigma_kappas=[[se_vector[15],se_vector[16],se_vector[17],se_vector[18]],
[se_vector[19],se_vector[20],se_vector[21],se_vector[22]]]

#First measure is normalized. starting arbitrary values
lambdas=[1,1]




#########Opening workbook##############
wb=openpyxl.load_workbook('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/estimation/str_estimates.xlsx')
ws = wb["table_1"]

##Utility function##
list_beta = [alphap_opt, alphaf_opt, eta_opt]
list_sigma = [sigma_alphap_opt, sigma_alphaf_opt, sigma_eta_opt]

for c in range(3):
	beta_est = ws.cell('D' + str(c+5))
	sigma_est = ws.cell('F' + str(c+5))
	beta_est.value = np.float(list_beta[c])
	sigma_est.value = np.float(list_sigma[c])


#Wage process
list_beta = [wagep_betas[0,0], wagep_betas[1,0], wagep_betas[2,0],wagep_betas[3,0],wagep_betas[4,0]]
list_sigma = [sigma_wagep_betas[0,0], sigma_wagep_betas[1,0], sigma_wagep_betas[2,0],
	sigma_wagep_betas[3,0],sigma_wagep_betas[4,0]]

for c in range(5):
	beta_est = ws.cell('D' + str(c+10))
	sigma_est = ws.cell('F' + str(c+10))
	beta_est.value = np.float(list_beta[c])
	sigma_est.value = np.float(list_sigma[c])


#Prod function young cc=0
list_beta = [gamma1[0][0],gamma2[0][0]]
list_sigma = [sigma_gamma1[0][0],sigma_gamma2[0][0]]

for c in range(2):
	beta_est = ws.cell('D' + str(c+17))
	sigma_est = ws.cell('F' + str(c+17))
	beta_est.value = np.float(list_beta[c])
	sigma_est.value = np.float(list_sigma[c])

#Prod function young cc=1
list_beta = [gamma1[0][1],gamma2[0][1],tfp]
list_sigma = [sigma_gamma1[0][1],sigma_gamma2[0][1],sigma_tfp]

for c in range(3):
	beta_est = ws.cell('D' + str(c+21))
	sigma_est = ws.cell('F' + str(c+21))
	beta_est.value = np.float(list_beta[c])
	sigma_est.value = np.float(list_sigma[c])

#Prod function old
list_beta = [gamma1[1],gamma2[1]]
list_sigma = [sigma_gamma1[1],sigma_gamma2[1]]

for c in range(2):
	beta_est = ws.cell('D' + str(c+26))
	sigma_est = ws.cell('F' + str(c+26))
	beta_est.value = np.float(list_beta[c])
	sigma_est.value = np.float(list_sigma[c])

ws = wb["table_2"]

#Kappas (t=2)
list_beta = [kappas[0][0],kappas[0][1],kappas[0][2],kappas[0][3]]
list_sigma = [sigma_kappas[0][0],sigma_kappas[0][1],sigma_kappas[0][2],sigma_kappas[0][3]]

for c in range(4):
	beta_est = ws.cell('D' + str(c+5))
	sigma_est = ws.cell('F' + str(c+5))
	beta_est.value = np.float(list_beta[c])
	sigma_est.value = np.float(list_sigma[c])

#Kappas (t=5)
list_beta = [kappas[1][0],kappas[1][1],kappas[1][2],kappas[1][3]]
list_sigma = [sigma_kappas[1][0],sigma_kappas[1][1],sigma_kappas[1][2],sigma_kappas[1][3]]

for c in range(4):
	beta_est = ws.cell('D' + str(c+11))
	sigma_est = ws.cell('F' + str(c+11))
	beta_est.value = np.float(list_beta[c])
	sigma_est.value = np.float(list_sigma[c])




wb.save('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/estimation/str_estimates.xlsx')