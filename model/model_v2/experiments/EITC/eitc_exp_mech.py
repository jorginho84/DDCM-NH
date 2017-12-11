"""
execfile('eitc_exp_mech.py')

This file computes EITC experiments using the whole sample to build counterfactuals
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
sys.path.append("/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample")
import utility as util
import gridemax
import time
import int_linear
import emax as emax
import simdata as simdata
sys.path.append("/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/estimation")
import estimate as estimate
sys.path.append("/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/experiments")
from ate_gen import ATE
sys.path.append("/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/experiments/EITC")
from bset import Budget

np.random.seed(1)

betas_nelder=np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/betas_modelv16.npy')

#Number of periods where all children are less than or equal to 18
nperiods = 8

#Utility function
eta=betas_nelder[0]
alphap=betas_nelder[1]
alphaf=betas_nelder[2]

#wage process
wagep_betas=np.array([betas_nelder[3],betas_nelder[4],betas_nelder[5],
	betas_nelder[6],betas_nelder[7],betas_nelder[8],betas_nelder[9]]).reshape((7,1))

#Production function [young,old]
gamma1= betas_nelder[10]
gamma2= betas_nelder[11]
gamma3= betas_nelder[12]
tfp=betas_nelder[13]
sigma2theta=1

kappas=[[betas_nelder[14],betas_nelder[15],betas_nelder[16],betas_nelder[17]],
[betas_nelder[18],betas_nelder[19],betas_nelder[20],betas_nelder[21]]]

#initial theta
rho_theta_epsilon = betas_nelder[22]

#First measure is normalized. starting arbitrary values
#All factor loadings are normalized
lambdas=[1,1]


#Child care price
mup = 0.57*0 + (1-0.57)*750

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
#see wage_process.do to see the order of the variables.
x_w=x_df[ ['age_ra', 'd_HS2', 'constant' ] ].values


#Data for marriage process
#Parameters: marriage. Last one is the constant
x_m=x_df[ ['age_ra', 'constant']   ].values
marriagep_betas=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/marriage_process/betas_m_v2.csv').values

#Data for fertility process (only at X0)
#Parameters: kids. last one is the constant
x_k=x_df[ ['age_ra', 'age_ra2', 'constant']   ].values
kidsp_betas=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/kids_process/betas_kids_v2.csv').values


#Minimum set of x's (for interpolation)
x_wmk=x_df[  ['age_ra', 'age_ra2', 'd_HS2', 'constant'] ].values

#Data for treatment status
passign=x_df[ ['d_RA']   ].values

#The EITC parameters: experiments 1 and 2

#The EITC parameters
eitc_list = pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/eitc_list.p', 'rb' ) )

#Exp 1: Full EITC vs No EITC
eitc_list_1 = pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/eitc_dic_1.p', 'rb' ) )

#Exp 2: Full EITC vs fixed EITC
eitc_list_2 = pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/eitc_dic_2.p', 'rb' ) )

#Exp 3: Everybody with EITC
eitc_list_3 = pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/eitc_dic_3.p', 'rb' ) )

#Exp 4: Everybody no EITC
eitc_list_4 = pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/eitc_dic_4.p', 'rb' ) )

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
age_ch = np.zeros((N,nperiods))
for t in range(nperiods):
	age_ch[:,t] = agech0[:,0] + t


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

#For montercarlo integration
D=50

#For II procedure
M=1000

#How many hours is part- and full-time work
hours_p=15
hours_f=40

#Indicate if model includes a work requirement (wr), 
#and child care subsidy (cs) and a wage subsidy (ws)

#In these experiments, NH is shut down
wr=0
ws=0

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

cs=0
param0=util.Parameters(alphap,alphaf,eta,gamma1,gamma2,gamma3,
	tfp,sigma2theta, rho_theta_epsilon,wagep_betas, marriagep_betas, kidsp_betas, eitc_list,
	afdc_list,snap_list,cpi,lambdas,kappas,pafdc,psnap,mup)

output_ins=estimate.Estimate(nperiods,param0,x_w,x_m,x_k,x_wmk,passign,agech0,nkids0,
	married0,D,dict_grid,M,N,moments_vector,var_cov,hours_p,hours_f,
	wr,cs,ws)

model  = util.Utility(param0,N,x_w,x_m,x_k,passign,
	nkids0,married0,hours,childcare,agech0,hours_p,hours_f,wr,cs,ws)

emax_instance = output_ins.emax(param0,model)
choices_baseline = output_ins.samples(param0,emax_instance,model)

#The E[Log] of consumption and leisure
ec = np.mean(np.mean(np.log(choices_baseline['consumption_matrix']),axis=2),axis=0)
hours_m = choices_baseline['hours_matrix']
boo_p = hours_m == hours_p
boo_f = hours_m == hours_f
boo_u = hours_m == 0
cc = choices_baseline['choice_matrix']>2
ecc = np.mean(np.mean(cc,axis=2),axis=0)
tch = cc*(148 - 40) + (1-cc)*(boo_u*148 + boo_p*(148 - hours_p) + boo_f*(148 - hours_f)) 
el = np.mean(np.mean(np.log(tch),axis=2),axis=0)
e_age = np.mean(age_ch<=6,axis=0)
np.save('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/EITC/ec.npy',ec)
np.save('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/EITC/el.npy',el)
np.save('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/EITC/ecc.npy',ecc)
np.save('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/EITC/e_age.npy',e_age)


#SD of no EITC (t=0...8)
sd_matrix = np.zeros((nperiods,M))

for j in range(M):
	for t in range(nperiods):
		sd_matrix[t,j] = np.std(np.log(choices_baseline['theta_matrix'][:,t,j]),axis=0)


#COMPUTING EXPERIMENTS

"""
#eitc_list_1: Full EITC vs No EITC
#eitc_list_2: Full EITC vs fixed EITC
#eitc_list_3: Everybody with EITC
#eitc_list_4: Everybody no EITC

#cc_sub_list: with (1) without (0) CC subsidy

"""
eitc_list = [eitc_list_1,eitc_list_2,eitc_list_3,eitc_list_4]
cc_sub_list = [0,1]

"""
EXP0: no EITC, no CC
EXP1: full EITC, no CC
EXP2: no EITC, full CC
EXP3: full EITC, full CC
"""

experiments=[ [eitc_list[3],cc_sub_list[0]], [eitc_list[2],cc_sub_list[0]],
[eitc_list[3],cc_sub_list[1]], [eitc_list[2],cc_sub_list[1]] ]

choices = []
models = []


###The Experiment loop###
for j in range(len(experiments)): #the experiment loop

	print 'Im in experiment number ', j

	#Defines the instance with parameters
	param0=util.Parameters(alphap,alphaf,eta,gamma1,gamma2,gamma3,
		tfp,sigma2theta,rho_theta_epsilon,wagep_betas, marriagep_betas, kidsp_betas,
		experiments[j][0],afdc_list,snap_list,cpi,lambdas,kappas,pafdc,psnap,mup)

	output_ins=estimate.Estimate(nperiods,param0,x_w,x_m,x_k,x_wmk,passign,agech0,nkids0,
		married0,D,dict_grid,M,N,moments_vector,var_cov,hours_p,hours_f,
		wr,experiments[j][1],ws)

	#The model (utility instance)	
	models.append(Budget(param0,N,x_w,x_m,x_k,passign,nkids0,married0,
			hours,childcare,agech0,hours_p,hours_f,wr,experiments[j][1],ws))

	#Obtaining emax instances, samples, and betas for M samples
	np.random.seed(1)
	emax_instance = output_ins.emax(param0,models[j])
	choices.append(output_ins.samples(param0,emax_instance,models[j]))

##Recovering choices
cc_sim_matrix = []
ct_sim_matrix = []
h_sim_matrix = []
theta_sim_matrix = []
wage_sim_matrix = []
theta_sd = [np.zeros((N,nperiods,M)),np.zeros((N,nperiods,M)),np.zeros((N,nperiods,M))]
for j in range(len(experiments)): #the experiment loop
	theta_sd.append(np.zeros((N,nperiods,M)))
	cc_sim_matrix.append(choices[j]['choice_matrix']>=3)
	ct_sim_matrix.append(choices[j]['consumption_matrix'])
	h_sim_matrix.append(choices[j]['hours_matrix'])
	theta_sim_matrix.append(choices[j]['theta_matrix'])
	wage_sim_matrix.append(choices[j]['wage_matrix'])

	for t in range(nperiods):
		for k in range(M):
			theta_sd[j][:,t,k] = np.log(theta_sim_matrix[j][:,t,k])/sd_matrix[t,k]




######The Contribution to ATE theta#####

#Impact on ln theta
ate_theta_sd = [np.zeros((nperiods,M)),np.zeros((nperiods,M)),np.zeros((nperiods,M))]
av_impact = []
for k in range(1,4):
	for j in range(M):
		for t in range(nperiods):
			ate_theta_sd[k-1][t,j] = np.mean(theta_sd[k][:,t,j] - theta_sd[0][:,t,j],axis=0)

	av_impact.append(np.mean(ate_theta_sd[k-1],axis=1)) 

#Impact on consumption, child care, labor supply
ate_ct = [np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods))]
ate_cc = [np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods))]
ate_part = [np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods))]
ate_full = [np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods))]


full_0 = h_sim_matrix[0]==hours_f
part_0 = h_sim_matrix[0]==hours_p

for k in range(1,4):
	full = h_sim_matrix[k]==hours_f
	part = h_sim_matrix[k]==hours_p

	ate_ct[k-1] = np.mean(np.mean(ct_sim_matrix[k] - ct_sim_matrix[0],axis=0),axis=1)/1000
	ate_cc[k-1] = np.mean(np.mean(cc_sim_matrix[k] - cc_sim_matrix[0],axis=0),axis=1)
	ate_part[k-1] = np.mean(np.mean(part,axis=2) -  np.mean(part_0,axis=2),axis=0)
	ate_full[k-1] = np.mean(np.mean(full,axis=2) -  np.mean(full_0,axis=2),axis=0)


#Defining counterfactuals (3)
#EXP1 - EXP0
#EXP2 - EXP0
#EXP3 - EXP0


#For the 3 counterfactuals
ate_cont_theta  = [np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M))]
ate_cont_lt  = [np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M))]
ate_cont_cc  = [np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M))]
ate_cont_ct  = [np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M))]



for t in range(nperiods - 1):
	for j in range(M):


		for k in range(1,4): #the counterfactual loop

			#the sample
			boo_all = (age_ch[:,2]<=6)

			#the theta contribution
			ltheta_th0 = models[0].thetat(t,theta_sim_matrix[0][:,t,j],
				h_sim_matrix[0][:,t,j],cc_sim_matrix[0][:,t,j],
				ct_sim_matrix[0][:,t,j])
			ltheta_th1 = models[k].thetat(t,theta_sim_matrix[k][:,t,j],
				h_sim_matrix[0][:,t,j],cc_sim_matrix[0][:,t,j],
				ct_sim_matrix[0][:,t,j])
		
			ate_cont_theta[k-1][t,j] = np.mean(np.log(ltheta_th1[boo_all]) - np.log(ltheta_th0[boo_all]))/sd_matrix[t,j]
		
			#The leisure contribution
			ltheta_th1 = models[k].thetat(t,theta_sim_matrix[k][:,t,j],
				h_sim_matrix[k][:,t,j],cc_sim_matrix[0][:,t,j],
				ct_sim_matrix[0][:,t,j])
			ltheta_th0 = models[k].thetat(t,theta_sim_matrix[k][:,t,j],
			h_sim_matrix[0][:,t,j],cc_sim_matrix[0][:,t,j],
			ct_sim_matrix[0][:,t,j])
			
			ate_cont_lt[k-1][t,j] = np.mean(np.log(ltheta_th1[boo_all]) - np.log(ltheta_th0[boo_all]))/sd_matrix[t,j]

			#The CC contribution
			ltheta_th1 = models[k].thetat(t,theta_sim_matrix[k][:,t,j],
				h_sim_matrix[k][:,t,j],cc_sim_matrix[k][:,t,j],
				ct_sim_matrix[0][:,t,j])
			ltheta_th0 = models[k].thetat(t,theta_sim_matrix[k][:,t,j],
				h_sim_matrix[k][:,t,j],cc_sim_matrix[0][:,t,j],
				ct_sim_matrix[0][:,t,j])
			ate_cont_cc[k-1][t,j] = np.mean(np.log(ltheta_th1[boo_all]) - np.log(ltheta_th0[boo_all]))/sd_matrix[t,j]

			#The consumption contribution
			ltheta_th1 = models[k].thetat(t,theta_sim_matrix[k][:,t,j],
				h_sim_matrix[k][:,t,j],cc_sim_matrix[k][:,t,j],
				ct_sim_matrix[k][:,t,j])
			ltheta_th0 = models[k].thetat(t,theta_sim_matrix[k][:,t,j],
				h_sim_matrix[k][:,t,j],cc_sim_matrix[k][:,t,j],
				ct_sim_matrix[0][:,t,j])
			ate_cont_ct[k-1][t,j] = np.mean(np.log(ltheta_th1[boo_all]) - np.log(ltheta_th0[boo_all]))/sd_matrix[t,j]


###The graphs##


#Table: average effects
outcome_list = [r'Consumption (US\$ 1,000)', 'Part-time', 'Full-time', 'Child care']

ate_theta = [np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods))]
for j in range(3):
	ate_theta[j] = np.mean(ate_theta_sd[j][1:],axis=1)

output_list =  [ate_ct,ate_part,ate_full,ate_cc]

#number of periods to consider averaging
periods = [nperiods,nperiods,nperiods,3,nperiods-1]

with open('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/EITC/table_eitc_mech.tex','w') as f:
	f.write(r'\begin{tabular}{llccccc}'+'\n')	
	f.write(r'\hline'+'\n')
	f.write(r'ATE   && (1)   && (2)   && (3) \bigstrut[b]\\'+'\n')
	f.write(r'\cline{1-1}\cline{3-7}')
	for j in range(len(output_list)):
		f.write(outcome_list[j]+ '&&'+ '{:3.2f}'.format(np.mean(output_list[j][0][0:periods[j]]))  
			+'&& '+ '{:3.2f}'.format(np.mean(output_list[j][1][0:periods[j]])) 
			+'&& '+ '{:3.2f}'.format(np.mean(output_list[j][2][0:periods[j]])))
		f.write(r' \bigstrut[t]\\'+'\n')

	f.write(r'\hline'+'\n')
	f.write(r'EITC (1995-2003) &       & $\checkmark$ &       &       &       & $\checkmark$ \\'+'\n')
	f.write(r'Child care subsidy &       &       &       & $\checkmark$ &       & $\checkmark$ \bigstrut[b]\\'+'\n')
	f.write(r'\hline'+'\n')
	f.write(r'\end{tabular}%'+'\n')




#Mechanisms
y = []
exp = ['eitc1_cc0', 'eitc0_cc1', 'eitc1_cc1']

for j in range(3): #the experiment loop
	x = np.array(range(1,nperiods))
	y1 = np.mean(ate_cont_theta[j],axis=1)
	y2 = np.mean(ate_cont_lt[j],axis=1)
	y3 = np.mean(ate_cont_cc[j],axis=1)
	y4 = np.mean(ate_cont_ct[j],axis=1)
	total = y1 + y2 + y3 + y4

	fig, ax=plt.subplots()
	ax.plot(x,y2, color='k',linewidth=3,marker='o')
	ax.bar(x,y1, color='k' ,alpha=.8,bottom=y2,align='center')
	ax.bar(x,y3, color='k' , alpha=.4, bottom=y1+y2,align='center')
	ax.bar(x,y4,color='w',bottom=y3+y1+y2,align='center',edgecolor='k',
		linewidth=1)
	ax.set_ylabel(r'Effect on child human capital ($\sigma$s)', fontsize=14)
	ax.set_xlabel(r'Years after random assignment ($t$)', fontsize=14)
	ax.spines['right'].set_visible(False)
	ax.spines['top'].set_visible(False)
	ax.yaxis.set_ticks_position('left')
	ax.xaxis.set_ticks_position('bottom')
	ax.margins(0, 0)
	ax.set_ylim(-0.01,.50)
	ax.legend(['Time', r'$\theta_t$','Child care','Consumption'],loc=7)
	plt.show()
	fig.savefig('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/EITC/mech_' + exp[j] + '.pdf', format='pdf')
	plt.close()

	#this is for the next graph
	y.append(np.concatenate((np.array([0]),total),axis=0))



#Effects on ln theta
nper = av_impact[0].shape[0]
fig, ax=plt.subplots()
x = np.array(range(0,nper))
plot0=ax.plot(x,y[0],'k-',label=r'EITC $\checkmark$ - CC subsidy $\times$',alpha=0.9)
plot1=ax.plot(x,y[1],'k--',label=r'EITC $\times$ - CC subsidy $\checkmark$',alpha=0.9)
plot2=ax.plot(x,y[2],'k:',label=r'EITC $\checkmark$ - CC subsidy $\checkmark$',alpha=0.9)
plt.setp(plot0,linewidth=3)
plt.setp(plot1,linewidth=3)
plt.setp(plot2,linewidth=3)
ax.set_ylabel(r'Effect on child human capital ($\sigma$s)', fontsize=14)
ax.set_xlabel(r'Years after random assignment ($t$)', fontsize=14)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
ax.legend([r'EITC $\checkmark$ - CC subsidy $\times$',
	r'EITC $\times$ - CC subsidy $\checkmark$',
	r'EITC $\checkmark$ - CC subsidy $\checkmark$'])
ax.legend(loc=0)
ax.set_ylim(-0.01,.50)
plt.show()
fig.savefig('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/EITC/ate_theta_eitc.pdf', format='pdf')
plt.close()
