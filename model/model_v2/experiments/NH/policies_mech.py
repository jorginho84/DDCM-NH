"""

exec(open("/home/jrodriguez/NH_HC/codes/model/experiments/NH/policies_mech.py").read())

This file plots ATE theta of different New Hope policies

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
from joblib import Parallel, delayed
from scipy import interpolate
import matplotlib
#matplotlib.use('Agg') # Force matplotlib to not use any Xwindows backend.
import matplotlib.pyplot as plt
sys.path.append("/home/jrodriguez/NH_HC/codes/model/simulate_sample")
import utility as util
import gridemax
import time
import int_linear
import emax as emax
import simdata as simdata
sys.path.append("/home/jrodriguez/NH_HC/codes/model/estimation")
import estimate as estimate
sys.path.append("/home/jrodriguez/NH_HC/codes/model/experiments/NH")
from ates import ATE
from util2 import Prod2



np.random.seed(1)

betas_nelder=np.load("/home/jrodriguez/NH_HC/results/Model/estimation/betas_modelv24.npy")

#Number of periods where all children are less than or equal to 18
nperiods = 8

#Utility function
eta = betas_nelder[0] + 0.1
alphap = betas_nelder[0]
alphaf = betas_nelder[2] - 0.1 

#wage process
wagep_betas=np.array([betas_nelder[3],betas_nelder[4],1.65,
	betas_nelder[6],betas_nelder[7]]).reshape((5,1))

#income process: male
income_male_betas = np.array([0.2,7.2,.32]).reshape((3,1))
c_emp_spouse = .8


#Production function [young,old]
gamma1= betas_nelder[8]
gamma2= 0.05
gamma3= betas_nelder[10] + 0.02
tfp=0.1
sigma2theta = 1
varphi = 0.7


kappas=[[betas_nelder[12],betas_nelder[13],betas_nelder[14],betas_nelder[15]],
[betas_nelder[16]-0.15,betas_nelder[17]-0.15,betas_nelder[18]-0.15,
betas_nelder[19]-0.15]]

#initial theta
rho_theta_epsilon = 0.05
rho_theta_ab = 0.25


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
X_aux=pd.read_csv('/home/jrodriguez/NH_HC/results/Model/sample_model.csv')
x_df=X_aux

#Sample size 
N=X_aux.shape[0]

#Data for wage process
#see wage_process.do to see the order of the variables.
x_w=x_df[ ['d_HS2', 'constant' ] ].values


#Data for marriage process
#Parameters: marriage. Last one is the constant
x_m=x_df[ ['age_ra', 'constant']   ].values
marriagep_betas=pd.read_csv('/home/jrodriguez/NH_HC/results/marriage_process/betas_m_v2.csv').values

#Data for fertility process (only at X0)
#Parameters: kids. last one is the constant
x_k=x_df[ ['age_ra', 'age_ra2', 'constant']   ].values
kidsp_betas=pd.read_csv('/home/jrodriguez/NH_HC/results/kids_process/betas_kids_v2.csv').values


#Minimum set of x's (for interpolation)
x_wmk=x_df[  ['age_ra','age_ra2', 'd_HS2', 'constant'] ].values

#Data for treatment status
passign=x_df[ ['d_RA']   ].values
#passign = np.random.binomial(1,0.5,(N,1))

#The EITC parameters
eitc_list = pickle.load( open("/home/jrodriguez/NH_HC/codes/model/simulate_sample/eitc_list.p", 'rb' ) )

#The AFDC parameters
afdc_list = pickle.load( open("/home/jrodriguez/NH_HC/codes/model/simulate_sample/afdc_list.p", 'rb' ) )

#The SNAP parameters
snap_list = pickle.load( open("/home/jrodriguez/NH_HC/codes/model/simulate_sample/snap_list.p", 'rb' ) ) 


#CPI index
cpi =  pickle.load( open("/home/jrodriguez/NH_HC/codes/model/simulate_sample/cpi.p", 'rb' ) )



#Here: the estimates from the auxiliary model
###
###

#Assuming random start
#theta0=np.exp(np.random.randn(N))

#number of kids at baseline
nkids0=x_df[ ['nkids_baseline']   ].values

#marital status at baseline
married0=x_df[ ['d_marital_2']   ].values

#age of child at baseline
agech0_a=x_df[['age_t0A']].values[:,0]
agech0_b=x_df[['age_t0B']].values[:,0]
d_childb=x_df[['d_childB']].values
d_childa=x_df[['d_childA']].values

agech_a = np.zeros((N,nperiods))
agech_b = np.zeros((N,nperiods))

for periodt in range(nperiods):
	agech_a[d_childa[:,0] == 1,periodt] = agech0_a[d_childa[:,0] == 1] + periodt
	agech_b[d_childb[:,0] == 1,periodt] = agech0_b[d_childb[:,0] == 1] + periodt


agech = np.concatenate((agech_a[d_childa[:,0] == 1,:],
	agech_b[d_childb[:,0] == 1,:]),axis=0)


#Defines the instance with parameters
param0 = util.Parameters(alphap,alphaf,eta,gamma1,gamma2,gamma3,
	tfp,sigma2theta,varphi,rho_theta_epsilon,rho_theta_ab,wagep_betas,
	income_male_betas,c_emp_spouse,
	marriagep_betas, kidsp_betas, eitc_list,
	afdc_list,snap_list,cpi,lambdas,kappas,pafdc,psnap,mup)


###Auxiliary estimates###
moments_vector=pd.read_csv("/home/jrodriguez/NH_HC/results/aux_model/moments_vector.csv").values

#This is the var cov matrix of aux estimates
var_cov=pd.read_csv("/home/jrodriguez/NH_HC/results/aux_model/var_cov.csv").values

#The vector of aux standard errors
#Using diagonal of Var-Cov matrix of simulated moments
se_vector  = np.sqrt(np.diagonal(var_cov))

#Creating a grid for the emax computation
dict_grid=gridemax.grid()

#For montercarlo integration
D = 20

#Number of samples to produce
M = 20

#How many hours is part- and full-time work
hours_p = 15
hours_f = 40

#################################################################################
###Obtaining counterfactuals

#This is the list of models to compute [wr,cs,ws]. This order is fixed
models_list = [[0,0,1], [0,1,1], [1,0,1],[0,1,0],[1,1,0],[1,1,1]]
models_names = ['WS','CS_WS','WR_WS','CS','WR_CS','WR_CS_WS']

#number of periods to consider for each input
nperiods_cc = 3
nperiods_ct = 3
nperiods_emp = 3
nperiods_theta = 8

#Young until periodt=period_y
period_y = 2

#Computing contribution to ATE theta by policy
ate_cont_theta  = []
ate_cont_lt  = []
ate_cont_cc  = []
ate_cont_ct  = []

###Computing counterfactuals
ates_list = []
choices_list = []
cost_list = []
contribution_list = []
sd_matrix_list = []

for j in range(len(models_list)):
	output_ins=estimate.Estimate(nperiods,param0,x_w,x_m,x_k,x_wmk,passign,
		agech0_a,agech0_b,d_childa,d_childb,nkids0,
		married0,D,dict_grid,M,N,moments_vector,var_cov,hours_p,hours_f,
		models_list[j][0],models_list[j][1],models_list[j][2])

	hours = np.zeros(N) #arbitrary to initialize model instance
	childcare  = np.zeros(N)

	#obtaining values to normalize theta
	model = util.Utility(param0,N,x_w,x_m,x_k,passign,nkids0,married0,hours,
		childcare,childcare,agech0_a,agech0_b,d_childa,d_childb,
		hours_p,hours_f,models_list[j][0],models_list[j][1],models_list[j][2])

	np.random.seed(1)
	emax_instance = output_ins.emax(param0,model)
	choices = output_ins.samples(param0,emax_instance,model)
	#The E[Log] of consumption, leisure, and child care to normalize E[log theta]=0
	ec = np.mean(np.mean(np.log(choices['consumption_matrix']),axis=2),axis=0)
	hours_m = choices['hours_matrix']
	boo_p = hours_m == hours_p
	boo_f = hours_m == hours_f
	boo_u = hours_m == 0
	cc_a = choices['childcare_a_matrix'].copy()
	cc_b = choices['childcare_b_matrix'].copy()
	ecc_a = np.mean(np.mean(cc_a,axis=2),axis=0)
	ecc_b = np.mean(np.mean(cc_a,axis=2),axis=0)
	
	tch_a = np.zeros((N,nperiods,M))
	tch_b = np.zeros((N,nperiods,M))
	for t in range(nperiods):
		tch_a[agech_a[:,t]<=5,t,:] = cc_a[agech_a[:,t]<=5,t,:]*(168 - hours_f) + (1-cc_a[agech_a[:,t]<=5,t,:])*(168 - hours_m[agech_a[:,t]<=5,t,:])
		tch_a[agech_a[:,t]>5,t,:] = 133 - hours_m[agech_a[:,t]>5,t,:]

		tch_b[agech_b[:,t]<=5,t,:] = cc_b[agech_b[:,t]<=5,t,:]*(168 - hours_f) + (1-cc_b[agech_b[:,t]<=5,t,:])*(168 - hours_m[agech_b[:,t]<=5,t,:])
		tch_b[agech_b[:,t]>5,t,:] = 133 - hours_m[agech_b[:,t]>5,t,:] 
	
	el_a = np.mean(np.mean(np.log(tch_a),axis=2),axis=0)
	el_b = np.mean(np.mean(np.log(tch_b),axis=2),axis=0)
	e_age_a = np.mean(agech_a<=5,axis=0)
	e_age_b = np.mean(agech_b<=5,axis=0)
	
	np.save('/home/jrodriguez/NH_HC/results/Model/experiments/NH/ec.npy',ec)
	np.save('/home/jrodriguez/NH_HC/results/Model/experiments/NH/el_a.npy',el_a)
	np.save('/home/jrodriguez/NH_HC/results/Model/experiments/NH/el_b.npy',el_b)
	np.save('/home/jrodriguez/NH_HC/results/Model/experiments/NH/ecc_a.npy',ecc_a)
	np.save('/home/jrodriguez/NH_HC/results/Model/experiments/NH/ecc_b.npy',ecc_b)
	np.save('/home/jrodriguez/NH_HC/results/Model/experiments/NH/e_age_a.npy',e_age_a)
	np.save('/home/jrodriguez/NH_HC/results/Model/experiments/NH/e_age_b.npy',e_age_b)
	
		#SD matrix
	ltheta_a = np.log(choices['theta_matrix_a'])
	ltheta_b = np.log(choices['theta_matrix_b'])
	ltheta = np.concatenate((ltheta_a[d_childa[:,0]==1,:,:],
		ltheta_b[d_childb[:,0]==1,:,:]),axis=0)

	sd_matrix = np.zeros((nperiods,M))
	for jj in range (M):
		for t in range(nperiods):
			sd_matrix[t,jj] = np.std(ltheta[:,t,jj],axis=0)
	
	sd_matrix_list.append(sd_matrix)
	
	#Obtaining counterfactuals with the same emax
	choices_c = {}
	models = []
	for k in range(2):
		passign_aux=k*np.ones((N,1))#everybody in treatment/control
		models.append(Prod2(param0,N,x_w,x_m,x_k,passign,
					nkids0,married0,hours,childcare,childcare,
					agech0_a,agech0_b,d_childa,d_childb,hours_p,hours_f,
					models_list[j][0],models_list[j][1],models_list[j][2]))
		output_ins.__dict__['passign'] = passign_aux
		choices_c['Choice_' + str(k)] = output_ins.samples(param0,emax_instance,models[k])

	choices_list.append(choices_c)
	ate_ins = ATE(N,M,choices_c,models,agech0_a,agech0_b,d_childa,d_childb,
		passign,hours_p,hours_f,nperiods,
		nperiods_cc,nperiods_ct,nperiods_emp,nperiods_theta,period_y,sd_matrix)
	ates = ate_ins.sim_ate()
	ates_list.append(ates['ATES'])
	contribution_list.append(ates['Contributions'])

	#Costs
	cost_list.append(choices['cscost_matrix'] + choices['iscost_matrix'] )







#################################################################################
#Figures
"""
y_limit_upper = np.mean(contribution_list[1]['Theta'],axis=1) + np.mean(contribution_list[1]['Time'],axis=1) + np.mean(contribution_list[1]['CC'],axis=1) + np.mean(contribution_list[j]['Money'],axis=1)
y_limit_lower = np.mean(contribution_list[5]['Time'],axis=1)


#Mechanisms figures
for j in range(len(models_list)):
	x = np.array(range(1,nperiods))
	y1 = np.mean(contribution_list[j]['Theta'],axis=1)
	y2 = np.mean(contribution_list[j]['Time'],axis=1)
	y3 = np.mean(contribution_list[j]['CC'],axis=1)
	y4 = np.mean(contribution_list[j]['Money'],axis=1)
	total = y1 + y2 + y3 + y4
	horiz_line_data = np.array([0 for i in range(len(x))])
	fig, ax=plt.subplots()
	ax.plot(x,y2, color='k',zorder=1,linewidth=4.5,label='Time')
	ax.plot(x,horiz_line_data, 'k--',linewidth=2)
	ax.fill_between(x,y2,(y2+y1), color='k' ,alpha=.65,zorder=2,label='Lagged human capital')
	ax.fill_between(x,(y2+y1),(y2+y1+y3), color='k' ,alpha=.35,zorder=3,label='Child care')
	ax.fill_between(x,(y2+y1+y3),(total), color='k' ,alpha=.12,zorder=4,label='Money')
	ax.set_ylabel(r'Effect on child human capital ($\sigma$s)', fontsize=14)
	ax.set_xlabel(r'Years after random assignment ($t$)', fontsize=14)
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
	#ax.set_ylim(y_limit_lower[0] - 0.02,y_limit_upper[3] + 0.02)
	ax.legend(loc=5,fontsize=19)
	plt.yticks(fontsize=11)
	plt.xticks(fontsize=11)
	#ax.legend(['Time', 'Lagged human capital','Child care','Consumption'],loc=5)
	plt.show()
	fig.savefig('C:\\Users\\jrodriguezo\\Dropbox\\Chicago\\Research\\Human capital and the household\\lizzie_backup\\results\\Model\\experiments\\NH\\mech_' + models_names[j]+'.pdf', format='pdf')
	plt.close()

"""


"""

This is the order:

names_list_v2 = ['Wage sub', 'Wage sub + Child care sub','Wage sub + Work req', 'Child care sub', 
'Child care sub + Work req', 'Full treatment']
"""

"""

#Figure: ATE on theta of wage sub vs cc sub/no work requirements
names_list_v2 = ['Wage sub', 'Child care sub','Wage sub + Child care sub']
markers_list = ['k-','k--','k-o' ]
facecolor_list = ['k','k','k' ]
y_list = []
y_list.append(np.mean(ates_list[0]['Theta'],axis=1))
y_list.append(np.mean(ates_list[3]['Theta'],axis=1))
y_list.append(np.mean(ates_list[1]['Theta'],axis=1))

x = np.array(range(1,nperiods))
fig, ax=plt.subplots()
for k in range(len(y_list)):
	ax.plot(x,y_list[k],markers_list[k],markerfacecolor= facecolor_list[k],
		markeredgewidth=1.0,label=names_list_v2[k],linewidth=3,markersize=11,alpha=0.9)
ax.set_ylabel(r'Impact on child human capital ($\sigma$s)', fontsize=12)
ax.set_xlabel(r'Years after random assignment ($t$)', fontsize=12)
ax.set_ylim(0,0.16)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
plt.yticks(fontsize=11)
plt.xticks(fontsize=11)
ax.legend(loc=4,fontsize = 11)
plt.show()
fig.savefig('C:\\Users\\jrodriguezo\\Dropbox\\Chicago\\Research\\Human capital and the household\\lizzie_backup\\results\\Model\\experiments\\NH\\ate_theta_policies_1.pdf', format='pdf')
plt.close()


#Figure: ATE on theta of wage sub vs cc sub/ work requirements
names_list_v2 = ['Wage sub + Work req', 'Child care sub + Work req','Full treatment']
markers_list = ['k-','k--','k-o' ]
facecolor_list = ['k','k','k' ]
y_list = []
y_list.append(np.mean(ates_list[2]['Theta'],axis=1))
y_list.append(np.mean(ates_list[4]['Theta'],axis=1))
y_list.append(np.mean(ates_list[5]['Theta'],axis=1))

x = np.array(range(1,nperiods))
fig, ax=plt.subplots()
for k in range(len(y_list)):
	ax.plot(x,y_list[k],markers_list[k],markerfacecolor= facecolor_list[k],
		markeredgewidth=1.0,label=names_list_v2[k],linewidth=3,markersize=11,alpha=0.9)
ax.set_ylabel(r'Impact on child human capital ($\sigma$s)', fontsize=12)
ax.set_xlabel(r'Years after random assignment ($t$)', fontsize=12)
ax.set_ylim(0,0.16)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
plt.yticks(fontsize=11)
plt.xticks(fontsize=11)
ax.legend(loc=4,fontsize = 11)
plt.show()
fig.savefig('C:\\Users\\jrodriguezo\\Dropbox\\Chicago\\Research\\Human capital and the household\\lizzie_backup\\results\\Model\\experiments\\NH\\ate_theta_policies_2.pdf', format='pdf')
plt.close()

####The table###
#the list of policies
outcome_list = [r'Consumption (US\$)', 'Part-time', 'Full-time', 'Child care']

output_list = ['Consumption', 'Part-time', 'Full-time', 'CC']

with open('C:\\Users\\jrodriguezo\\Dropbox\\Chicago\\Research\\Human capital and the household\\lizzie_backup\\results\\Model\\experiments\\NH\\table_nhpol_hh.tex','w') as f:
	f.write(r'\begin{tabular}{lcccccccccccc}'+'\n')
	f.write(r'\hline'+'\n')
	f.write('ATE'+r'& & (1)   & & (2)&& (3)& & (4) && (5) && (6) \bigstrut[b]\\'+'\n')
	f.write(r'\cline{1-1}\cline{3-13}'+'\n')
	for j in range(len(outcome_list)):
		
		if j==0: #consumption w/ no decimals
			
			f.write(outcome_list[j])
			for k in range(6): #the policy loop
				f.write(r'  && '+ '{:02.0f}'.format(np.mean(ates_list[k][output_list[j]][0:3,:])))
			f.write(r' \bigstrut[t]\\'+'\n')
		else:
			f.write(outcome_list[j])
			for k in range(6): #the policy loop
				f.write(r'  && '+ '{:04.3f}'.format(np.mean(ates_list[k][output_list[j]][0:3,:])))
			f.write(r' \bigstrut[t]\\'+'\n')

	f.write(r'\hline'+'\n')
	f.write(r'Wage subsidy && $\checkmark$ && $\checkmark$ && $\checkmark$ &&&&  & & $\checkmark$ \bigstrut[t]\\'+'\n')
	f.write(r'Child care subsidy &       &       &       & $\checkmark$ &       &       &       & $\checkmark$ &       & $\checkmark$ &       & $\checkmark$ \\'+'\n')
	f.write(r'Work requirement &       &       &       &       &       & $\checkmark$ &       &       &       & $\checkmark$ &       & $\checkmark$ \bigstrut[b]\\'+'\n')
	f.write(r'\hline'+'\n')
	f.write(r'\end{tabular}'+'\n')


"""