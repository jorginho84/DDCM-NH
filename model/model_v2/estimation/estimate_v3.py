"""
This class takes an initial set of parameters and actual data and estimates
the parameters of the structural model via General Indirect Inference.

"""
from __future__ import division #omit for python 3.x
import numpy as np
import pandas as pd
from numba import jit
import sys, os
from scipy import stats
from scipy.optimize import minimize
from scipy.optimize import fmin_bfgs
from pathos.multiprocessing import ProcessPool
sys.path.append("/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample")
import utility as util
import gridemax
import time
import int_linear
import emax as emax
import simdata as simdata


class Estimate:
	def __init__(self,param0,x_w,x_m,x_k,x_wmk,passign,agech0,theta0,
		nkids0,married0,D,dict_grid,M,N,moments_vector,w_matrix,hours_p,hours_f,
		wr,cs,ws):

		self.param0=param0
		self.x_w,self.x_m,self.x_k,self.x_wmk=x_w,x_m,x_k,x_wmk
		self.passign,self.theta0,self.nkids0,self.married0=passign,theta0,nkids0,married0
		self.D,self.dict_grid =D,dict_grid
		self.agech0=agech0
		self.M,self.N=M,N
		self.moments_vector,self.w_matrix=moments_vector,w_matrix
		self.hours_p,self.hours_f=hours_p,hours_f
		self.wr,self.cs,self.ws=wr,cs,ws

	def emax(self,param1,model):
		"""
		Takes given betas and estimates the emax function (en emax_dic)

		"""
		#updating with new betas
		np.random.seed(1) #always the same emax, for a given set of beta
		emax_ins_1=emax.Emaxt(param1,self.D,self.dict_grid,self.hours_p,
			self.hours_f,self.wr,self.cs,self.ws,model)
		return emax_ins_1.recursive(8) #t=1 to t=8

	def samples(self,param1,emaxins,model):
		"""
		Returns a sample M of utility values
		"""

		#number of choices
		J=6

		#updating sample with new betas and emax
		simdata_ins= simdata.SimData(self.N,param1,emaxins,
			self.x_w,self.x_m,self.x_k,self.x_wmk,self.passign,self.theta0,
			self.nkids0,self.married0,self.agech0,self.hours_p,self.hours_f,
			self.wr,self.cs,self.ws,model)

		#save here
		util_list=[]
		income_matrix=np.zeros((self.N,9,self.M))
		consumption_matrix=np.zeros((self.N,9,self.M))
		choice_matrix=np.zeros((self.N,9,self.M))
		utils_periodt=np.zeros((self.N,J,9,self.M))
		utils_c_periodt=np.zeros((self.N,J,9,self.M))
		theta_matrix=np.zeros((self.N,9,self.M))
		wage_matrix=np.zeros((self.N,9,self.M))
		hours_matrix=np.zeros((self.N,9,self.M))
		ssrs_t2_matrix=np.zeros((self.N,self.M))
		ssrs_t5_matrix=np.zeros((self.N,self.M))

		#Computing samples (in paralel)
		def sample_gen(j):
			np.random.seed(j+100)
			return simdata_ins.fake_data(9)

		pool = ProcessPool(nodes=15)
		dics = pool.map(sample_gen,range(self.M))
		
		
    	#Saving results		
		for j in range(0,self.M):
			income_matrix[:,:,j]=dics[j]['Income']
			consumption_matrix[:,:,j]=dics[j]['Consumption']
			choice_matrix[:,:,j]=dics[j]['Choices']
			theta_matrix[:,:,j]=dics[j]['Theta']
			wage_matrix[:,:,j]=dics[j]['Wage']
			hours_matrix[:,:,j]=dics[j]['Hours']
			ssrs_t2_matrix[:,j]=dics[j]['SSRS_t2']
			ssrs_t5_matrix[:,j]=dics[j]['SSRS_t5']
			ssrs_t5_matrix[:,j]=dics[j]['SSRS_t5']
			

			for periodt in range(0,9):
				utils_periodt[:,:,periodt,j]=dics[j]['Uti_values_dic'][periodt]
				utils_c_periodt[:,:,periodt,j]=dics[j]['Uti_values_c_dic'][periodt]

		return {'utils_periodt': utils_periodt,'utils_c_periodt': utils_c_periodt,
				'income_matrix':income_matrix,
				'choice_matrix': choice_matrix,'theta_matrix': theta_matrix,
				'wage_matrix': wage_matrix,'consumption_matrix':consumption_matrix,
				'hours_matrix': hours_matrix, 'ssrs_t2_matrix':ssrs_t2_matrix,
				'ssrs_t5_matrix':ssrs_t5_matrix }

	def aux_model(self,choices):
		"""
		Computes the auxiliary estimates from simulated data
		"""

		#number of choices
		J=6
		J_1=3 #3 hours categories
		nperiods=9
		age_child=np.zeros((self.N,nperiods)) #age of child every period
		for x in range(0,nperiods):
			age_child[:,x]=np.reshape(self.agech0,self.N)+x

		##Obtaining Auxiliary estimate for every m##
		choice_matrix=choices['choice_matrix'].copy()

		############################################################
		####Aux to identify utility function########################
		############################################################

		#child care at period t=0,1 and 4
		choices_aux=np.concatenate((choice_matrix[:,1,:], 
			choice_matrix[:,4,:]),axis=0) #t=1,4
		age_aux=np.concatenate((age_child[:,1],age_child[:,4]),axis=0)
		passign_aux=np.concatenate((self.passign[:,0],self.passign[:,0]),axis=0)
		cc_logit=choices_aux>=3
		boo=(age_aux<=6) & (passign_aux==0)
		beta_childcare=np.mean(cc_logit[boo,:],axis=0) #beta for every m


		#unemployment at period t=0,1 and 4
		choices_aux=np.concatenate((choice_matrix[:,0,:],choice_matrix[:,1,:], 
			choice_matrix[:,4,:]),axis=0) #t=1,4
		age_aux=np.concatenate((age_child[:,0],age_child[:,1],age_child[:,4]),axis=0)
		passign_aux=np.concatenate((self.passign[:,0],self.passign[:,0],self.passign[:,0]),axis=0)
		cc_logit=(choices_aux==0) | (choices_aux==3)
		boo=(age_aux<=6) & (passign_aux==0)
		beta_hours1=np.mean(cc_logit[boo,:],axis=0) #beta for every m
				

		#mean hours at t=0,1,4 and 7
		choices_aux=np.concatenate((choice_matrix[:,0,:],choice_matrix[:,1,:],
			choice_matrix[:,4,:],choice_matrix[:,7,:]),axis=0)
		passign_aux=np.concatenate((self.passign[:,0],self.passign[:,0],
			self.passign[:,0],self.passign[:,0]),axis=0)
		age_aux=np.concatenate((age_child[:,0],age_child[:,1],age_child[:,4],
			age_child[:,7]),axis=0)
		hours_aux_2=(choices_aux==1) | (choices_aux==4)
		hours_aux_3=(choices_aux==2) | (choices_aux==5)
		boo_h=(passign_aux==0) & (age_aux>6)
		beta_hours2=np.mean(hours_aux_2[boo_h,:],axis=0)
		beta_hours3=np.mean(hours_aux_3[boo_h,:],axis=0)

		############################################################
		####Aux to identify wage process############################
		############################################################

		wage_matrix=choices['wage_matrix'].copy()
		wage_aux=np.log(np.concatenate((wage_matrix[:,0,:],wage_matrix[:,1,:],
		wage_matrix[:,4,:],wage_matrix[:,7,:]),axis=0)) #to panel and logs

		age_t0=self.x_w[:,0]
		age=np.zeros((self.N,9))
		for t in range(9):
			age[:,t]=age_t0+t
		
		age_aux=np.reshape(np.concatenate((age[:,0],age[:,1],age[:,4],age[:,7]),axis=0),(self.N*4,1))
		age2_aux=np.square(age_aux)

		period0=np.log(np.zeros(self.N) + 1)
		period1=np.log(np.zeros(self.N) + 2)
		period4=np.log(np.zeros(self.N) + 5)
		period7=np.log(np.zeros(self.N) + 8)
		lt = np.reshape(np.concatenate((period0,period1,period4,period7),axis=0),(self.N*4,1))

		dhs_aux=np.reshape(np.concatenate((self.x_w[:,1],self.x_w[:,1],self.x_w[:,1],self.x_w[:,1]),axis=0),(self.N*4,1))
		choices_aux=np.concatenate((choice_matrix[:,0,:],choice_matrix[:,1,:],
			choice_matrix[:,4,:],choice_matrix[:,7,:]),axis=0)
		boo_work=(choices_aux==1) | (choices_aux==2) | (choices_aux==4) | (choices_aux==5)
		
		beta_w=np.zeros((5,self.M)) #5 parameters
		sigma_w=np.zeros((1,self.M))
		const=np.ones((self.N*4,1)) #4 periods:0,1,4,7
		for j in range(self.M):
			xw_aux=np.concatenate((age_aux[boo_work[:,j]==1,:],
				age2_aux[boo_work[:,j]==1,:],
				dhs_aux[boo_work[:,j]==1,:],
				lt[boo_work[:,j]==1,:],
				const[boo_work[:,j]==1,:]),axis=1)

			#If nonsingular matrix
			if np.linalg.cond(np.dot(np.transpose(xw_aux),
					xw_aux)) < 1/sys.float_info.epsilon:
				xx_inv=np.linalg.inv(np.dot(np.transpose(xw_aux),xw_aux))
				xy=np.dot(np.transpose(xw_aux),wage_aux[boo_work[:,j],j])
				beta_w[:,j]=np.dot(xx_inv,xy)
				e=wage_aux[boo_work[:,j],j]-np.dot(xw_aux,beta_w[:,j])
				sigma_w[:,j]=np.sum(np.square(e))/(wage_aux[boo_work[:,j],j].shape[0] 
					- beta_w[:,j].shape[0])
			else:
				print 'disregarding m sample: singular matrix in wage process estimation'
				pass
		beta_wagep=np.concatenate((beta_w,sigma_w),axis=0)

		
		############################################################
		###Aux estimate to identify prod function###################
		############################################################

		ssrs_t2_matrix=choices['ssrs_t2_matrix'].copy()
		ssrs_t5_matrix=choices['ssrs_t5_matrix'].copy()
		
		consumption_matrix=choices['consumption_matrix'].copy()
		lconsumption_matrix=np.log(consumption_matrix) - np.mean(np.log(consumption_matrix),axis=0)
				
		#we already have age_child_p
		hours_matrix=choices['hours_matrix'].copy()
		leisure_matrix=148-hours_matrix
		lleisure_matrix=np.log(leisure_matrix) - np.mean(np.log(leisure_matrix),axis=0)

		beta_kappas_t2=np.zeros((4,self.M)) #4 moments
		beta_inputs_old=np.zeros((2,self.M)) # 2 moments
		beta_inputs_young_cc1=np.zeros((3,self.M)) #3 moments
		beta_kappas_t5=np.zeros((4,self.M)) #4 moments
				
		for z in range(2,6): #4 rankings
			boo=ssrs_t2_matrix==z
			beta_kappas_t2[z-2,:]=np.mean(boo,axis=0)

			
		boo_old=age_child[:,4]>6 #older than 6 at t=4
		boo_young=age_child[:,1]<=6 #less than 6 at t=1


		for j in range(self.M):
			boo_ssrs2=(ssrs_t2_matrix[:,j]>=3) & (boo_old)
			beta_inputs_old[0,j] = np.corrcoef(lconsumption_matrix[boo_old,4,j],ssrs_t5_matrix[boo_old,j])[1,0]
			beta_inputs_old[1,j] = np.corrcoef(lleisure_matrix[boo_old,4,j],ssrs_t5_matrix[boo_old,j])[1,0]
			
			b_cc0=choice_matrix[:,1,j]<3 #child care choice=0 at t=1
			b_cc1=choice_matrix[:,1,j]>=3 #child care choice=1 at t=1
			boo_young_cc0 = (boo_young==True) & (b_cc0==True)
			boo_young_cc1 = (boo_young==True) & (b_cc1==True)
			beta_inputs_young_cc1[0,j] = np.corrcoef(lconsumption_matrix[boo_young,1,j],ssrs_t2_matrix[boo_young,j])[1,0]
			beta_inputs_young_cc1[1,j] = np.corrcoef(lleisure_matrix[boo_young,1,j],ssrs_t2_matrix[boo_young,j])[1,0]
			beta_inputs_young_cc1[2,j] = np.mean(ssrs_t2_matrix[boo_young_cc1,j]) - np.mean(ssrs_t2_matrix[boo_young_cc0,j])

		
		for z in range(2,6): #4 rankings
			boo=ssrs_t5_matrix==z
			beta_kappas_t5[z-2,:]=np.mean(boo,axis=0)
		
		
		return{'beta_childcare':beta_childcare,'beta_hours1': beta_hours1,
		'beta_hours2':beta_hours2,'beta_hours3':beta_hours3,'beta_wagep': beta_wagep, 
		'beta_kappas_t2': beta_kappas_t2,'beta_inputs_old':beta_inputs_old,
		'beta_inputs_young_cc1':beta_inputs_young_cc1,'beta_kappas_t5':beta_kappas_t5		}
	
	
	def ll(self,beta):
		"""
		Takes structural parameters and computes the objective function for optimization 
		
		"""
		start_time = time.time()
		print ''
		print ''
		print 'Beginning sample generator'

		def sym(a):
			return ((1/(1+np.exp(-a))) - 0.5)*2

		#updating beta->parameters instance to compute likelihood.
		self.param0.eta=beta[0]
		self.param0.alphap=beta[1]
		self.param0.alphaf=beta[2]
		self.param0.alpha_cc=beta[3]
		self.param0.betaw[0]=beta[4]
		self.param0.betaw[1]=beta[5]
		self.param0.betaw[2]=beta[6]
		self.param0.betaw[3]=beta[7]
		self.param0.betaw[4]=beta[8]
		self.param0.betaw[5]=np.exp(beta[9])
		self.param0.gamma1[0]=sym(beta[10])
		self.param0.gamma2[0]=sym(beta[11])
		self.param0.gamma1[1]=sym(beta[12])
		self.param0.gamma2[1]=sym(beta[13])
		self.param0.tfp=beta[14]
		self.param0.kappas[0][0]=beta[15]
		self.param0.kappas[0][1]=beta[16]
		self.param0.kappas[0][2]=beta[17]
		self.param0.kappas[0][3]=beta[18]
		self.param0.kappas[1][0]=beta[19]
		self.param0.kappas[1][1]=beta[20]
		self.param0.kappas[1][2]=beta[21]
		self.param0.kappas[1][3]=beta[22]
			

		#The model (utility instance)
		hours = np.zeros(self.N)
		childcare  = np.zeros(self.N)

		model  = util.Utility(self.param0,self.N,self.x_w,self.x_m,self.x_k,self.passign,
			self.theta0,self.nkids0,self.married0,hours,childcare,
			self.agech0,self.hours_p,self.hours_f,self.wr,self.cs,self.ws)

		##obtaining emax instance##
		emax_instance=self.emax(self.param0,model)
		
		##obtaining samples##

		choices=self.samples(self.param0,emax_instance,model)

		###########################################################################
		##Getting the betas of the auxiliary model#################################
		###########################################################################
		dic_betas=self.aux_model(choices)

		time_opt=time.time() - start_time
		print ''
		print ''
		print 'Done sample generation in'
		print("--- %s seconds ---" % (time_opt))
		print ''
		print ''
		start_time = time.time()
		print 'Beginning aux model generator'


		#utility_aux
		beta_childcare=np.mean(dic_betas['beta_childcare'],axis=0) #1x1
		beta_hours1=np.mean(dic_betas['beta_hours1'],axis=0) #1x1
		beta_hours2=np.mean(dic_betas['beta_hours2'],axis=0) #1x1
		beta_hours3=np.mean(dic_betas['beta_hours3'],axis=0) #1x1
		beta_wagep=np.mean(dic_betas['beta_wagep'],axis=1) # 5 x 1
		beta_kappas_t2=np.mean(dic_betas['beta_kappas_t2'],axis=1) #4 x 1
		beta_kappas_t5=np.mean(dic_betas['beta_kappas_t5'],axis=1) #4 x 1
		beta_inputs_old=np.mean(dic_betas['beta_inputs_old'],axis=1) #2 x 1
		beta_inputs_young_cc1=np.mean(dic_betas['beta_inputs_young_cc1'],axis=1) #3 x 1

			

		###########################################################################
		####Forming the likelihood#################################################
		###########################################################################

		#Number of moments to match
		num_par=beta_childcare.size + beta_hours1.size + beta_hours2.size + beta_hours3.size + beta_wagep.size + beta_kappas_t2.size +  beta_kappas_t5.size + beta_inputs_old.size + beta_inputs_young_cc1.size
		
		#Outer matrix
		x_vector=np.zeros((num_par,1))

		
		x_vector[0:beta_childcare.size,0]=beta_childcare - self.moments_vector[0,0]
		
		ind=beta_childcare.size
		x_vector[ind:ind+beta_hours1.size,0]=beta_hours1 - self.moments_vector[ind,0]

		ind = ind + beta_hours1.size
		x_vector[ind:ind+beta_hours2.size,0]=beta_hours2 - self.moments_vector[ind,0]
		
		ind=ind + beta_hours2.size
		x_vector[ind:ind + beta_hours3.size,0]=beta_hours3 - self.moments_vector[ind,0]
		
		ind = ind + beta_hours3.size
		x_vector[ind: ind+ beta_wagep.size,0]=beta_wagep - self.moments_vector[ind:ind+ beta_wagep.size,0]
		
		ind = ind + beta_wagep.size
		x_vector[ind:ind + beta_kappas_t2.size,0]=beta_kappas_t2 - self.moments_vector[ind:ind + beta_kappas_t2.size,0]

		ind = ind + beta_kappas_t2.size
		x_vector[ind: ind + beta_kappas_t5.size,0] = beta_kappas_t5 - self.moments_vector[ind: ind + beta_kappas_t5.size,0]
		
		ind = ind + beta_kappas_t5.size
		x_vector[ind:ind + beta_inputs_old.size,0] = beta_inputs_old - self.moments_vector[ind:ind + beta_inputs_old.size,0]
		
		ind = ind + beta_inputs_old.size
		x_vector[ind: ind + beta_inputs_young_cc1.size,0] = beta_inputs_young_cc1 - self.moments_vector[ind: ind + beta_inputs_young_cc1.size,0]
		
		
		
		#The Q metric
		q_w=np.dot(np.dot(np.transpose(x_vector),np.linalg.inv(self.w_matrix)),x_vector)
		print ''
		print 'The objetive function value equals ', q_w
		print ''

		time_opt=time.time() - start_time
		print 'Done aux model generation in'
		print("--- %s seconds ---" % (time_opt))

		return q_w



	def optimizer(self):
		
		
		#symmetric interval constraint
		def syminv(g):
			out = -np.log((2/(g+1)) - 1)
			return out
		
				
		beta0=np.array([self.param0.eta,self.param0.alphap,self.param0.alphaf,
			self.param0.alpha_cc,self.param0.betaw[0],self.param0.betaw[1],
			self.param0.betaw[2],self.param0.betaw[3],self.param0.betaw[4],
			np.log(self.param0.betaw[5]),
			syminv(self.param0.gamma1[0]),syminv(self.param0.gamma2[0]),
			syminv(self.param0.gamma1[1]),syminv(self.param0.gamma2[1]),
			self.param0.tfp,
			self.param0.kappas[0][0],self.param0.kappas[0][1],#kappa: t=2, m0
			self.param0.kappas[0][2],self.param0.kappas[0][3], #kappa: t=2, m0
			self.param0.kappas[1][0],self.param0.kappas[1][1],#kappa: t=5, m0
			self.param0.kappas[1][2],self.param0.kappas[1][3], #kappa: t=5, m0
			]) 

		
		#Here we go
		opt = minimize(self.ll, beta0,  method='Nelder-Mead', options={'maxiter':2000, 'maxfev': 90000, 'ftol': 1e-1, 'disp': True});
		
		return opt



