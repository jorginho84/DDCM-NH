"""

exec(open("/home/jrodriguez/NH_HC/codes/model_v2/experiments/EITC/eitc_exp_mech.py").read())


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

betas_nelder=np.load("/home/jrodriguez/NH_HC/results/model_v2/estimation/betas_modelv27_twoch.npy")


#Number of periods where all children are less than or equal to 18
nperiods = 8

#Utility function
eta = betas_nelder[0]
alphap = betas_nelder[1]
alphaf = betas_nelder[2]

#wage process
wagep_betas=np.array([betas_nelder[3],betas_nelder[4],betas_nelder[5],
	betas_nelder[6],betas_nelder[7]]).reshape((5,1))

#income process: male
income_male_betas = np.array([betas_nelder[8],betas_nelder[9],
	betas_nelder[10]]).reshape((3,1))
c_emp_spouse = betas_nelder[11]


#Production function [young,old]
gamma1= betas_nelder[12]
gamma2= betas_nelder[13]
gamma3= betas_nelder[14] - 0.05
tfp = betas_nelder[15]
sigma2theta = 1



kappas=[[betas_nelder[16],betas_nelder[17],
betas_nelder[18],betas_nelder[19]],
[betas_nelder[20],betas_nelder[21],betas_nelder[22],
betas_nelder[23]]]

#initial theta
rho_theta_epsilon = betas_nelder[24]

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
D=20

#For II procedure
M=200

#How many hours is part- and full-time work
hours_p=20
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
	tfp,sigma2theta,rho_theta_epsilon,wagep_betas,
	income_male_betas,c_emp_spouse,
	marriagep_betas, kidsp_betas, eitc_list,
	afdc_list,snap_list,cpi,lambdas,kappas,pafdc,psnap,mup)

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
#eitc_list_1: Everybody with EITC
#eitc_list_4: Everybody no EITC

#cc_sub_list: with (1) without (0) CC subsidy

"""
eitc_list = [eitc_list_4,eitc_list_1]
cc_sub_list = [0,1]

"""
EXP0: no EITC, no CC
EXP1: full EITC, no CC
EXP2: no EITC, full CC
EXP3: full EITC, full CC
"""

experiments=[ [eitc_list[0],cc_sub_list[0]], [eitc_list[1],cc_sub_list[0]],
[eitc_list[0],cc_sub_list[1]], [eitc_list[1],cc_sub_list[1]] ]

choices = []
models = []
params = []


###The Experiment loop###
for j in range(len(experiments)): #the experiment loop

	print('Im in experiment number ', j)

	#Defines the instance with parameters
	params.append(util.Parameters(alphap,alphaf,eta,gamma1,gamma2,gamma3,
			tfp,sigma2theta,rho_theta_epsilon,wagep_betas, 
			income_male_betas,c_emp_spouse,
			marriagep_betas, kidsp_betas,
			experiments[j][0],afdc_list,snap_list,cpi,lambdas,kappas,pafdc,psnap,mup))

	output_ins=estimate.Estimate(nperiods,params[j],x_w,x_m,x_k,x_wmk,passign,agech0,nkids0,
		married0,D,dict_grid,M,N,moments_vector,var_cov,hours_p,hours_f,
		wr,experiments[j][1],ws)

	#The model (utility instance)	
	models.append(Budget(params[j],N,x_w,x_m,x_k,passign,nkids0,married0,
			hours,childcare,agech0,hours_p,hours_f,wr,experiments[j][1],ws))

	#Obtaining emax instances, samples, and betas for M samples
	np.random.seed(1)
	emax_instance = output_ins.emax(params[j],models[j])
	choices.append(output_ins.samples(params[j],emax_instance,models[j]))

##Recovering choices
cc_sim_matrix = []
ct_sim_matrix = []
h_sim_matrix = []
theta_sim_matrix = []
wage_sim_matrix = []
theta_sd = [np.zeros((N,nperiods,M)),np.zeros((N,nperiods,M)),np.zeros((N,nperiods,M))]
for j in range(len(experiments)): #the experiment loop
	theta_sd.append(np.zeros((N,nperiods,M)))
	cc_sim_matrix.append(choices[j]['childcare_matrix'])
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
outcome_list = [r'Consumption (US\$ 1,000)', 'Part-time (percentage points)', 'Full-time (percentage points)', 'Child care (percentage points)']

ate_theta = [np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods))]
for j in range(3):
	ate_theta[j] = np.mean(ate_theta_sd[j][1:],axis=1)

output_list =  [ate_ct,ate_part,ate_full,ate_cc]

for k in range(3):
	for j in range(3):
		output_list[k+1][j] = output_list[k+1][j]*100

#number of periods to consider averaging
periods = [nperiods,nperiods,nperiods,3,nperiods-1]

with open('/home/jrodriguez/NH_HC/results/model_v2/experiments/EITC/table_eitc_mech.tex','w') as f:
	f.write(r'\begin{tabular}{llccccc}'+'\n')	
	f.write(r'\hline'+'\n')
	f.write(r'Variable   && (1)   && (2)   && (3) \bigstrut[b]\\'+'\n')
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


#Mechanisms: for paper
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
	fig.savefig('/home/jrodriguez/NH_HC/results/model_v2/experiments/EITC/mech_' + exp[j] + '.pdf', format='pdf')
	plt.close()

	#this is for the next graph
	y.append(np.concatenate((np.array([0]),total),axis=0))

#Mechanisms: for slides
y = []
exp = ['eitc1_cc0', 'eitc0_cc1', 'eitc1_cc1']

for j in range(3): #the experiment loop
	x = np.array(range(1,nperiods))
	y1 = np.mean(ate_cont_theta[j],axis=1)
	y2 = np.mean(ate_cont_lt[j],axis=1)
	y3 = np.mean(ate_cont_cc[j],axis=1)
	y4 = np.mean(ate_cont_ct[j],axis=1)
	total = y1 + y2 + y3 + y4
	horiz_line_data = np.array([0 for i in range(len(x))])

	fig, ax=plt.subplots()
	ax.plot(x,y2, color='k',zorder=1,linewidth=4.5,label='Time')
	ax.plot(x,horiz_line_data, 'k--',linewidth=2)
	ax.fill_between(x,y2,(y2+y1), color='k' ,alpha=.65,zorder=2,label='Lagged human capital')
	ax.fill_between(x,(y2+y1),(y2+y1+y3), color='k' ,alpha=.35,zorder=3,label='Child care')
	ax.fill_between(x,(y2+y1+y3),(total), color='k' ,alpha=.12,zorder=4,label='Money')
	ax.set_ylabel(r'Effect on child human capital ($\sigma$s)', fontsize=20)
	ax.set_xlabel(r'Years after random assignment ($t$)', fontsize=20)
	#ax.annotate('Explained by time', xy=(2, y2[2]), xytext=(2.5, y2[2]-0.02),
	#	arrowprops=dict(facecolor='black', shrink=0.05,connectionstyle="arc3"))
	#ax.annotate('Explained by consumption', xy=(3, total[2]-0.01), xytext=(2, total[2]+0.02),
	#	arrowprops=dict(facecolor='black', shrink=0.05,connectionstyle="arc3"))
	
	#ax.annotate('Explained by child care', xy=(2.2, y1[1]+0.04), xytext=(3, y1[1]+0.02),
	#	arrowprops=dict(facecolor='black', shrink=0.05,connectionstyle="arc3"))
	#ax.text(4,0.05,'Explained by lagged human capital')
	ax.spines['right'].set_visible(False)
	ax.spines['top'].set_visible(False)
	ax.yaxis.set_ticks_position('left')
	ax.xaxis.set_ticks_position('bottom')
	ax.margins(0, 0)
	ax.legend(loc=5,fontsize = 19)
	plt.show()
	fig.savefig('/home/jrodriguez/NH_HC/results/model_v2/experiments/EITC/mech_' + exp[j] + '_slides.pdf', format='pdf')
	plt.close()

	#this is for the next graph
	y.append(np.concatenate((np.array([0]),total),axis=0))



#Effects on ln theta
names_list_v2 = [r'EITC $\checkmark$ - CC subsidy $\times$',
r'EITC $\times$ - CC subsidy $\checkmark$',
r'EITC $\checkmark$ - CC subsidy $\checkmark$']
markers_list = ['k-','k--','k-o']
facecolor_list = ['k','k','k']

nper = av_impact[0].shape[0]
fig, ax=plt.subplots()
x = np.array(range(0,nper))
for k in range(len(y)):
	ax.plot(x,y[k],markers_list[k],markerfacecolor= facecolor_list[k],
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
ax.set_ylim(-0.01,.50)
plt.show()
fig.savefig('/home/jrodriguez/NH_HC/results/model_v2/experiments/EITC/ate_theta_eitc.pdf', format='pdf')
plt.close()
