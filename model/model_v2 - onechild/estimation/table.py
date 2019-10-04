"""
exec(open("/home/jrodriguez/NH_HC/codes/model_v2/estimation/table.py").read())


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
betas_nelder=np.load('/home/jrodriguez/NH_HC/results/Model/estimation/betas_modelv46.npy')
var_cov=np.load('/home/jrodriguez/NH_HC/results/model_v2/estimation/sesv3_modelv46.npy')
se_vector  = np.sqrt(np.diagonal(var_cov))

#Utility function
eta = 0.35
alphap = betas_nelder[1]
alphaf = betas_nelder[2]
mu_c = -0.56


sigma_eta_opt=se_vector[0]
sigma_alphap_opt=se_vector[1]
sigma_alphaf_opt=se_vector[2]

#wage process
wagep_betas=np.array([betas_nelder[3],betas_nelder[4],betas_nelder[5],
	betas_nelder[6],betas_nelder[7]]).reshape((5,1))

sigma_wagep_betas=np.array([se_vector[3],se_vector[4],se_vector[5],
	se_vector[6],se_vector[7]]).reshape((5,1))


income_male_betas = np.array([betas_nelder[8],betas_nelder[9],
	betas_nelder[10]]).reshape((3,1))
c_emp_spouse = betas_nelder[11]


sigma_income_male_betas = np.array([se_vector[8],se_vector[9],
	se_vector[10]]).reshape((3,1))
sigma_c_emp_spouse = se_vector[11]

#Production function [young[cc0,cc1],old]
gamma1= betas_nelder[12]
gamma2= betas_nelder[13]
gamma3= betas_nelder[14]
tfp = betas_nelder[15]
sigma2theta=1

sigma_gamma1=se_vector[12]
sigma_gamma2=se_vector[13]
sigma_gamma3=se_vector[14]
sigma_tfp=se_vector[15]


kappas = [betas_nelder[16],betas_nelder[17]]

sigma_kappas = [se_vector[16],se_vector[17]]

sigma_z = [1,1]



rho_theta_epsilon = betas_nelder[18]
sigma_rho_theta_epsilon = se_vector[18]


#First measure is normalized. starting arbitrary values
lambdas=[1,1]



###########.TEX table##################

utility_list_beta = [alphap,alphaf,eta]
utility_list_se = [sigma_alphap_opt,sigma_alphaf_opt,sigma_eta_opt]
utility_names = [r'Preference for part-time work ($\alpha^p$)', 
r'Preference for full-time work ($\alpha^f$)',
r'Preference for human capital ($\eta$)']

wage_list_beta = [wagep_betas[0,0],wagep_betas[1,0],wagep_betas[2,0],
wagep_betas[3,0],wagep_betas[4,0]]
wage_list_se = [sigma_wagep_betas[0,0],sigma_wagep_betas[1,0],
sigma_wagep_betas[2,0],sigma_wagep_betas[3,0],sigma_wagep_betas[4,0]]
wage_names = ['High school dummy', 'Trend','Constant', 'Variance of error term','AR(1) error term']

swage_list_beta = [income_male_betas[0,0],income_male_betas[1,0],income_male_betas[2,0],
c_emp_spouse]
swage_list_se = [sigma_income_male_betas[0,0],sigma_income_male_betas[1,0],sigma_income_male_betas[2,0],
sigma_c_emp_spouse]
swage_names = ['High school dummy', 'Constant', 'Variance of error term','Employment probability']


prod_list_beta = [tfp,gamma1,gamma2,gamma3,rho_theta_epsilon]
prod_list_se  = [sigma_tfp,sigma_gamma1,sigma_gamma2,sigma_gamma3,sigma_rho_theta_epsilon]
prod_names = [r'Child care TFP ($\gamma_1$)', r'Lagged human capital ($\gamma_2$)', r'Consumption ($\gamma_3$)',
r'Time at home ($\gamma_4$)',  r'$Corr(\varepsilon_0^{\theta},\varepsilon_0^w)$']

ssrs_list_beta = [kappas[0],kappas[1]]
ssrs_list_se = [sigma_kappas[0],sigma_kappas[1]]

ssrs_names = [r'Intercept ($t=2$)', r'Intercept ($t=5$)']

#This is for the paper
with open('/home/jrodriguez/NH_HC/results/model_v2/estimation/estimates.tex','w') as f:
	f.write(r'\begin{tabular}{lcccc}'+'\n')
	f.write(r'\hline' + '\n')
	f.write(r'Parameter &  & Estimate & & S.E. \bigstrut\\' + '\n')
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
	f.write(r'\emph{C. Spouse income} &       &       &       &  \\' + '\n')
	for j in range(len(swage_list_beta)):
		f.write(swage_names[j]+r' &  &  '+ '{:04.3f}'.format(swage_list_beta[j]) +
			r' &  & '+ '{:04.3f}'.format(swage_list_se[j])+r' \\' + '\n')

	f.write(r' &       &       &       &  \\' + '\n')
	f.write(r'\emph{D. Production function} &       &       &       &  \\' + '\n')
	for j in range(len(prod_list_beta)):
		f.write(prod_names[j]+r' &  &  '+ '{:04.3f}'.format(prod_list_beta[j]) +
			r' &  & '+ '{:04.3f}'.format(prod_list_se[j])+r' \\' + '\n')

	f.write(r' &       &       &       &  \\' + '\n')
	f.write(r'\emph{E. SSRS)} &       &       &       &  \\' + '\n')
	
	f.write(ssrs_names[0]+r' &  &  '+ '{:04.3f}'.format(ssrs_list_beta[0]) +
		r' &  & '+ '{:04.3f}'.format(ssrs_list_se[0])+r' \\' + '\n')

	f.write(ssrs_names[1]+r' &  &  '+ '{:04.3f}'.format(ssrs_list_beta[1]) +
		r' &  & '+ '{:04.3f}'.format(ssrs_list_se[1])+r' \\' + '\n')


	f.write(r'\hline'+'\n')
	f.write(r'\end{tabular}' + '\n')
	f.close()


