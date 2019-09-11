"""

exec(open("/home/jrodriguez/NH_HC/codes/model_v2/experiments/EITC/eitc_exp_mech.py").read())

This file computes EITC experiments/UBI experiments

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
from joblib import Parallel, delayed
from scipy import interpolate
import matplotlib
matplotlib.use('Agg') # Force matplotlib to not use any Xwindows backend.
import matplotlib.pyplot as plt
#sys.path.append("C:\\Users\\Jorge\\Dropbox\\Chicago\\Research\\Human capital and the household\]codes\\model")
sys.path.append("/home/jrodriguez/NH_HC/codes/model_v2/simulate_sample")
import utility as util
import gridemax
import time
import int_linear
import emax as emax
import simdata as simdata
sys.path.append("/home/jrodriguez/NH_HC/codes/model_v2/estimation")
import estimate as estimate
sys.path.append("/home/jrodriguez/NH_HC/codes/model_v2/experiments/EITC")
from bset import Budget

np.random.seed(1)

betas_nelder = np.load("/home/jrodriguez/NH_HC/results/Model/estimation/betas_modelv40.npy")

#Number of periods where all children are less than or equal to 18
nperiods = 8

#Utility function
eta = betas_nelder[0]
alphap = betas_nelder[1]
alphaf = betas_nelder[2]

mu_c = -0.56

#wage process en employment processes: female
wagep_betas=np.array([betas_nelder[3],betas_nelder[4],betas_nelder[5],
	betas_nelder[6],betas_nelder[7]]).reshape((5,1))

#income process: male
income_male_betas = np.array([betas_nelder[8],betas_nelder[9],
	betas_nelder[10]]).reshape((3,1))
c_emp_spouse = betas_nelder[11]


#Production function [young,old]
gamma1 = betas_nelder[12]
gamma2 = betas_nelder[13]
gamma3 = betas_nelder[14]
tfp = betas_nelder[15]
sigma2theta = 1

kappas = [betas_nelder[16],betas_nelder[17]]

#first sigma is normalized
sigma_z = [1,betas_nelder[18]]


#initial theta
rho_theta_epsilon = betas_nelder[19]

#First measure is normalized. starting arbitrary values
#All factor loadings are normalized
lambdas=[1,1]


#Child care price
mup = 750

#Probability of afdc takeup
pafdc=.60

#Probability of snap takeup
psnap=.70

#Data
X_aux=pd.read_csv("/home/jrodriguez/NH_HC/results/model_v2/sample_model.csv")
x_df=X_aux

#Sample size 
N=X_aux.shape[0]

#Data for wage process
#see wage_process.do to see the order of the variables.
x_w=x_df[ ['d_HS2', 'constant' ] ].values


#Data for marriage process
#Parameters: marriage. Last one is the constant
x_m=x_df[ ['age_ra', 'constant']   ].values
marriagep_betas=pd.read_csv("/home/jrodriguez/NH_HC/results/model_v2/marriage_process/betas_m_v2.csv").values

#Data for fertility process (only at X0)
#Parameters: kids. last one is the constant
x_k=x_df[ ['age_ra', 'age_ra2', 'constant']   ].values
kidsp_betas=pd.read_csv("/home/jrodriguez/NH_HC/results/model_v2/kids_process/betas_kids_v2.csv").values


#Minimum set of x's (for interpolation)
x_wmk=x_df[  ['age_ra','age_ra2', 'd_HS2', 'constant'] ].values

#Data for treatment status
passign=x_df[ ['d_RA']   ].values

#The EITC parameters: experiments 1 and 2

#The EITC parameters
eitc_list = pickle.load( open( '/home/jrodriguez/NH_HC/codes/model_v2/simulate_sample/eitc_list.p', 'rb' ) )

#Exp 1: Full EITC, everybody
eitc_list_1 = pickle.load( open( '/home/jrodriguez/NH_HC/codes/model_v2/simulate_sample/eitc_dic_1.p', 'rb' ) )

#Exp 2: Everybody no EITC
eitc_list_4 = pickle.load( open( '/home/jrodriguez/NH_HC/codes/model_v2/simulate_sample/eitc_dic_4.p', 'rb' ) )

#The AFDC parameters
afdc_list = pickle.load( open("/home/jrodriguez/NH_HC/codes/model_v2/simulate_sample/afdc_list.p", 'rb' ) )

#The SNAP parameters
snap_list = pickle.load( open("/home/jrodriguez/NH_HC/codes/model_v2/simulate_sample/snap_list.p", 'rb' ) ) 

#CPI index
cpi =  pickle.load( open("/home/jrodriguez/NH_HC/codes/model_v2/simulate_sample/cpi.p", 'rb' ) )

#Federal Poverty Lines
fpl_list = pickle.load( open("/home/jrodriguez/NH_HC/codes/model_v2/simulate_sample/fpl_list.p", 'rb' ) )

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
age_ch = np.zeros((N,nperiods))
for t in range(nperiods):
	age_ch[:,t] = agech0[:,0] + t


###Auxiliary estimates### 

moments_vector=pd.read_csv("/home/jrodriguez/NH_HC/results/model_v2/aux_model/moments_vector.csv").values

#This is the var cov matrix of aux estimates
var_cov=pd.read_csv("/home/jrodriguez/NH_HC/results/model_v2/aux_model/var_cov.csv").values

#The W matrix in Wald metric
#Using diagonal of Var-Cov matrix of simulated moments
w_matrix  = np.zeros((var_cov.shape[0],var_cov.shape[0]))
for i in range(var_cov.shape[0]):
	w_matrix[i,i] = var_cov[i,i]


#Creating a grid for the emax computation
dict_grid=gridemax.grid()

#For montercarlo integration
D = 25

#For II procedure
M = 200

#How many hours is part- and full-time work
hours_p=15
hours_f=40

#Indicate if model includes a work requirement (wr), 
#and child care subsidy (cs) and a wage subsidy (ws)

#In these experiments, NH is shut down
wr=0
ws=0
cs=0

#number of periods to consider for each input
nperiods_cc = 3
nperiods_ct = 8
nperiods_emp = 8
nperiods_theta = 8

#Young until t=period_y
period_y = 2

#To start model instance
hours = np.zeros(N)
childcare  = np.zeros(N)


##############################################################################
#Baseline E[lnc] and E[lnl] from actual experiments


param0=util.Parameters(alphap,alphaf,mu_c,
	eta,gamma1,gamma2,gamma3,
	tfp,sigma2theta,rho_theta_epsilon,wagep_betas,
	income_male_betas,c_emp_spouse,
	marriagep_betas, kidsp_betas, eitc_list,
	afdc_list,snap_list,cpi,fpl_list,
	lambdas,kappas,pafdc,psnap,mup,sigma_z)

output_ins=estimate.Estimate(nperiods,param0,x_w,x_m,x_k,x_wmk,passign,agech0,nkids0,
	married0,D,dict_grid,M,N,moments_vector,var_cov,hours_p,hours_f,
	wr,cs,ws)

model  = util.Utility(param0,N,x_w,x_m,x_k,passign,
	nkids0,married0,hours,childcare,agech0,hours_p,hours_f,wr,cs,ws)

emax_instance = output_ins.emax(param0,model)
choices_baseline = output_ins.samples(param0,emax_instance,model)

##SD of no EITC (t=0...8)
sd_matrix = np.zeros((nperiods,M))

for j in range(M):
	for t in range(nperiods):
		sd_matrix[t,j] = np.std(np.log(choices_baseline['theta_matrix'][:,t,j]),axis=0)


#COMPUTING EXPERIMENTS

"""
#eitc_list: Everybody with EITC (eitc_list_1) without EITC (eitc_list_4 )
#cc_sub_list: with (1) without (0) CC subsidy
#ubi_lisy: with (1) without (0) universal basic income

"""
eitc_exp_list = [eitc_list_4,eitc_list]
cc_sub_list = [0,1]
ubi_list = [0,1]

"""
Experiments:
0: no EITC, no CC
1: full EITC, no CC
2: full EITC, full CC
3: UBI, no CC
4: UBI, CC
"""

###Two different baselines###
baseline = [[eitc_exp_list[0],cc_sub_list[0],ubi_list[0]],
[eitc_exp_list[0],cc_sub_list[1],ubi_list[0]]]

choices_baseline = []
models_baseline = []
params_baseline = []


for j in range(len(baseline)): #the baseline loop

	print('Im in baseline number', j)

	#Defines the instance with parameters
	params_baseline.append(util.Parameters(alphap,alphaf,mu_c,
	eta,gamma1,gamma2,gamma3,
	tfp,sigma2theta,rho_theta_epsilon,wagep_betas,
	income_male_betas,c_emp_spouse,
	marriagep_betas, kidsp_betas, baseline[j][0],
	afdc_list,snap_list,cpi,fpl_list,
	lambdas,kappas,pafdc,psnap,mup,sigma_z))
	
	output_ins=estimate.Estimate(nperiods,params_baseline[j],x_w,x_m,x_k,x_wmk,passign,agech0,nkids0,
		married0,D,dict_grid,M,N,moments_vector,var_cov,hours_p,hours_f,
		wr,baseline[j][1],baseline[j][2])

	#The model (utility instance)	
	models_baseline.append(Budget(params_baseline[j],N,x_w,x_m,x_k,passign,nkids0,married0,
			hours,childcare,agech0,hours_p,hours_f,wr,
			baseline[j][1],baseline[j][2]))

	#Obtaining emax instances, samples, and betas for M samples
	np.random.seed(1)
	emax_instance = output_ins.emax(params_baseline[j],models_baseline[j])
	choices_baseline.append(output_ins.samples(params_baseline[j],emax_instance,models_baseline[j]))



##Recovering choices
cc_sim_matrix_baseline = []
ct_sim_matrix_baseline = []
h_sim_matrix_baseline = []
theta_sim_matrix_baseline = []
wage_sim_matrix_baseline = []
income_sim_matrix_baseline = []
part_sim_matrix_baseline = []
full_sim_matrix_baseline = []
emp_sim_matrix_baseline = []
theta_sd_baseline = [np.zeros((N,nperiods,M)),np.zeros((N,nperiods,M))]

for j in range(len(baseline)): #the baseline loop
	cc_sim_matrix_baseline.append(choices_baseline[j]['childcare_matrix'])
	ct_sim_matrix_baseline.append(choices_baseline[j]['consumption_matrix'])
	income_sim_matrix_baseline.append(choices_baseline[j]['income_matrix'])
	h_sim_matrix_baseline.append(choices_baseline[j]['hours_matrix'])
	theta_sim_matrix_baseline.append(choices_baseline[j]['theta_matrix'])
	wage_sim_matrix_baseline.append(choices_baseline[j]['wage_matrix'])
	part_sim_matrix_baseline.append(choices_baseline[j]['hours_matrix'] == hours_p)
	full_sim_matrix_baseline.append(choices_baseline[j]['hours_matrix'] == hours_f)
	emp_sim_matrix_baseline.append(choices_baseline[j]['hours_matrix'] > 0 )


###The Experiment loop###
experiments = [ [eitc_exp_list[1],cc_sub_list[0],ubi_list[0]],
[eitc_exp_list[1],cc_sub_list[1],ubi_list[0]],
[eitc_exp_list[0],cc_sub_list[0],ubi_list[1]],
[eitc_exp_list[0],cc_sub_list[1],ubi_list[1]] ]

choices = []
models = []
params = []

for j in range(len(experiments)): #the experiment loop

	print('Im in experiment number ', j)

	#Defines the instance with parameters
	params.append(util.Parameters(alphap,alphaf,mu_c,
	eta,gamma1,gamma2,gamma3,
	tfp,sigma2theta,rho_theta_epsilon,wagep_betas,
	income_male_betas,c_emp_spouse,
	marriagep_betas, kidsp_betas, experiments[j][0],
	afdc_list,snap_list,cpi,fpl_list,
	lambdas,kappas,pafdc,psnap,mup,sigma_z))

	
	output_ins=estimate.Estimate(nperiods,params[j],x_w,x_m,x_k,x_wmk,passign,agech0,nkids0,
		married0,D,dict_grid,M,N,moments_vector,var_cov,hours_p,hours_f,
		wr,experiments[j][1],experiments[j][2])

	#The model (utility instance)	
	models.append(Budget(params[j],N,x_w,x_m,x_k,passign,nkids0,married0,
			hours,childcare,agech0,hours_p,hours_f,wr,
			experiments[j][1],experiments[j][2]))

	#Obtaining emax instances, samples, and betas for M samples
	np.random.seed(1)
	emax_instance = output_ins.emax(params[j],models[j])
	choices.append(output_ins.samples(params[j],emax_instance,models[j]))

##Recovering choices
cc_sim_matrix = []
ct_sim_matrix = []
h_sim_matrix = []
part_sim_matrix = []
full_sim_matrix = []
emp_sim_matrix = []
theta_sim_matrix = []
wage_sim_matrix = []
income_sim_matrix = []
theta_sd = [np.zeros((N,nperiods,M)),np.zeros((N,nperiods,M)),
	np.zeros((N,nperiods,M)),np.zeros((N,nperiods,M))]

for j in range(len(experiments)): #the experiment loop
	cc_sim_matrix.append(choices[j]['childcare_matrix'])
	ct_sim_matrix.append(choices[j]['consumption_matrix'])
	income_sim_matrix.append(choices[j]['income_matrix'])
	h_sim_matrix.append(choices[j]['hours_matrix'])
	theta_sim_matrix.append(choices[j]['theta_matrix'])
	wage_sim_matrix.append(choices[j]['wage_matrix'])
	part_sim_matrix.append(choices[j]['hours_matrix'] == hours_p)
	full_sim_matrix.append(choices[j]['hours_matrix'] == hours_f)
	emp_sim_matrix.append(choices[j]['hours_matrix'] > 0)



######The Contribution to ATE theta#####

#the sample
boo_all = (age_ch[:,2]<=6)


#Impact on ln theta
ate_theta_sd = [np.zeros((nperiods,M)),np.zeros((nperiods,M)),np.zeros((nperiods,M)),np.zeros((nperiods,M))]
av_impact = []
sd_long = []
for k in range(len(experiments)):
	
	if k % 2 == 0:
		z = 0
	else:
		z = 1

	sd_long.append(np.concatenate((np.log(theta_sim_matrix[k]),np.log(theta_sim_matrix_baseline[z])),axis=0))

	for j in range(M):
		for t in range(nperiods):

			ate_theta_sd[k][t,j] = np.mean(np.log(theta_sim_matrix[k][boo_all==1,t,j]) - np.log(theta_sim_matrix_baseline[z][boo_all==1,t,j]))/np.std(sd_long[k][:,t,j],axis=0)

	av_impact.append(np.mean(ate_theta_sd[k],axis=1)) 

#Impact on consumption, child care, labor supply
ate_ct = [np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods))]
ate_cc = [np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods))]
ate_hours = [np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods))]
ate_income = [np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods))]
ate_part = [np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods))]
ate_full = [np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods))]
ate_emp = [np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods))]

for k in range(len(experiments)):

	if k % 2 == 0:
		z = 0
	else:
		z = 1

	ate_ct[k] = np.mean(np.mean(ct_sim_matrix[k][boo_all==1,:,:] - ct_sim_matrix_baseline[z][boo_all==1,:,:],axis=0),axis=1)*12/100
	ate_cc[k] = np.mean(np.mean(cc_sim_matrix[k][boo_all==1,:,:] - cc_sim_matrix_baseline[z][boo_all==1,:,:],axis=0),axis=1)
	ate_hours[k] = np.mean(np.mean(h_sim_matrix[k][boo_all==1,:,:] - h_sim_matrix_baseline[z][boo_all==1,:,:],axis=0),axis=1)
	ate_part[k] = np.mean(np.mean(part_sim_matrix[k][boo_all==1,:,:],axis=0) - np.mean(part_sim_matrix_baseline[z][boo_all==1,:,:],axis=0),axis=1)
	ate_full[k] = np.mean(np.mean(full_sim_matrix[k][boo_all==1,:,:],axis=0) - np.mean(full_sim_matrix_baseline[z][boo_all==1,:,:],axis=0),axis=1)
	ate_emp[k] = np.mean(np.mean(emp_sim_matrix[k][boo_all==1,:,:],axis=0) - np.mean(emp_sim_matrix_baseline[z][boo_all==1,:,:],axis=0),axis=1)
	ate_income[k] = np.mean(np.mean(income_sim_matrix[k][boo_all==1,:,:] - income_sim_matrix_baseline[z][boo_all==1,:,:],axis=0),axis=1)



#For 4 counterfactuals
ate_cont_theta  = [np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M))]
ate_cont_lt  = [np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M))]
ate_cont_cc  = [np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M))]
ate_cont_ct  = [np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M))]


for t in range(nperiods - 1):
	for j in range(M):


		for k in range(len(experiments)): #the counterfactual loop

			if k % 2 == 0:
				z = 0
			else:
				z = 1

			#the theta contribution
			ltheta_th1 = models[k].thetat(t,theta_sim_matrix[k][:,t,j],
				h_sim_matrix_baseline[z][:,t,j],cc_sim_matrix_baseline[z][:,t,j],
				ct_sim_matrix_baseline[z][:,t,j])
			ltheta_th0 = models[k].thetat(t,theta_sim_matrix_baseline[z][:,t,j],
				h_sim_matrix_baseline[z][:,t,j],cc_sim_matrix_baseline[z][:,t,j],
				ct_sim_matrix_baseline[z][:,t,j])
		
			ate_cont_theta[k][t,j] = np.mean(np.log(ltheta_th1[boo_all]) - np.log(ltheta_th0[boo_all]))/np.std(sd_long[k][:,t,j],axis=0)
		
			#The leisure contribution
			ltheta_th1 = models[k].thetat(t,theta_sim_matrix[k][:,t,j],
				h_sim_matrix[k][:,t,j],cc_sim_matrix_baseline[z][:,t,j],
				ct_sim_matrix_baseline[z][:,t,j])
			ltheta_th0 = models[k].thetat(t,theta_sim_matrix[k][:,t,j],
			h_sim_matrix_baseline[z][:,t,j],cc_sim_matrix_baseline[z][:,t,j],
			ct_sim_matrix_baseline[z][:,t,j])
			
			ate_cont_lt[k][t,j] = np.mean(np.log(ltheta_th1[boo_all]) - np.log(ltheta_th0[boo_all]))/np.std(sd_long[k][:,t,j],axis=0)

			#The CC contribution
			ltheta_th1 = models[k].thetat(t,theta_sim_matrix[k][:,t,j],
				h_sim_matrix[k][:,t,j],cc_sim_matrix[k][:,t,j],
				ct_sim_matrix_baseline[z][:,t,j])
			ltheta_th0 = models[k].thetat(t,theta_sim_matrix[k][:,t,j],
				h_sim_matrix[k][:,t,j],cc_sim_matrix_baseline[z][:,t,j],
				ct_sim_matrix_baseline[z][:,t,j])
			ate_cont_cc[k][t,j] = np.mean(np.log(ltheta_th1[boo_all]) - np.log(ltheta_th0[boo_all]))/np.std(sd_long[k][:,t,j],axis=0)

			#The consumption contribution
			ltheta_th1 = models[k].thetat(t,theta_sim_matrix[k][:,t,j],
				h_sim_matrix[k][:,t,j],cc_sim_matrix[k][:,t,j],
				ct_sim_matrix[k][:,t,j])
			ltheta_th0 = models[k].thetat(t,theta_sim_matrix[k][:,t,j],
				h_sim_matrix[k][:,t,j],cc_sim_matrix[k][:,t,j],
				ct_sim_matrix_baseline[z][:,t,j])
			ate_cont_ct[k][t,j] = np.mean(np.log(ltheta_th1[boo_all]) - np.log(ltheta_th0[boo_all]))/np.std(sd_long[k][:,t,j],axis=0)


###The graphs##


#Table: average effects
outcome_list = [r'Money (US\$ 100)', 'Weekly hours worked', 'Child care (percentage points)']

output_list =  [ate_ct,ate_hours,ate_cc]

for j in range(len(experiments)):
	ate_cc[j] = ate_cc[j]*100

#number of periods to consider averaging
periods = [3,3,3]

with open('/home/jrodriguez/NH_HC/results/model_v2/experiments/EITC/table_eitc_mech.tex','w') as f:
	f.write(r'\begin{tabular}{llccccccc}'+'\n')	
	f.write(r'\hline'+'\n')
	f.write(r'Variable &       & (1)   &       & (2)   &       & (3)   &       & (4) \bigstrut\\'+'\n')
	f.write(r'\hline'+'\n')
	for j in range(len(output_list)):
		f.write(
			outcome_list[j]+ '&&'+ '{:3.2f}'.format(np.mean(output_list[j][0][0:periods[j]]))  
			+'&& '+ '{:3.2f}'.format(np.mean(output_list[j][1][0:periods[j]])) 
			+'&& '+ '{:3.2f}'.format(np.mean(output_list[j][2][0:periods[j]]))
			+'&& '+ '{:3.2f}'.format(np.mean(output_list[j][3][0:periods[j]]))
			)

		f.write(r' \bigstrut[t]\\'+'\n')

		
	f.write(r'\hline'+'\n')
	f.write(r'EITC (1995-2003) &       & Yes   &       & Yes   &       & No    &       & No \bigstrut[t]\\'+'\n')
	f.write(r'Unconditional transfer &       & No    &       & No    &       & Yes   &       & Yes \\'+'\n')
	f.write(r'Child care subsidy &       & No    &       & Yes   &       & No    &       & Yes \bigstrut[b]\\'+'\n')
	f.write(r'\hline'+'\n')
	f.write(r'\end{tabular}%'+'\n')



#Effects on ln theta
names_list_v2 = [r'EITC $\checkmark$ - CC subsidy $\times$ ',
r'EITC $\checkmark$ - CC subsidy $\checkmark$',
r'Unconditional $\checkmark$ - CC subsidy $\times$',
r'Unconditional $\checkmark$ - CC subsidy $\checkmark$']


markers_list = ['k-','k--','k-o','k-.']
facecolor_list = ['k','k','k','k']

nper = av_impact[0].shape[0]
fig, ax=plt.subplots()
x = np.array(range(0,nper))
for k in range(len(experiments)):
	ax.plot(x,av_impact[k],markers_list[k],markerfacecolor= facecolor_list[k],
		markeredgewidth=1.0,label=names_list_v2[k],linewidth=3,markersize=11,alpha=0.9)
ax.set_ylabel(r'Effect on child human capital ($\sigma$s)', fontsize=15)
ax.set_xlabel(r'Years after random assignment ($t$)', fontsize=15)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
ax.legend(loc=0)
plt.yticks(fontsize=15)
plt.xticks(fontsize=15)
#ax.set_ylim(-0.01,.50)
plt.show()
fig.savefig('/home/jrodriguez/NH_HC/results/model_v2/experiments/EITC/ate_theta_eitc.pdf', format='pdf')
plt.close()


#Mechanisms Figures
phi_money = np.zeros((nperiods-1,len(experiments)))
phi_cc = np.zeros((nperiods-1,len(experiments)))
phi_time = np.zeros((nperiods-1,len(experiments)))

for k in range(len(experiments)):
	c_money = np.mean(ate_cont_ct[k],axis=1)
	c_cc = np.mean(ate_cont_cc[k],axis=1)
	c_time = np.mean(ate_cont_lt[k],axis=1)

	phi_money[0,k] = c_money[0]
	phi_cc[0,k] = c_cc[0]
	phi_time[0,k] = c_time[0]
	for t in range(c_money.shape[0]-1):
		phi_money[t+1,k] = c_money[t+1] + gamma1*phi_money[t,k]
		phi_cc[t+1,k] = c_cc[t+1] + gamma1*phi_cc[t,k]
		phi_time[t+1,k] = c_time[t+1] + gamma1*phi_time[t,k]

#Plot accumulated contributions up to period nt
nt = 2

x = np.array(len(experiments))
total = phi_time[nt,:] + phi_cc[nt,:] + phi_money[nt,:]
bar1 =  phi_time[nt,:]/total #Time
bar2 = phi_money[nt,:]/total # Income
bar3 = phi_cc[nt,:]/total # CC
y = np.arange(len(experiments))

y_labels = [r'EITC, CS $\times$', r'EITC, CS $\checkmark$', 
r'Uncond, CS $\times$', r'Uncond, CS $\checkmark$']

fig, ax=plt.subplots()
ax.barh(y,bar1.tolist(),height=0.5,color='gray',edgecolor='black',label='Time')
ax.barh(y,bar2.tolist(),height=0.5,left=bar1,color='blue',alpha=0.7,edgecolor='black',label='Money')
ax.barh(y,bar3.tolist(),height=0.5,left=list(map(lambda g,y:g+y,bar1.tolist(),bar2.tolist())),color='green',alpha=0.7,edgecolor='black',hatch='//',label='Child care')
#ax.set_xlabel(r'Share explained by input', fontsize=14)
ax.legend(loc='upper center',bbox_to_anchor=(0.5, -0.05),fontsize=12,ncol=3)
plt.yticks(y,y_labels,fontsize=11)
plt.show()
fig.savefig('/home/jrodriguez/NH_HC/results/model_v2/experiments/EITC/mech_share_income.pdf', format='pdf')
plt.close()


