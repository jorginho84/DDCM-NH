"""
execfile('mech.py')
This file computes a decomposition analysis of variables that explain ATE on theta

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
sys.path.append("/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/experiments/NH")
from util2 import Prod2



np.random.seed(1)

betas_nelder=np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/betas_modelv23.npy')

#Number of periods where all children are less than or equal to 18
nperiods = 8

#Utility function
eta = betas_nelder[0]
alphap = betas_nelder[1]
alphaf = betas_nelder[2]

#wage process
wagep_betas=np.array([betas_nelder[3],betas_nelder[4],betas_nelder[5],
	betas_nelder[6],betas_nelder[7]]).reshape((5,1))


#Production function [young,old]
gamma1= betas_nelder[8]
gamma2= betas_nelder[9]
gamma3= betas_nelder[10]
tfp=betas_nelder[11]
sigma2theta=1

kappas=[[betas_nelder[12],betas_nelder[13],betas_nelder[14],betas_nelder[15]],
[betas_nelder[16],betas_nelder[17],betas_nelder[18],betas_nelder[19]]]

#initial theta
rho_theta_epsilon = betas_nelder[20]


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
x_w=x_df[ ['d_HS2', 'constant' ] ].values


#Data for marriage process
#Parameters: marriage. Last one is the constant
x_m=x_df[ ['age_ra', 'constant']   ].values
marriagep_betas=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/marriage_process/betas_m_v2.csv').values

#Data for fertility process (only at X0)
#Parameters: kids. last one is the constant
x_k=x_df[ ['age_ra', 'age_ra2', 'constant']   ].values
kidsp_betas=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/kids_process/betas_kids_v2.csv').values


#Minimum set of x's (for interpolation)
x_wmk=x_df[  ['age_ra','age_ra2', 'd_HS2', 'constant'] ].values

#Data for treatment status
passign=x_df[ ['d_RA']   ].values
#passign = np.random.binomial(1,0.5,(N,1))

#The EITC parameters
eitc_list = pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/eitc_list.p', 'rb' ) )

#The AFDC parameters
afdc_list = pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/afdc_list.p', 'rb' ) )

#The SNAP parameters
snap_list = pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/snap_list.p', 'rb' ) )

#CPI index
cpi =  pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/cpi.p', 'rb' ) )


#number of kids at baseline
nkids0=x_df[ ['nkids_baseline']   ].values

#marital status at baseline
married0=x_df[ ['d_marital_2']   ].values

#age of child at baseline
agech0=x_df[['age_t0']].values
age_ch = np.zeros((N,nperiods))
for t in range(nperiods):
	age_ch[:,t] = agech0[:,0] + t



#Defines the instance with parameters
param0=util.Parameters(alphap,alphaf,eta,gamma1,gamma2,gamma3,
	tfp,sigma2theta,rho_theta_epsilon,wagep_betas, marriagep_betas, kidsp_betas, eitc_list,
	afdc_list,snap_list,cpi,lambdas,kappas,pafdc,psnap,mup)

###Auxiliary estimates###
moments_vector=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/moments_vector.csv').values

#This is the var cov matrix of aux estimates
var_cov=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/var_cov.csv').values

#The vector of aux standard errors
#Using diagonal of Var-Cov matrix of simulated moments
se_vector  = np.sqrt(np.diagonal(var_cov))


#Creating a grid for the emax computation
dict_grid=gridemax.grid()

#For montercarlo integration
D=50

#Number of samples to produce
M=1000

#How many hours is part- and full-time work
hours_p=20
hours_f=40

#Indicate if model includes a work requirement (wr), 
#and child care subsidy (cs) and a wage subsidy (ws)
wr=1
cs=1
ws=1

#The estimate class
output_ins=estimate.Estimate(nperiods,param0,x_w,x_m,x_k,x_wmk,passign,agech0,nkids0,
	married0,D,dict_grid,M,N,moments_vector,var_cov,hours_p,hours_f,
	wr,cs,ws)

#The model (utility instance)
hours = np.zeros(N)
childcare  = np.zeros(N)

model  = util.Utility(param0,N,x_w,x_m,x_k,passign,
	nkids0,married0,hours,childcare,agech0,hours_p,hours_f,wr,cs,ws)

#Obtaining emax instance: this is fixed throughout the exercise
emax_instance = output_ins.emax(param0,model)

#Original choices (dictionary)
choices = output_ins.samples(param0,emax_instance,model)


#The E[Log] of consumption, leisure, and child care to normalize E[log theta]=0
ec = np.mean(np.mean(np.log(choices['consumption_matrix']),axis=2),axis=0)
hours_m = choices['hours_matrix']
boo_p = hours_m == hours_p
boo_f = hours_m == hours_f
boo_u = hours_m == 0
cc = choices['choice_matrix']>2
ecc = np.mean(np.mean(cc,axis=2),axis=0)
tch = np.zeros((N,nperiods,M))
for t in range(nperiods):
	tch[age_ch[:,t]<=5,t,:] = cc[age_ch[:,t]<=5,t,:]*(168 - hours_f) + (1-cc[age_ch[:,t]<=5,t,:])*(168 - hours_m[age_ch[:,t]<=5,t,:])
	tch[age_ch[:,t]>5,t,:] = 133 - hours_m[age_ch[:,t]>5,t,:]
el = np.mean(np.mean(np.log(tch),axis=2),axis=0)
e_age = np.mean(age_ch<=5,axis=0)
np.save('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/NH/ec.npy',ec)
np.save('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/NH/el.npy',el)
np.save('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/NH/ecc.npy',ecc)
np.save('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/NH/e_age.npy',e_age)

#E[ln \theta] by period
e_lnt = np.mean(np.mean(np.log(choices['theta_matrix']),axis=0),axis=1)
sd_lnt = np.mean(np.std(np.log(choices['theta_matrix']),axis=0),axis=1)

np.std(np.log(choices['theta_matrix'][:,:,0]),axis=0)

#Obtaining samples with the same emax
choices_c = {}
models = []
for j in range(2):
	passign_aux=j*np.ones((N,1))
	models.append(Prod2(param0,N,x_w,x_m,x_k,passign,
		nkids0,married0,hours,childcare,agech0,hours_p,hours_f,wr,cs,ws))
	output_ins.__dict__['passign'] = passign_aux
	choices_c['Choice_' + str(j)] = output_ins.samples(param0,emax_instance,models[j])


#Age of child
age_ch = np.zeros((N,nperiods))
for t in range(nperiods):
	age_ch[:,t] = agech0[:,0] + t

##################################################
#ATE on theta.
theta_matrix = np.log(choices['theta_matrix'])
ate_theta = np.mean(np.mean(theta_matrix[passign[:,0]==1,:,:],axis=0) - np.mean(theta_matrix[passign[:,0]==0,:,:],axis=0),axis=1)


ltheta = np.log(choices['theta_matrix'])
sd_matrix = np.zeros((nperiods,M))
for j in range (M):
	for t in range(nperiods):
		sd_matrix[t,j] = np.std(ltheta[:,t,j],axis=0)
		ltheta[:,t,j] = (ltheta[:,t,j] - np.mean(ltheta[:,t,j],axis=0))/np.std(ltheta[:,t,j],axis=0)

ate_theta_sd = np.mean(np.mean(ltheta[passign[:,0]==1,:,:],axis=0) - np.mean(ltheta[passign[:,0]==0,:,:],axis=0),axis=1)


theta_sim_matrix = []
for j in range(2):
	theta_sim_matrix.append(choices_c['Choice_' + str(j)]['theta_matrix'])

#For measuring in SD units
theta_sd = [np.zeros((N,nperiods,M)),np.zeros((N,nperiods,M))]

for j in range(M):
	for t in range(nperiods):
		for k in range(2):
			theta_sd[k][:,t,j] = np.log(theta_sim_matrix[k][:,t,j])/sd_matrix[t,j]


#Another measure of SDs
long_theta = np.concatenate((theta_sim_matrix[0],theta_sim_matrix[1]),axis=0)
sd_matrix_long = np.zeros((nperiods,M))
for j in range (M):
	for t in range(nperiods):
		sd_matrix_long[t,j] = np.std(np.log(long_theta[:,t,j]),axis=0)



#Choices
cc_sim_matrix = []
for j in range(2):
	cc_sim_matrix.append(choices_c['Choice_' + str(j)]['choice_matrix']>=3)

ct_sim_matrix = []
for j in range(2):
	ct_sim_matrix.append(choices_c['Choice_' + str(j)]['consumption_matrix'])

#impact on period 0
ate_ct_sim = np.mean(np.mean(ct_sim_matrix[1][:,0,:] - ct_sim_matrix[0][:,0,:],axis=1),axis=0)

income_sim_matrix = []
for j in range(2):
	income_sim_matrix.append(choices_c['Choice_' + str(j)]['income_matrix'])

ate_income_sim = np.mean(np.mean(income_sim_matrix[1][:,0,:] - income_sim_matrix[0][:,0,:],axis=1),axis=0)


h_sim_matrix = []
for j in range(2):
	h_sim_matrix.append(choices_c['Choice_' + str(j)]['hours_matrix'])

#samples

sample1 = (h_sim_matrix[1][:,0,:]==40) & (h_sim_matrix[0][:,0,:]<40)
sample2	=((h_sim_matrix[1][:,0,:]==40) & (h_sim_matrix[0][:,0,:]==40)) | (h_sim_matrix[1][:,0,:]<40)

ate_theta_sim = np.zeros((nperiods,M))
ate_theta_sim_sd = np.zeros((nperiods,M))
for j  in range(M):
	for t in range(nperiods):
		ate_theta_sim_sd[t,j] = 	np.mean(theta_sd[1][:,t,j] - theta_sd[0][:,t,j],axis=0)
		ate_theta_sim[t,j] = np.mean(theta_sim_matrix[1][:,t,j] - theta_sim_matrix[0][:,t,j],axis=0)

np.mean(ate_theta_sim_sd,axis=1)
np.mean(ate_theta_sim,axis=1)



#Computing contribution to ATE theta by age [young,old,overall]
ate_cont_theta  = [np.zeros((nperiods-1,M)),np.zeros((nperiods-1,M)),np.zeros((nperiods-1,M))]
ate_cont_lt  = [np.zeros((nperiods-1,M)),np.zeros((nperiods-1,M)),np.zeros((nperiods-1,M))]
ate_cont_cc  = [np.zeros((nperiods-1,M)),np.zeros((nperiods-1,M)),np.zeros((nperiods-1,M))]
ate_cont_ct  = [np.zeros((nperiods-1,M)),np.zeros((nperiods-1,M)),np.zeros((nperiods-1,M))]


for periodt in range(nperiods-1):									

	for j in range(M):
	#the theta contribution
	
		
		#the sample
		boo_y = (h_sim_matrix[1][:,0,j]==40) & (h_sim_matrix[0][:,0,j]<40) & (age_ch[:,2]<=6)
		boo_o = (((h_sim_matrix[1][:,0,j]==40) & (h_sim_matrix[0][:,0,j]==40)) | (h_sim_matrix[1][:,0,j]<40)) & (age_ch[:,2]<=6)
		boo_all = (age_ch[:,2]<=6)
		
		ltheta_th1 = models[1].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[0][:,periodt,j],cc_sim_matrix[0][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])
		ltheta_th0 = models[0].thetat(periodt,theta_sim_matrix[0][:,periodt,j],
			h_sim_matrix[0][:,periodt,j],cc_sim_matrix[0][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])
		ate_cont_theta[0][periodt,j] = np.mean(np.log(ltheta_th1[boo_y]) - np.log(ltheta_th0[boo_y]))/sd_matrix[periodt,j]
		ate_cont_theta[1][periodt,j] = np.mean(np.log(ltheta_th1[boo_o]) - np.log(ltheta_th0[boo_o]))/sd_matrix[periodt,j]
		ate_cont_theta[2][periodt,j] = np.mean(np.log(ltheta_th1[boo_all]) - np.log(ltheta_th0[boo_all]))/sd_matrix[periodt,j]


	#The leisure contribution
		ltheta_th1 = models[1].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[1][:,periodt,j],cc_sim_matrix[0][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])
		ltheta_th0 = models[0].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[0][:,periodt,j],cc_sim_matrix[0][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])
		ate_cont_lt[0][periodt,j] = np.mean(np.log(ltheta_th1[boo_y]) - np.log(ltheta_th0[boo_y]))/sd_matrix[periodt,j]
		ate_cont_lt[1][periodt,j] = np.mean(np.log(ltheta_th1[boo_o]) - np.log(ltheta_th0[boo_o]))/sd_matrix[periodt,j]
		ate_cont_lt[2][periodt,j] = np.mean(np.log(ltheta_th1[boo_all]) - np.log(ltheta_th0[boo_all]))/sd_matrix[periodt,j]

	#The CC contribution
		ltheta_th1 = models[1].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[1][:,periodt,j],cc_sim_matrix[1][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])
		ltheta_th0 = models[0].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[1][:,periodt,j],cc_sim_matrix[0][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])
		ate_cont_cc[0][periodt,j] = np.mean(np.log(ltheta_th1[boo_y]) - np.log(ltheta_th0[boo_y]))/sd_matrix[periodt,j]
		ate_cont_cc[1][periodt,j] = np.mean(np.log(ltheta_th1[boo_o]) - np.log(ltheta_th0[boo_o]))/sd_matrix[periodt,j]
		ate_cont_cc[2][periodt,j] = np.mean(np.log(ltheta_th1[boo_all]) - np.log(ltheta_th0[boo_all]))/sd_matrix[periodt,j]

	#The consumption contribution
		ltheta_th1 = models[1].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[1][:,periodt,j],cc_sim_matrix[1][:,periodt,j],
			ct_sim_matrix[1][:,periodt,j])
		ltheta_th0 = models[0].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[1][:,periodt,j],cc_sim_matrix[1][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])
		ate_cont_ct[0][periodt,j] = np.mean(np.log(ltheta_th1[boo_y]) - np.log(ltheta_th0[boo_y]))/sd_matrix[periodt,j]
		ate_cont_ct[1][periodt,j] = np.mean(np.log(ltheta_th1[boo_o]) - np.log(ltheta_th0[boo_o]))/sd_matrix[periodt,j]
		ate_cont_ct[2][periodt,j] = np.mean(np.log(ltheta_th1[boo_all]) - np.log(ltheta_th0[boo_all]))/sd_matrix[periodt,j]

	
###The graphs##

#For paper
exp = ['extensive-margin', 'intensive-margin', 'overall']

for j in range(3): #the experiment loop
	x = np.array(range(1,nperiods))
	y1 = np.mean(ate_cont_theta[j],axis=1)
	y2 = np.mean(ate_cont_lt[j],axis=1)
	y3 = np.mean(ate_cont_cc[j],axis=1)
	y4 = np.mean(ate_cont_ct[j],axis=1)
	total = y1 + y2 + y3 + y4
	horiz_line_data = np.array([0 for i in xrange(len(x))])

	fig, ax=plt.subplots()
	ax.plot(x,y2, color='k',zorder=1,linewidth=4.5,label='Time')
	ax.plot(x,horiz_line_data, 'k--',linewidth=2)
	ax.fill_between(x,y2,(y2+y1), color='k' ,alpha=.7,zorder=2)
	ax.fill_between(x,(y2+y1),(y2+y1+y3), color='k' ,alpha=.4,zorder=3)
	ax.fill_between(x,(y2+y1+y3),(total), color='k' ,alpha=.15,zorder=4)
	ax.set_ylabel(r'Effect on child human capital ($\sigma$s)', fontsize=14)
	ax.set_xlabel(r'Years after random assignment ($t$)', fontsize=14)
	ax.spines['right'].set_visible(False)
	ax.spines['top'].set_visible(False)
	ax.yaxis.set_ticks_position('left')
	ax.xaxis.set_ticks_position('bottom')
	ax.margins(0, 0)
	ax.set_ylim(-0.05,.35)
	ax.legend(['Time', 'Lagged human capital','Child care','Consumption'],loc=4)
	plt.show()
	fig.savefig('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/NH/mech_' + exp[j] + '.pdf', format='pdf')
	plt.close()

#For slides
exp = ['extensive-margin', 'intensive-margin', 'overall']


for j in range(3): #the experiment loop
	x = np.array(range(1,nperiods))
	y1 = np.mean(ate_cont_theta[j],axis=1)
	y2 = np.mean(ate_cont_lt[j],axis=1)
	y3 = np.mean(ate_cont_cc[j],axis=1)
	y4 = np.mean(ate_cont_ct[j],axis=1)
	total = y1 + y2 + y3 + y4
	horiz_line_data = np.array([0 for i in xrange(len(x))])

	fig, ax=plt.subplots()
	ax.plot(x,y2, color='k',zorder=1,linewidth=4.5)
	ax.plot(x,horiz_line_data, 'k--',linewidth=2)
	ax.fill_between(x,y2,(y2+y1), color='k' ,alpha=.65,zorder=2)
	ax.fill_between(x,(y2+y1),(y2+y1+y3), color='k' ,alpha=.35,zorder=3)
	ax.fill_between(x,(y2+y1+y3),(total), color='k' ,alpha=.12,zorder=4)
	ax.set_ylabel(r'Effect on child human capital ($\sigma$s)', fontsize=14)
	ax.set_xlabel(r'Years after random assignment ($t$)', fontsize=14)
	ax.annotate('Explained by time', xy=(2, y2[2]), xytext=(2.5, y2[2]-0.02),
		arrowprops=dict(facecolor='black', shrink=0.05,connectionstyle="arc3"))
	ax.annotate('Explained by consumption', xy=(3, total[2]-0.01), xytext=(2, total[2]+0.02),
		arrowprops=dict(facecolor='black', shrink=0.05,connectionstyle="arc3"))
	
	ax.annotate('Explained by child care', xy=(2.2, y1[1]+0.04), xytext=(3, y1[1]+0.02),
		arrowprops=dict(facecolor='black', shrink=0.05,connectionstyle="arc3"))
	ax.text(4,0.05,'Explained by lagged human capital')
	ax.spines['right'].set_visible(False)
	ax.spines['top'].set_visible(False)
	ax.yaxis.set_ticks_position('left')
	ax.xaxis.set_ticks_position('bottom')
	ax.margins(0, 0)
	ax.set_ylim(y2[0]-0.035,total[2] + 0.02)
	#ax.legend(loc=5)
	#ax.legend(['Time', 'Lagged human capital','Child care','Consumption'],loc=5)
	plt.show()
	fig.savefig('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/NH/mech_' + exp[j] + '_slides.pdf', format='pdf')
	plt.close()

#for slides: total effect

exp = ['extensive-margin', 'intensive-margin', 'overall']


for j in range(3): #the experiment loop
	x = np.array(range(1,nperiods))
	y1 = np.mean(ate_cont_theta[j],axis=1)
	y2 = np.mean(ate_cont_lt[j],axis=1)
	y3 = np.mean(ate_cont_cc[j],axis=1)
	y4 = np.mean(ate_cont_ct[j],axis=1)
	total = y1 + y2 + y3 + y4
	horiz_line_data = np.array([0 for i in xrange(len(x))])

	fig, ax=plt.subplots()
	ax.plot(x,total, color='k',zorder=1,linewidth=4.5)
	ax.plot(x,horiz_line_data, 'k--',linewidth=2)
	ax.set_ylabel(r'Effect on child human capital ($\sigma$s)', fontsize=14)
	ax.set_xlabel(r'Years after random assignment ($t$)', fontsize=14)
	ax.spines['right'].set_visible(False)
	ax.spines['top'].set_visible(False)
	ax.yaxis.set_ticks_position('left')
	ax.xaxis.set_ticks_position('bottom')
	ax.margins(0, 0)
	ax.set_ylim(y2[0]-0.035,total[2] + 0.02)
	#ax.legend(loc=5)
	#ax.legend(['Time', 'Lagged human capital','Child care','Consumption'],loc=5)
	plt.show()
	fig.savefig('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/NH/mech_total_slides.pdf', format='pdf')
	plt.close()


#Contribution % pc
j=0
ate_cont_ct_pc = np.mean(ate_cont_ct[j],axis=1)/ (np.mean(ate_cont_theta[j],axis=1)+ np.mean(ate_cont_lt[j],axis=1) + np.mean(ate_cont_cc[j],axis=1) + np.mean(ate_cont_ct[j],axis=1))
ate_cont_cc_pc = np.mean(ate_cont_cc[j],axis=1)/ (np.mean(ate_cont_theta[j],axis=1)+ np.mean(ate_cont_lt[j],axis=1) + np.mean(ate_cont_cc[j],axis=1) + np.mean(ate_cont_ct[j],axis=1))
ate_cont_lt_pc = np.mean(ate_cont_lt[j],axis=1)/ (np.mean(ate_cont_theta[j],axis=1)+ np.mean(ate_cont_lt[j],axis=1) + np.mean(ate_cont_cc[j],axis=1) + np.mean(ate_cont_ct[j],axis=1))
ate_cont_theta_pc = np.mean(ate_cont_theta[j],axis=1)/ (np.mean(ate_cont_theta[j],axis=1)+ np.mean(ate_cont_lt[j],axis=1) + np.mean(ate_cont_cc[j],axis=1) + np.mean(ate_cont_ct[j],axis=1))

np.mean(ate_cont_ct[j],axis=1) + np.mean(ate_cont_cc[j],axis=1) + np.mean(ate_cont_lt[j],axis=1) + np.mean(ate_cont_theta[j],axis=1)

ate_cont_ct_pc + ate_cont_cc_pc + ate_cont_lt_pc
#Impact of income, sd units, for 1st period
ate_theta_sim_sd[1]*ate_cont_ct_pc[0] 

(y2[0] + y3[0] + y4[0])*gamma1

#additional income
income = []
income.append(choices_c['Choice_0']['income_matrix'])
income.append(choices_c['Choice_1']['income_matrix'])

np.mean(np.mean(income[1] - income[0],axis=2),axis=0)