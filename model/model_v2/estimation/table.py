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
betas_nelder=np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/betas_modelv7_v2_e3_d100.npy')
var_cov=np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/estimation/ses_modelv7_v2_e3_3pc_d100.npy')
se_vector  = np.sqrt(np.diagonal(var_cov))

#Utility function
eta_opt=betas_nelder[0]
alphap_opt=betas_nelder[1]
alphaf_opt=betas_nelder[2]
alpha_cc_opt=betas_nelder[3]

sigma_eta_opt=se_vector[0]
sigma_alphap_opt=se_vector[1]
sigma_alphaf_opt=se_vector[2]
sigma_alpha_cc_opt=se_vector[3]

#wage process
wagep_betas=np.array([betas_nelder[4],betas_nelder[5],betas_nelder[6],
	betas_nelder[7],betas_nelder[8],betas_nelder[9]]).reshape((6,1))

sigma_wagep_betas=np.array([se_vector[4],se_vector[5],se_vector[6],se_vector[7],
	se_vector[8],se_vector[9]]).reshape((6,1))


#Production function [young[cc0,cc1],old]
gamma1=[betas_nelder[10],betas_nelder[12]]
gamma2=[betas_nelder[11],betas_nelder[13]]
tfp=betas_nelder[14]

sigma_gamma1=[se_vector[10],se_vector[12]]
sigma_gamma2=[se_vector[11],se_vector[13]]
sigma_tfp=se_vector[14]

#Measurement system: three measures for t=2, one for t=5
kappas=[[betas_nelder[15],betas_nelder[16],betas_nelder[17],betas_nelder[18]],
[betas_nelder[19],betas_nelder[20],betas_nelder[21],betas_nelder[22]]]

sigma_kappas=[[se_vector[15],se_vector[16],se_vector[17],se_vector[18]],
[se_vector[19],se_vector[20],se_vector[21],se_vector[22]]]

#First measure is normalized. starting arbitrary values
lambdas=[1,1]



###########.TEX table##################

utility_list_beta = [alphap_opt,alphaf_opt,alpha_cc_opt,eta_opt]
utility_list_se = [sigma_alphap_opt,sigma_alphaf_opt,sigma_alpha_cc_opt,sigma_eta_opt]
utility_names = [r'Preference for part-time work ($\alpha^p$)', 
r'Preference for full-time work ($\alpha^f$)',r'Preference for child care ($\alpha^c$)'
,r'Preference for human capital ($\eta$)']

wage_list_beta = [wagep_betas[0,0],wagep_betas[1,0],wagep_betas[2,0],wagep_betas[3,0],
wagep_betas[4,0],wagep_betas[5,0]]
wage_list_se = [sigma_wagep_betas[0,0],sigma_wagep_betas[1,0],
sigma_wagep_betas[2,0],sigma_wagep_betas[3,0],sigma_wagep_betas[4,0],sigma_wagep_betas[5,0]]
wage_names = ['Age', r'Age$^2$', 'High school', 'Constant', r'$\log(t)$' ,'Variance of error term']

prody_list_beta = [gamma1[0],gamma2[0],tfp]
prody_list_se  = [sigma_gamma1[0],sigma_gamma2[0],sigma_tfp]
prody_names = [r'Lagged human capital ($\gamma_1^y$)', r'Consumption ($\gamma_2^y$)',
r'TFP ($\mu$)']

prodo_list_beta = [gamma1[1],gamma2[1]]
prodo_list_se  = [sigma_gamma1[1],sigma_gamma2[1]]
prodo_names = [r'Lagged human capital ($\gamma_1^0$)', r'Consumption ($\gamma_2^0$)']

ssrs2_list_beta = kappas[0]
ssrs2_list_se = sigma_kappas[0]
ssrs_names = [r'$\kappa_1$',r'$\kappa_2$',r'$\kappa_3$',r'$\kappa_4$']

ssrs5_list_beta = kappas[1]
ssrs5_list_se = sigma_kappas[1]

with open('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/estimation/estimates.tex','w') as f:
	f.write(r'\begin{tabular}{lcccc}'+'\n')
	f.write(r'\hline' + '\n')
	f.write(r'\textbf{Parameter} &  & \textbf{Estimate} & & \textbf{S.E.} \bigstrut\\' + '\n')
	f.write(r'\cline{1-1}\cline{3-5}' + '\n')
	f.write(r'\emph{A. Utility function} &       &       &       &  \\' + '\n')
	for j in range(len(utility_list_beta)):
		f.write(utility_names[j]+r' &  &  '+ '{:04.3f}'.format(utility_list_beta[j]) +
			r' &  & '+ '{:04.3f}'.format(utility_list_se[j])+r' \\' + '\n')

	f.write(r' &       &       &       &  \\' + '\n')
	f.write(r'\emph{B. Wage offer} &       &       &       &  \\' + '\n')
	for j in range(len(wage_list_beta)):
		f.write(wage_names[j]+r' &  &  '+ '{:04.3f}'.format(wage_list_beta[j]) +
			r' &  & '+ '{:04.3f}'.format(wage_list_se[j])+r' \\' + '\n')

	f.write(r' &       &       &       &  \\' + '\n')
	f.write(r'\emph{C. Production function: young} &       &       &       &  \\' + '\n')
	for j in range(len(prody_list_beta)):
		f.write(prody_names[j]+r' &  &  '+ '{:04.3f}'.format(prody_list_beta[j]) +
			r' &  & '+ '{:04.3f}'.format(prody_list_se[j])+r' \\' + '\n')

	f.write(r' &       &       &       &  \\' + '\n')
	f.write(r'\emph{D. Production function: old} &       &       &       &  \\' + '\n')
	for j in range(len(prodo_list_beta)):
		f.write(prodo_names[j]+r' &  &  '+ '{:04.3f}'.format(prodo_list_beta[j]) +
			r' &  & '+ '{:04.3f}'.format(prodo_list_se[j])+r' \\' + '\n')

	f.write(r' &       &       &       &  \\' + '\n')
	f.write(r'\emph{E. SSRS ($t=2$)} &       &       &       &  \\' + '\n')
	for j in range(len(ssrs2_list_beta)):
		f.write(ssrs_names[j]+r' &  &  '+ '{:04.3f}'.format(ssrs2_list_beta[j]) +
			r' &  & '+ '{:04.3f}'.format(ssrs2_list_se[j])+r' \\' + '\n')

	f.write(r' &       &       &       &  \\' + '\n')
	f.write(r'\emph{F. SSRS ($t=5$)} &       &       &       &  \\' + '\n')
	for j in range(len(ssrs5_list_beta)):
		f.write(ssrs_names[j]+r' &  &  '+ '{:04.3f}'.format(ssrs5_list_beta[j]) +
			r' &  & '+ '{:04.3f}'.format(ssrs5_list_se[j])+r' \\' + '\n')

	f.write(r'\hline'+'\n')
	f.write(r'\end{tabular}' + '\n')
	f.close()

