"""
exec(open("/home/jrodriguez/NH_HC/codes/model_v2/simulate_sample/master_sim.py").read())

(1) Defines a set of parameters and X's
(2) Defines a grid of state variables
(3) Obtains a dictionary with the set of emax functions
(4) Given (3), simulates fake data

The emax functions are interpolating instances (see int_linear.py for 
	more information)

(1). The parameters and X's are related to the specificaciones of the regressions
on marriage, number of kids, and the wage process. Make sure to match those in
"marriage_process/marriage_process.do";"kids_process/kids_process.do"; and
"wage_process/wage.do".

(2) and (3). Uses gridemax.py to construct the grid. Use this file to modify 
the size of the grid. Importantly, the variables in the grid must coincide
to those in (1). Then, it uses emax.py and int_linear.py to compute emax functions
that depends on the grid values. It returns a dictionary of emax functions, which
are instances of the class defined in int_linear

(4) The emax dictionary is an input in the class found in simdata.py.

pip2.7 install --user line_profiler


"""
import numpy as np
import pandas as pd
import pickle
import tracemalloc
import itertools
import sys, os
from scipy import stats
from scipy import interpolate
import matplotlib.pyplot as plt
import time
from pathos.multiprocessing import ProcessPool
sys.path.append("/home/jrodriguez/NH_HC/codes/model_v2/simulate_sample")
import utility as util
import gridemax
import int_linear
import emax as emax
import simdata as simdata


np.random.seed(1);
#Sample size
#N=315

betas_nelder = np.load("/home/jrodriguez/NH_HC/results/Model/estimation/betas_modelv46.npy")


#Number of periods where all children are less than or equal to 18
nperiods = 8

#Utility function
eta = .05
alphap = betas_nelder[1]
alphaf = -0.05
mu_c = -0.56

#wage process en employment processes: female
wagep_betas=np.array([0.24,betas_nelder[4],1.28,
	betas_nelder[6],betas_nelder[7]]).reshape((5,1))

#income process: male
income_male_betas = np.array([betas_nelder[8],betas_nelder[9],
	betas_nelder[10]]).reshape((3,1))
c_emp_spouse = betas_nelder[11]


#Production function [young,old]
gamma1 = 0.9
gamma2 = 0.01
gamma3 = 0.01
tfp = 0.4
sigma2theta = 1

kappas = [0,0]

#first sigma is normalized
sigma_z = [1,1]

#initial theta
rho_theta_epsilon = betas_nelder[18]

#All factor loadings are normalized
lambdas=[1,1]

#Child care price
mup = 750

#Probability of afdc takeup
pafdc=.60

#Probability of snap takeup
psnap=.70

#Data
#X_aux=pd.read_csv('C:\\Users\\Jorge\\Dropbox\\Chicago\\Research\\Human capital and the household\\results\\Model\\Xs.csv')
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
marriagep_betas=pd.read_csv("/home/jrodriguez/NH_HC/results/marriage_process/betas_m_v2.csv").values

#Data for fertility process (only at X0)
#Parameters: kids. last one is the constant
x_k=x_df[ ['age_ra', 'age_ra2', 'constant']   ].values
kidsp_betas=pd.read_csv("/home/jrodriguez/NH_HC/results/kids_process/betas_kids_v2.csv").values


#Minimum set of x's (for interpolation)
x_wmk=x_df[  ['age_ra','age_ra2', 'd_HS2', 'constant'] ].values

#Data for treatment status
passign=x_df[ ['d_RA']   ].values

#The EITC parameters
eitc_list = pickle.load( open("/home/jrodriguez/NH_HC/codes/model_v2/simulate_sample/eitc_list.p", 'rb' ) )

#The AFDC parameters
afdc_list = pickle.load( open("/home/jrodriguez/NH_HC/codes/model_v2/simulate_sample/afdc_list.p", 'rb' ) )

#The SNAP parameters
snap_list = pickle.load( open("/home/jrodriguez/NH_HC/codes/model_v2/simulate_sample/snap_list.p", 'rb' ) ) 

#CPI index
cpi =  pickle.load( open("/home/jrodriguez/NH_HC/codes/model_v2/simulate_sample/fpl_list.p", 'rb' ) )

#Federal Poverty Lines
fpl_list = pickle.load( open("/home/jrodriguez/NH_HC/codes/model_v2/simulate_sample/fpl_list.p", 'rb' ) ) 

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
agech0=x_df[['age_t0']].values


#Defines the instance with parameters
param0 = util.Parameters(alphap,alphaf,mu_c,
	eta,gamma1,gamma2,gamma3,
	tfp,sigma2theta,rho_theta_epsilon,wagep_betas,
	income_male_betas,c_emp_spouse,
	marriagep_betas, kidsp_betas, eitc_list,
	afdc_list,snap_list,cpi,fpl_list,
	lambdas,kappas,pafdc,psnap,mup,sigma_z)


#Creating a grid for the emax computation
dict_grid=gridemax.grid()

#How many hours is part- and full-time work
hours_p = 15
hours_f = 40

hours = np.zeros(N)
childcare = np.zeros(N)
wr,cs,ws=1,1,1

#This is an arbitrary initialization of Utility class
model = util.Utility(param0,N,x_w,x_m,x_k,passign,nkids0,married0,hours,childcare,
	agech0,hours_p,hours_f,wr,cs,ws)

tracemalloc.start()

##############Computing EmaxT#####################
print ('')
print ('')
print ('Getting a dictionary of emax')
start_time = time.time()
print ('')
print ('')

D=20
np.random.seed(2)
emax_function_in=emax.Emaxt(param0,D,dict_grid,hours_p,hours_f,
	wr,cs,ws,model)
emax_dic=emax_function_in.recursive() #8 emax (t=1 to t=8)


time_emax=time.time() - start_time
print ('')
print ('')
print ('Done with procedure in:')
print("--- %s seconds ---" % (time_emax))
print ('')
print ('')




#########Simulating data###############
print ('')
print ('')
print ('Simulating fake data')
start_time = time.time()
print ('')
print ('')


sim_ins=simdata.SimData(N,param0,emax_dic,x_w,x_m,x_k,x_wmk,passign,nkids0,married0,
	agech0,hours_p,hours_f,wr,cs,ws,model)

data_dic=sim_ins.fake_data(8)


time_sim=time.time() - start_time
print ('')
print ('')
print ('Done with procedure in:')
print("--- %s seconds ---" % (time_sim))
print ('')
print ('')

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

print("[ Top 10 ]")
for stat in top_stats[:10]:
    print(stat)

#warning: for individuals with children over 18 yo, the problem is not well defined.
#look only until t=8 years after RA
ct=data_dic['Consumption']
income=data_dic['Income']
nh_sup=data_dic['nh_matrix']
nh_cc=data_dic['cs_cost_matrix']
theta_t=data_dic['Theta']
cc_t=data_dic['Childcare']
hours_t=data_dic['Hours']
wage_t=data_dic['Wage']
kids=data_dic['Kids']
marr=data_dic['Marriage']
income=data_dic['Income']
spouse_income=data_dic['Spouse_income']
spouse_employment=data_dic['Spouse_employment_matrix']

#spouse income
np.mean(spouse_income,axis=0)
np.mean(spouse_employment,axis=0)

#Expenditures
np.count_nonzero(nh_sup[:,0])
np.count_nonzero(nh_cc[:,0])
np.sum(nh_sup,axis=0)
np.sum(nh_cc,axis=0)


np.count_nonzero(passign)
np.mean(nh_cc[nh_cc>0],axis=0)

#log theta in SD units
ltheta = np.log(theta_t)
np.mean(ltheta,axis=0)
np.std(ltheta,axis=0)

np.mean(cc_t,axis=0)


#Impact of NH on logtheta (SD units) and child care in time
ate_theta=np.mean(ltheta[passign[:,0]==1,:],axis=0) - np.mean(ltheta[passign[:,0]==0,:],axis=0)

ate_theta/np.std(ltheta,axis=0)

#need to adjust for age (age_long)
ate_cc=np.mean(cc_t[passign[:,0]==1,:],axis=0) - np.mean(cc_t[passign[:,0]==0,:],axis=0)


#Impact on income
np.mean(income,axis=0)
ate_income=np.mean(income[passign[:,0]==1,:],axis=0) - np.mean(income[passign[:,0]==0,:],axis=0)
ate_ct=np.mean(ct[passign[:,0]==1,:],axis=0) - np.mean(ct[passign[:,0]==0,:],axis=0)

np.mean(np.mean(ct[passign[:,0]==0,:],axis=0))

#Labor supply
unemp_t=hours_t==0
part_t=hours_t==hours_p
full_t=hours_t==hours_f

ate_hours = np.mean(hours_t[passign[:,0]==1,:],axis=0) - np.mean(hours_t[passign[:,0]==0,:],axis=0)


np.mean(unemp_t,axis=0)
np.mean(full_t,axis=0)
np.mean(part_t,axis=0)


np.mean(wage_t[unemp_t[:,0]==0,0])

gross = wage_t*hours_t*52
np.mean(gross[unemp_t[:,0]==0,0])
np.mean(wage_t[(part_t[:,0]==1) & (passign[:,0]==1),0],axis=0)
np.mean(gross[(part_t[:,0]==1) & (passign[:,0]==1),0],axis=0)
np.mean(income[(unemp_t[:,0]==1) & (passign[:,0]==1),0],axis=0)

ate_income_all=np.mean(income[passign[:,0]==1,0],axis=0) - np.mean(income[passign[:,0]==0,0],axis=0)
ate_income_ft=np.mean(income[(full_t[:,0]==1) & (passign[:,0]==1),0],axis=0) - np.mean(income[(full_t[:,0]==1) & (passign[:,0]==0),0],axis=0)
ate_income_pt=np.mean(income[(part_t[:,0]==1) & (passign[:,0]==1),0],axis=0) - np.mean(income[(part_t[:,0]==1) & (passign[:,0]==0),0],axis=0)
ate_income_un=np.mean(income[(unemp_t[:,0]==1) & (passign[:,0]==1),0],axis=0) - np.mean(income[(unemp_t[:,0]==1) & (passign[:,0]==0),0],axis=0)

#ATE on employment
ate_unem=np.mean(unemp_t[passign[:,0]==1,:],axis=0) - np.mean(unemp_t[passign[:,0]==0,:],axis=0)
ate_part=np.mean(part_t[passign[:,0]==1,:],axis=0) - np.mean(part_t[passign[:,0]==0,:],axis=0)
ate_full=np.mean(full_t[passign[:,0]==1,:],axis=0) - np.mean(full_t[passign[:,0]==0,:],axis=0)

