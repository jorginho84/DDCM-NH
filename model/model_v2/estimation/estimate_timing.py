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
		nkids0,married0,D,dict_grid,M,N,betas_dic,sigma_dic):

		self.param0=param0
		self.x_w,self.x_m,self.x_k,self.x_wmk=x_w,x_m,x_k,x_wmk
		self.passign,self.theta0,self.nkids0,self.married0=passign,theta0,nkids0,married0
		self.D,self.dict_grid =D,dict_grid
		self.agech0=agech0
		self.M,self.N=M,N
		self.betas_dic,self.sigma_dic=betas_dic,sigma_dic

	def emax(self,param1):
		"""
		Takes given betas and estimates the emax function (en emax_dic)

		"""
		#updating with new betas
		emax_ins_1=emax.Emaxt(param1,self.D,self.dict_grid)
		return emax_ins_1.recursive(8) #t=1 to t=8

	def samples(self,param1,emaxins):
		"""
		Returns a sample M of utility values
		"""

		#number of choices
		J=6

		#updating sample with new betas and emax
		simdata_ins= simdata.SimData(self.N,param1,emaxins,
			self.x_w,self.x_m,self.x_k,self.x_wmk,self.passign,self.theta0,
			self.nkids0,self.married0,self.agech0)

		#save here
		util_list=[]
		income_matrix=np.zeros((self.N,9,self.M))
		consumption_matrix=np.zeros((self.N,9,self.M))
		choice_matrix=np.zeros((self.N,9,self.M))
		utils_periodt=np.zeros((self.N,J,9,self.M))
		theta_matrix=np.zeros((self.N,9,self.M))
		wage_matrix=np.zeros((self.N,9,self.M))
		hours_matrix=np.zeros((self.N,9,self.M))
		ssrs_t2_matrix=np.zeros((self.N,3,self.M))
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
			ssrs_t2_matrix[:,:,j]=dics[j]['SSRS_t2']
			ssrs_t5_matrix[:,j]=dics[j]['SSRS_t5']
			

			for periodt in range(0,9):
				utils_periodt[:,:,periodt,j]=dics[j]['Uti_values_dic'][periodt]

		return {'utils_periodt': utils_periodt,'income_matrix':income_matrix,
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

		#child care at period t=1 and 4
		choices_aux=np.concatenate((choice_matrix[:,1,:], 
			choice_matrix[:,4,:]),axis=0) #t=1,4
		age_aux=np.concatenate((age_child[:,1],age_child[:,4]),axis=0)
		passign_aux=np.concatenate((self.passign[:,0],self.passign[:,0]),axis=0)
		cc_logit=choices_aux>=3
		boo=(age_aux<=5) & (passign_aux==0)
		beta_childcare=np.mean(cc_logit[boo,:],axis=0) #beta for every m
		
		#mean hours at t=0,1,4 and 7
		choices_aux=np.concatenate((choice_matrix[:,0,:],choice_matrix[:,1,:], 
			choice_matrix[:,4,:],choice_matrix[:,7,:]),axis=0)
		passign_aux=np.concatenate((self.passign[:,0],self.passign[:,0],self.passign[:,0],
			self.passign[:,0]),axis=0)
		hours_aux_2=(choices_aux==1) | (choices_aux==4)
		hours_aux_3=(choices_aux==2) | (choices_aux==5)
		boo_h=(passign_aux==0)
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

		dhs_aux=np.reshape(np.concatenate((self.x_w[:,1],self.x_w[:,1],self.x_w[:,1],self.x_w[:,1]),axis=0),(self.N*4,1))

		boo_work=(choices_aux==1) | (choices_aux==2) | (choices_aux==4) | (choices_aux==5)
		
		beta_w=np.zeros((4,self.M))
		sigma_w=np.zeros((1,self.M))
		const=np.ones((self.N*4,1)) #4 periods:0,1,4,7
		for j in range(self.M):
			xw_aux=np.concatenate((age_aux[boo_work[:,j]==1,:],
				age2_aux[boo_work[:,j]==1,:],
				dhs_aux[boo_work[:,j]==1,:],
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

		beta_kappas_t2=np.zeros((4,3,self.M)) #4 moments
		beta_lambdas_t2=np.zeros((2,self.M)) # 2 moments
		beta_inputs_old=np.zeros((3,self.M)) # 3 moments
		beta_inputs_young_cc0=np.zeros((3,self.M)) #3 moments
		beta_inputs_young_cc1=np.zeros((3,self.M)) #3 moments
		beta_kappas_t5=np.zeros((4,self.M)) #4 moments
		beta_lambdas_t5=np.zeros((1,self.M)) #1 moment
		
		for z in range(2,6): #4 rankings
			boo=ssrs_t2_matrix==z
			beta_kappas_t2[z-2,:,:]=np.mean(boo,axis=0)

		m1=ssrs_t2_matrix[:,0,:].copy()
		m2=ssrs_t2_matrix[:,1,:].copy()
		m3=ssrs_t2_matrix[:,2,:].copy()

		for j in range(self.M):
			boo_5=m2[:,j]==5
			boo_4=m2[:,j]==4
			boo_m1=m1[:,j]==5
			beta_lambdas_t2[0,j]=np.mean(boo_m1[boo_5]) - np.mean(boo_m1[boo_4])
			
			boo_5=m3[:,j]==5
			boo_4=m3[:,j]==4
			boo_m2=m2[:,j]==5
			beta_lambdas_t2[1,j]=np.mean(boo_m2[boo_5]) - np.mean(boo_m2[boo_4])

		boo_old=age_child[:,4]>5 #older than 5 at t=4
		boo_young=age_child[:,1]<=5 #less than 5 at t=1


		for j in range(self.M):
			boo_4=(ssrs_t5_matrix[:,j]>=3) & (boo_old)
			boo_2=(ssrs_t5_matrix[:,j]<3) & (boo_old)
			boo_ssrs2=(m1[:,j]>=3) & (boo_old)
			beta_inputs_old[0,j] = np.mean(lconsumption_matrix[boo_4,4,j]) - np.mean(lconsumption_matrix[boo_2,4,j])
			beta_inputs_old[1,j] = np.mean(lleisure_matrix[boo_4,4,j]) - np.mean(lleisure_matrix[boo_2,4,j])
			beta_inputs_old[2,j] = np.mean(boo_4[boo_ssrs2]) 
			
			b_cc0=choice_matrix[:,1,j]<3 #child care choice=0 at t=1
			
			boo_4=(m1[:,j]>=3) & (boo_young==True) & (b_cc0==True)
			boo_2=(m1[:,j]<3) & (boo_young==True) & (b_cc0==True)
			boo_ssrs5=(ssrs_t5_matrix[:,j]>=3) & (boo_young==True) & (b_cc0==True)
			beta_inputs_young_cc0[0,j] = np.mean(lconsumption_matrix[boo_4,1,j]) - np.mean(lconsumption_matrix[boo_2,1,j])
			beta_inputs_young_cc0[1,j] = np.mean(lleisure_matrix[boo_4,1,j]) - np.mean(lleisure_matrix[boo_2,1,j])
			beta_inputs_young_cc0[2,j] = np.mean(boo_ssrs5[boo_4])

			b_cc1=choice_matrix[:,1,j]>=3 #child care choice=1 at t=1
			boo_4=(m1[:,j]>=3) & (boo_young==True) & (b_cc1==True)
			boo_2=(m1[:,j]<3) & (boo_young==True) & (b_cc1==True)
			boo_ssrs5=(ssrs_t5_matrix[:,j]>=3) & (boo_young==True) & (b_cc1==True)
			beta_inputs_young_cc1[0,j] = np.mean(lconsumption_matrix[boo_4,1,j]) - np.mean(lconsumption_matrix[boo_2,1,j])
			beta_inputs_young_cc1[1,j] = np.mean(lleisure_matrix[boo_4,1,j]) - np.mean(lleisure_matrix[boo_2,1,j])
			beta_inputs_young_cc1[2,j] = np.mean(boo_ssrs5[boo_4])

		
		for z in range(2,6): #4 rankings
			boo=ssrs_t5_matrix==z
			beta_kappas_t5[z-2,:]=np.mean(boo,axis=0)
		
		for j in range(self.M):
			boo_t2_5=ssrs_t2_matrix[:,0,j]==5
			boo_t2_4=ssrs_t2_matrix[:,0,j]==4
			boo_t5=ssrs_t5_matrix[:,j]==5
			beta_lambdas_t5[0,j] = np.mean(boo_t5[boo_t2_5]) - np.mean(boo_t5[boo_t2_4])

		return{'beta_childcare':beta_childcare,'beta_hours2':beta_hours2,
		'beta_hours3':beta_hours3,'beta_wagep': beta_wagep, 'beta_kappas_t2': beta_kappas_t2,
		'beta_lambdas_t2':beta_lambdas_t2, 'beta_inputs_old':beta_inputs_old,
		'beta_inputs_young_cc0': beta_inputs_young_cc0, 
		'beta_inputs_young_cc1':beta_inputs_young_cc1,'beta_kappas_t5':beta_kappas_t5,
		'beta_lambdas_t5': beta_lambdas_t5}

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
		self.param0.betaw[0]=beta[3]
		self.param0.betaw[1]=beta[4]
		self.param0.betaw[2]=beta[5]
		self.param0.betaw[3]=beta[6]
		self.param0.betaw[4]=np.exp(beta[7])
		self.param0.gamma1[0][0]=sym(beta[8])
		self.param0.gamma2[0][0]=sym(beta[9])
		self.param0.gamma1[0][1]=sym(beta[10])
		self.param0.gamma2[0][1]=sym(beta[11])
		self.param0.gamma1[1]=sym(beta[12])
		self.param0.gamma2[1]=sym(beta[13])
		self.param0.kappas[0][0][0]=beta[14]
		self.param0.kappas[0][0][1]=beta[15]
		self.param0.kappas[0][0][2]=beta[16]
		self.param0.kappas[0][0][3]=beta[17]
		self.param0.kappas[0][1][0]=beta[18]
		self.param0.kappas[0][1][1]=beta[19]
		self.param0.kappas[0][1][2]=beta[20]
		self.param0.kappas[0][1][3]=beta[21]
		self.param0.kappas[0][2][0]=beta[22]
		self.param0.kappas[0][2][1]=beta[23]
		self.param0.kappas[0][2][2]=beta[24]
		self.param0.kappas[0][2][3]=beta[25]
		self.param0.kappas[1][0][0]=beta[26]
		self.param0.kappas[1][0][1]=beta[27]
		self.param0.kappas[1][0][2]=beta[28]
		self.param0.kappas[1][0][3]=beta[29]
		#First lambda = 1 (fixed)
		self.param0.lambdas[0][1]=beta[30]
		self.param0.lambdas[0][2]=beta[31]
		self.param0.lambdas[1][0]=beta[32]

		


		##obtaining emax instance##
		emax_instance=self.emax(self.param0)
		
		##obtaining samples##
		choices=self.samples(self.param0,emax_instance)

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
		beta_hours2=np.mean(dic_betas['beta_hours2'],axis=0) #1x1
		beta_hours3=np.mean(dic_betas['beta_hours3'],axis=0) #1x1
		beta_wagep=np.mean(dic_betas['beta_wagep'],axis=1) # 5 x 1
		beta_kappas_t2=np.mean(dic_betas['beta_kappas_t2'],axis=2) #4 x 3
		beta_lambdas_t2=np.mean(dic_betas['beta_lambdas_t2'],axis=1) #2 x 1
		beta_kappas_t5=np.mean(dic_betas['beta_kappas_t5'],axis=1) #4 x 1
		beta_lambdas_t5=np.mean(dic_betas['beta_lambdas_t5'],axis=1) #1 x 1
		beta_inputs_old=np.mean(dic_betas['beta_inputs_old'],axis=1) #3 x 1
		beta_inputs_young_cc0=np.mean(dic_betas['beta_inputs_young_cc0'],axis=1) #3 x 1
		beta_inputs_young_cc1=np.mean(dic_betas['beta_inputs_young_cc1'],axis=1) #3 x 1

		#Data equivalent
		beta_childcare_data=self.betas_dic['beta_cc']
		beta_hours2_data=self.betas_dic['beta_h2']
		beta_hours3_data=self.betas_dic['beta_h3']
		beta_wagep_data=self.betas_dic['beta_wage']
		beta_kappas_t2_data=self.betas_dic['beta_kappas_t2']
		beta_lambdas_t2_data=self.betas_dic['beta_lambdas_t2']
		beta_kappas_t5_data=self.betas_dic['beta_kappas_t5']
		beta_lambdas_t5_data=self.betas_dic['beta_lambdas_t5']
		beta_inputs_old_data=self.betas_dic['beta_inputs_old']
		beta_inputs_young_cc0_data=self.betas_dic['beta_inputs_young_cc0']
		beta_inputs_young_cc1_data=self.betas_dic['beta_inputs_young_cc1']

		#W matrix
		sigma_beta_cc=self.sigma_dic['sigma_beta_cc']
		sigma_beta_h2=self.sigma_dic['sigma_beta_h2']
		sigma_beta_h3=self.sigma_dic['sigma_beta_h3']
		sigma_beta_wage=self.sigma_dic['sigma_beta_wage']
		sigma_beta_kappas_t2=self.sigma_dic['sigma_beta_kappas_t2']
		sigma_beta_lambdas_t2=self.sigma_dic['sigma_beta_lambdas_t2']
		sigma_beta_kappas_t5=self.sigma_dic['sigma_beta_kappas_t5']
		sigma_beta_lambdas_t5=self.sigma_dic['sigma_beta_lambdas_t5']
		sigma_beta_inputs_old=self.sigma_dic['sigma_beta_inputs_old']
		sigma_beta_inputs_young_cc0=self.sigma_dic['sigma_beta_inputs_young_cc0']
		sigma_beta_inputs_young_cc1=self.sigma_dic['sigma_beta_inputs_young_cc1']


		###########################################################################
		####Forming the likelihood#################################################
		###########################################################################

		#Number of moments to match
		num_par=beta_childcare.size + beta_hours2.size + beta_hours3.size + beta_wagep.size + beta_kappas_t2.size + beta_lambdas_t2.size + beta_kappas_t5.size + beta_lambdas_t5.size +	beta_inputs_old.size + beta_inputs_young_cc0.size + beta_inputs_young_cc1.size
		
		#Weighting and outer matrix
		w_matrix=np.identity(num_par)
		x_vector=np.zeros((num_par,1))

		
		x_vector[0:beta_childcare.size,0]=beta_childcare - beta_childcare_data[:,0]
		w_matrix[0:beta_childcare.size,0:beta_childcare.size]=sigma_beta_cc

		ind=beta_childcare.size
		x_vector[ind:ind+beta_hours2.size,0]=beta_hours2 - beta_hours2_data[:,0]
		w_matrix[ind:ind+beta_hours2.size,ind:ind+beta_hours2.size]= sigma_beta_h2

		ind=ind + beta_hours2.size
		x_vector[ind:ind + beta_hours3.size,0]=beta_hours3 - beta_hours3_data[:,0]
		w_matrix[ind:ind + beta_hours3.size,ind:ind + beta_hours3.size]= sigma_beta_h3


		ind = ind + beta_hours3.size
		x_vector[ind: ind+ beta_wagep.size,0]=beta_wagep - beta_wagep_data[:,0]
		for k in range(beta_wagep.size):
			w_matrix[ind + k, ind + k] = sigma_beta_wage[k,0]
		
		ind = ind + beta_wagep.size
		for k in range(beta_kappas_t2.shape[1]):
			x_vector[ind:ind + beta_kappas_t2.shape[0],0]=beta_kappas_t2[:,k] - beta_kappas_t2_data[:,k]
			for j in range(beta_kappas_t2.shape[0]):
				w_matrix[ind + j, ind + j]=sigma_beta_kappas_t2[j,k]
			ind = ind + beta_kappas_t2.shape[0]

		x_vector[ind: ind + beta_lambdas_t2.size,0] = beta_lambdas_t2 - beta_lambdas_t2_data[:,0]
		for k in range(beta_lambdas_t2.size):
			w_matrix[ind + k, ind + k] = sigma_beta_lambdas_t2[k,0]

		ind = ind + beta_lambdas_t2.size
		x_vector[ind: ind + beta_kappas_t5.size,0] = beta_kappas_t5 - beta_kappas_t5_data[:,0]
		for k in range(beta_kappas_t5.size):
			w_matrix[ind + k, ind + k] = sigma_beta_kappas_t5[k,0]

		ind = ind + beta_kappas_t5.size
		x_vector[ind: ind + beta_lambdas_t5.size,0] = beta_lambdas_t5 - beta_lambdas_t5_data[:,0]
		w_matrix[ind: ind + beta_lambdas_t5.size,ind:ind + beta_lambdas_t5.size]

		ind = ind + beta_lambdas_t5.size
		x_vector[ind:ind + beta_inputs_old.size,0] = beta_inputs_old - beta_inputs_old_data[:,0]
		for k in range(beta_inputs_old.size):
			w_matrix[ind + k, ind + k]=sigma_beta_inputs_old[k,0]

		ind = ind + beta_inputs_old.size
		x_vector[ind: ind + beta_inputs_young_cc0.size,0] = beta_inputs_young_cc0 - beta_inputs_young_cc0_data[:,0]
		for k in range(beta_inputs_young_cc0.size):
			w_matrix[ind + k, ind + k]=sigma_beta_inputs_young_cc0[k,0]

		ind = ind + beta_inputs_young_cc0.size
		x_vector[ind: ind + beta_inputs_young_cc1.size,0] = beta_inputs_young_cc1 - beta_inputs_young_cc1_data[:,0]
		for k in range(beta_inputs_young_cc1.size):
			w_matrix[ind + k, ind + k]=sigma_beta_inputs_young_cc1[k,0]



		#The Q metric
		q_w=np.dot(np.dot(np.transpose(x_vector),np.linalg.inv(w_matrix)),x_vector)

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
			self.param0.betaw[0],self.param0.betaw[1],self.param0.betaw[2],
			self.param0.betaw[3],np.log(self.param0.betaw[4]),
			syminv(self.param0.gamma1[0][0]),syminv(self.param0.gamma2[0][0]),
			syminv(self.param0.gamma1[0][1]),syminv(self.param0.gamma2[0][1]),
			syminv(self.param0.gamma1[1]),syminv(self.param0.gamma2[1]),
			self.param0.kappas[0][0][0],self.param0.kappas[0][0][1], #kappa: t=2, m0
			self.param0.kappas[0][0][2],self.param0.kappas[0][0][3],#kappa: t=2, m0
			self.param0.kappas[0][1][0],self.param0.kappas[0][1][1],#kappa: t=2, m1
			self.param0.kappas[0][1][2],self.param0.kappas[0][1][3],#kappa: t=2, m1
			self.param0.kappas[0][2][0],self.param0.kappas[0][2][1],#kappa: t=2, m2
			self.param0.kappas[0][2][2],self.param0.kappas[0][2][3],#kappa: t=2, m2
			self.param0.kappas[1][0][0],self.param0.kappas[1][0][1],#kappa: t=5, m0
			self.param0.kappas[1][0][2],self.param0.kappas[1][0][3], #kappa: t=5, m0
			self.param0.lambdas[0][1], #lambda, t=0. first lambda_00=1 (fixed)
			self.param0.lambdas[0][2],#lambda, t=0
			self.param0.lambdas[1][0] #lambda t=1
			]) 

		
		#Here we go
		opt = minimize(self.ll, beta0,  method='Nelder-Mead', options={'maxiter':1000, 'maxfev': 90000, 'ftol': 1e-3, 'disp': True});
		
		return opt



