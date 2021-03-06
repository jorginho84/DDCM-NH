"""
This class takes an initial set of parameters and actual data and estimates
the parameters of the structural model via General Indirect Inference.

"""
#from __future__ import division #omit for python 3.x
import numpy as np
import pandas as pd
import gc
from numba import jit
import sys, os
from scipy import stats
from scipy.optimize import minimize
from scipy.optimize import fmin_bfgs
from pathos.multiprocessing import ProcessPool
sys.path.append("/home/jrodriguez/NH_HC/codes/model_v2/simulate_sample")
import utility as util
import gridemax
import time
import int_linear
import emax as emax
import simdata as simdata
import pybobyqa


class Estimate:
	def __init__(self,nperiods,param0,x_w,x_m,x_k,x_wmk,passign,agech0,
		nkids0,married0,D,dict_grid,M,N,moments_vector,
		w_matrix,hours_p,hours_f,
		wr,cs,ws):

		self.nperiods,self.param0=nperiods,param0
		self.x_w,self.x_m,self.x_k,self.x_wmk=x_w,x_m,x_k,x_wmk
		self.passign,self.nkids0,self.married0=passign,nkids0,married0
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
		#free up memory
		gc.collect()
		#updating with new betas
		np.random.seed(1) #always the same emax, for a given set of beta
		emax_ins_1=emax.Emaxt(param1,self.D,self.dict_grid,self.hours_p,
			self.hours_f,self.wr,self.cs,self.ws,model)
		return emax_ins_1.recursive() #t=1 to t=8

	def samples(self,param1,emaxins,model):
		"""
		Returns a sample M of utility values
		"""

		#number of choices
		J = 2*3

		#updating sample with new betas and emax
		simdata_ins= simdata.SimData(self.N,param1,emaxins,
			self.x_w,self.x_m,self.x_k,self.x_wmk,self.passign,
			self.nkids0,self.married0,self.agech0,
			self.hours_p,self.hours_f,
			self.wr,self.cs,self.ws,model)

		#save here
		util_list = []
		income_matrix = np.zeros((self.N,self.nperiods,self.M))
		consumption_matrix = np.zeros((self.N,self.nperiods,self.M))
		iscost_matrix = np.zeros((self.N,self.nperiods,self.M))
		cscost_matrix = np.zeros((self.N,self.nperiods,self.M))
		childcare_matrix = np.zeros((self.N,self.nperiods,self.M))
		theta_matrix = np.zeros((self.N,self.nperiods,self.M))
		wage_matrix = np.zeros((self.N,self.nperiods,self.M))
		spouse_income_matrix = np.zeros((self.N,self.nperiods,self.M))
		spouse_employment_matrix = np.zeros((self.N,self.nperiods,self.M))
		hours_matrix = np.zeros((self.N,self.nperiods,self.M))
		ssrs_t2_matrix = np.zeros((self.N,self.M))
		ssrs_t5_matrix = np.zeros((self.N,self.M))
		kids_matrix = np.zeros((self.N,self.nperiods,self.M))
		marr_matrix = np.zeros((self.N,self.nperiods,self.M))
		
		
		#Computing samples (in parallel)
		def sample_gen(j):
			np.random.seed(j+100)
			return simdata_ins.fake_data(self.nperiods)

		pool = ProcessPool(nodes = 10)
		dics = pool.map(sample_gen,range(self.M))
		pool.close()
		pool.join()
		pool.clear()
	#	dics = []
	#	for j in range(self.M):
	#		np.random.seed(j+100)
	#		dics.append(simdata_ins.fake_data(self.nperiods))


    	#Saving results		
		for j in range(0,self.M):
			income_matrix[:,:,j]=dics[j]['Income']
			consumption_matrix[:,:,j]=dics[j]['Consumption']
			iscost_matrix[:,:,j]=dics[j]['nh_matrix']
			childcare_matrix[:,:,j]=dics[j]['Childcare']
			theta_matrix[:,:,j]=dics[j]['Theta']
			ssrs_t2_matrix[:,j]=dics[j]['SSRS_t2']
			ssrs_t5_matrix[:,j]=dics[j]['SSRS_t5']
			wage_matrix[:,:,j]=dics[j]['Wage']
			spouse_income_matrix[:,:,j]=dics[j]['Spouse_income']
			spouse_employment_matrix[:,:,j]=dics[j]['Spouse_employment_matrix']
			hours_matrix[:,:,j]=dics[j]['Hours']
			kids_matrix[:,:,j]=dics[j]['Kids']
			marr_matrix[:,:,j]=dics[j]['Marriage']

		return {'income_matrix':income_matrix,
				'theta_matrix': theta_matrix,
				'ssrs_t2_matrix':ssrs_t2_matrix,'ssrs_t5_matrix':ssrs_t5_matrix,
				'childcare_matrix':childcare_matrix,'wage_matrix': wage_matrix,
				'consumption_matrix':consumption_matrix,'spouse_income_matrix':spouse_income_matrix,
				'spouse_employment_matrix':spouse_employment_matrix,
				'hours_matrix': hours_matrix,
				'iscost_matrix': iscost_matrix,
				'kids_matrix': kids_matrix ,'marr_matrix': marr_matrix  }

	def aux_model(self,choices):
		"""
		Computes the auxiliary estimates from simulated data
		"""

		#number of choices
		J = 2*3
		J_1 = 3 #3 hours categories
		nperiods=self.nperiods
		
		age_child = np.zeros((self.agech0.shape[0],nperiods))

		for x in range(0,nperiods):
			age_child[:,x]=np.reshape(self.agech0,self.N)+x

		##Obtaining Auxiliary estimate for every m##
		childcare_matrix=choices['childcare_matrix']
		hours_matrix=choices['hours_matrix']
		wage_matrix=choices['wage_matrix']
		income_matrix=choices['income_matrix']
		spouse_income_matrix=choices['spouse_income_matrix']
		spouse_employment_matrix=choices['spouse_employment_matrix']
		ssrs_t2_matrix=choices['ssrs_t2_matrix']
		ssrs_t5_matrix=choices['ssrs_t5_matrix']
		consumption_matrix=choices['consumption_matrix']
		kids_matrix=choices['kids_matrix']
		marr_matrix=choices['marr_matrix']


		############################################################
		####Utility function########################
		############################################################

		#child care at period t=1
		age_aux = age_child[:,1]
		passign_aux = self.passign[:,0]
		cc_logit = childcare_matrix[:,1,:]
		boo = (age_aux<=5)
		beta_childcare = np.mean(cc_logit[boo,:],axis=0) #beta for every m


		#mean hours at t=0,1
		hours_aux=np.concatenate((hours_matrix[:,0,:],hours_matrix[:,1,:],hours_matrix[:,4,:],hours_matrix[:,7,:]),axis=0)
		passign_aux=np.concatenate((self.passign[:,0],self.passign[:,0],self.passign[:,0],self.passign[:,0]),axis=0)
		
		hours_aux_1 = hours_aux == self.hours_p
		hours_aux_2 = hours_aux == self.hours_f
		beta_hours1 = np.mean(hours_aux_1,axis=0)
		beta_hours2 = np.mean(hours_aux_2,axis=0)

		
		############################################################
		####Wage process###########################################
		############################################################


		passign_aux = np.concatenate((self.passign[:,0],self.passign[:,0],
			self.passign[:,0],self.passign[:,0]),axis=0)

		wage_aux = np.log(np.concatenate((wage_matrix[:,0,:],wage_matrix[:,1,:],
		wage_matrix[:,4,:],wage_matrix[:,7,:]),axis=0)) #to panel and logs

		
		logt_dic={'period0':np.zeros((self.N,1)),
		'period1': np.zeros((self.N,1)) + 1,
		'period4': np.zeros((self.N,1)) + 4,
		'period7':np.zeros((self.N,1)) + 7}
		
		lt = np.reshape(np.concatenate((logt_dic['period0'][:,0],
			logt_dic['period1'][:,0],logt_dic['period4'][:,0],
			logt_dic['period7'][:,0]),axis=0),(self.N*4,1))

		x_list = [] #the X matrix
		x_list.append(np.reshape(np.concatenate((self.x_w[:,0],self.x_w[:,0],self.x_w[:,0],self.x_w[:,0]),axis=0),(self.N*4,1)))
		x_list.append(lt)
		x_list.append(np.reshape(np.concatenate((self.x_w[:,1],self.x_w[:,1],self.x_w[:,1],self.x_w[:,1]),axis=0),(self.N*4,1)))

		#sample who work all years
		boo_sample = (hours_matrix[:,0,:]>0) & (hours_matrix[:,1,:]>0) & (hours_matrix[:,4,:]>0) & (hours_matrix[:,7,:]>0)
		boo_work = np.concatenate((boo_sample,boo_sample,
			boo_sample,boo_sample),axis=0)

		beta_w=np.zeros((len(x_list),self.M))
		sigma_w=np.zeros((1,self.M))
		rho_eps=np.zeros((1,self.M))
		
		for j in range(self.M): #the sample loop
			xw_aux=np.concatenate((x_list[0][boo_work[:,j]==1,:],
				x_list[1][boo_work[:,j]==1,:],
				x_list[2][boo_work[:,j]==1,:]),axis=1)

			
			if np.linalg.cond(np.dot(np.transpose(xw_aux),
					xw_aux)) < 1/sys.float_info.epsilon: #If nonsingular matrix

				xx_inv=np.linalg.inv(np.dot(np.transpose(xw_aux),xw_aux))
				xy=np.dot(np.transpose(xw_aux),wage_aux[boo_work[:,j],j])
				beta_w[:,j]=np.dot(xx_inv,xy)

				#obtaining residuals by period for those who work all periods
				e_list = []
				n_work = self.x_w[boo_sample[:,j]==1,1].shape[0]

				for k in [0,1,4,7]:

					#Xs for those working all periods
					xw_aux_2=np.concatenate((np.reshape(self.x_w[boo_sample[:,j]==1,0],(n_work,1)),
						np.reshape(logt_dic['period' + str(k)][boo_sample[:,j]==1],(n_work,1)),
						np.reshape(self.x_w[boo_sample[:,j]==1,1],(n_work,1)),),axis=1)
					
					e = np.log(wage_matrix[boo_sample[:,j]==1,k,j]) - np.dot(xw_aux_2,beta_w[:,j])
					e_list.append(e)

				e  = np.concatenate((e_list[1],e_list[2],e_list[3]),axis=0).reshape((n_work*3,1))
				e_t1  = np.concatenate((e_list[0],e_list[1],e_list[2]),axis=0).reshape((n_work*3,1)) #lagged
				
				ee_inv = np.linalg.inv(np.dot(np.transpose(e_t1),e_t1))
				ey = np.dot(np.transpose(e_t1),e)
				rho_eps[:,j] = np.dot(ee_inv,ey)
				u = e - e_t1*rho_eps[:,j]
				sigma_w[:,j]=np.sum(np.square(u))/(e.shape[0] - rho_eps[:,j].shape[0])
			else:
				print ('disregarding m sample: singular matrix in wage process estimation')
				pass
		beta_wagep=np.concatenate((beta_w,sigma_w,rho_eps),axis=0)

		############################################################
		####Spouse's earnings and employment########################
		############################################################
		passign_aux = self.passign[:,0]
			
		wage_aux = np.log(spouse_income_matrix[:,2,:]) #to panel and logs

		#aca voy: check error message. have to condition for marriage and control group
		boo_sample = spouse_employment_matrix[:,2,:] == 1

		x_list = [] #the X matrix

		x_list.append(np.reshape(self.x_w[:,0],(self.x_w[:,0].shape[0],1)))
		x_list.append(np.reshape(self.x_w[:,1],(self.x_w[:,1].shape[0],1)))

		beta_w=np.zeros((len(x_list),self.M))
		sigma_w=np.zeros((1,self.M))

		for j in range(self.M): #the sample loop
				xw_aux=np.concatenate((x_list[0][boo_sample[:,j]==1,:],
					x_list[1][boo_sample[:,j]==1,:]),axis=1)

				if np.linalg.cond(np.dot(np.transpose(xw_aux),xw_aux)) < 1/sys.float_info.epsilon: #If nonsingular matrix

					xx_inv=np.linalg.inv(np.dot(np.transpose(xw_aux),xw_aux))
					xy=np.dot(np.transpose(xw_aux),wage_aux[boo_sample[:,j]==1,j])
					beta_w[:,j]=np.dot(xx_inv,xy)

					e = wage_aux[boo_sample[:,j]==1,j] - np.dot(xw_aux,beta_w[:,j])

					sigma_w[:,j]=np.sum(np.square(e))/(e.shape[0] - beta_w[:,j].shape[0])
				else:
					#print ('disregarding m sample: singular matrix in wage process estimation')
					pass

		beta_wage_spouse = np.concatenate((beta_w,sigma_w),axis=0)

		beta_emp_spouse = np.mean(boo_sample,axis=0)

		
		############################################################
		###Prod function############################################
		############################################################
		

		#aux variables
		age_aux = np.concatenate((age_child[:,1],
			age_child[:,4]),axis=0)
		ssrs_aux = np.concatenate((ssrs_t2_matrix,
			ssrs_t5_matrix),axis=0)

		income_aux = np.concatenate((income_matrix[:,1,:],
			income_matrix[:,4,:]),axis=0)/100000

		leisure_aux = np.concatenate((hours_matrix[:,1,:],
			hours_matrix[:,4,:]),axis=0)/100

		cte = np.ones((ssrs_aux.shape[0],1))
		
		childcare_aux = np.concatenate((childcare_matrix[:,1,:],childcare_matrix[:,4,:]),axis=0)

		beta_inputs = np.zeros((6,self.M)) #5 moments
		betas_init_prod = np.zeros((1,self.M)) #1 moment


		
		for j in range(self.M):

			#for gamma1
			beta_inputs[0,j] = np.corrcoef(ssrs_t2_matrix[:,j],ssrs_t5_matrix[:,j])[1,0]
			
			x_aux = np.concatenate((np.reshape(income_aux[:,j],(income_aux[:,j].shape[0],1)),
				np.reshape(leisure_aux[:,j],(leisure_aux[:,j].shape[0],1)),cte),axis=1)
			xx = np.dot(np.transpose(x_aux),x_aux)
			xy = np.dot(np.transpose(x_aux),ssrs_aux[:,j])
			xx_inv = np.linalg.inv(xx)
			betas_aux = np.dot(xx_inv,xy)
			beta_inputs[1,j] = betas_aux[0]
			beta_inputs[2,j] = betas_aux[1]

			#for tfp
			boo_young_cc0 = (age_aux<=5) & (childcare_aux[:,j] == 0)
			boo_young_cc1 = (age_aux<=5) & (childcare_aux[:,j] == 1)
			beta_inputs[3,j] = np.mean(ssrs_aux[boo_young_cc1,j]) - np.mean(ssrs_aux[boo_young_cc0,j])
			
			#variance
			beta_inputs[4,j] = np.var(ssrs_t2_matrix[:,j])
			beta_inputs[5,j] = np.var(ssrs_t5_matrix[:,j])

			#for initial theta
			boo_sample = hours_matrix[:,0,j]>0
			betas_init_prod[0,j] = np.corrcoef(ssrs_t2_matrix[boo_sample==1,j],np.log(wage_matrix[boo_sample==1,0,j]))[1,0]
			
		
		return{'beta_childcare':beta_childcare,'beta_hours1': beta_hours1,
		'beta_hours2':beta_hours2,'beta_wagep': beta_wagep,
		'beta_inputs': beta_inputs,'betas_init_prod':betas_init_prod,
		'beta_wage_spouse':beta_wage_spouse,'beta_emp_spouse':beta_emp_spouse}
	
	
	def ll(self,beta):
		"""
		Takes structural parameters and computes the objective function for optimization 
		
		"""
		start_time = time.time()
		print ('')
		print ('')
		print ('Beginning sample generator')

		def sym(a):
			return ((1/(1+np.exp(-a))) - 0.5)*2

		#updating beta->parameters instance to compute likelihood.
		self.param0.eta = beta[0]
		self.param0.alphap = beta[1]
		self.param0.alphaf = beta[2]
		self.param0.betaw[0] = beta[3]
		self.param0.betaw[1] = beta[4]
		self.param0.betaw[2] = beta[5]
		self.param0.betaw[3] = np.exp(beta[6])
		self.param0.betaw[4] = beta[7]
		self.param0.beta_spouse[0] = beta[8]
		self.param0.beta_spouse[1] = beta[9]
		self.param0.beta_spouse[2] = np.exp(beta[10])
		self.param0.c_emp_spouse = beta[11]
		self.param0.gamma1 = beta[12]
		self.param0.gamma2 = beta[13]
		self.param0.gamma3 = beta[14]
		self.param0.tfp = beta[15]
		self.param0.sigma_z[0] = beta[16]
		self.param0.sigma_z[1] = beta[17]
		self.param0.rho_theta_epsilon = sym(beta[18])
					

		#The model (utility instance)
		hours = np.zeros(self.N)
		childcare  = np.zeros(self.N)

		model  = util.Utility(self.param0,self.N,self.x_w,self.x_m,self.x_k,self.passign,
			self.nkids0,self.married0,hours,childcare,self.agech0,
			self.hours_p,self.hours_f,self.wr,self.cs,self.ws)

		##obtaining emax instance##
		emax_instance = self.emax(self.param0,model)

		time_emax = time.time() - start_time
		print ('')
		print ('')
		print ('Done emax in')
		print("--- %s seconds ---" % (time_emax))
		print ('')
		print ('')
		
		##obtaining samples##
		start_time = time.time()
		choices = self.samples(self.param0,emax_instance,model)

		time_choices = time.time() - start_time
		print ('')
		print ('')
		print ('Done sample gen in')
		print("--- %s seconds ---" % (time_choices))
		print ('')
		print ('')

		###########################################################################
		##Getting the betas of the auxiliary model#################################
		###########################################################################
		start_time = time.time()
		dic_betas=self.aux_model(choices)

		time_opt = time.time() - start_time
		print ('')
		print ('')
		print ('Done betas generation in')
		print("--- %s seconds ---" % (time_opt))
		print ('')
		print ('')
		start_time = time.time()
		print ('')
		print ('')
		print ('Beginning aux model generator')


		#utility_aux
		beta_childcare=np.mean(dic_betas['beta_childcare'],axis=0) #1x1
		beta_hours1=np.mean(dic_betas['beta_hours1'],axis=0) #1x1
		beta_hours2=np.mean(dic_betas['beta_hours2'],axis=0) #1x1
		beta_wagep=np.mean(dic_betas['beta_wagep'],axis=1) # 6 x 1
		beta_inputs=np.mean(dic_betas['beta_inputs'],axis=1) #4 x 1
		betas_init_prod=np.mean(dic_betas['betas_init_prod'],axis=1) #1 x 1
		beta_wage_spouse=np.mean(dic_betas['beta_wage_spouse'],axis=1)
		beta_emp_spouse=np.mean(dic_betas['beta_emp_spouse'],axis=0)
	

		###########################################################################
		####Forming the likelihood#################################################
		###########################################################################

		#Number of moments to match
		num_par = beta_childcare.size + beta_hours1.size + beta_hours2.size + beta_wagep.size + beta_wage_spouse.size + beta_emp_spouse.size + beta_inputs.size + betas_init_prod.size
		
		#Outer matrix
		x_vector=np.zeros((num_par,1))
		
		x_vector[0:beta_childcare.size,0] = beta_childcare - self.moments_vector[0,0]
		
		ind=beta_childcare.size
		x_vector[ind:ind+beta_hours1.size,0] = beta_hours1 - self.moments_vector[ind,0]

		ind = ind + beta_hours1.size
		x_vector[ind:ind+beta_hours2.size,0] = beta_hours2 - self.moments_vector[ind,0]
		
		ind=ind + beta_hours2.size
		x_vector[ind: ind+ beta_wagep.size,0] = beta_wagep - self.moments_vector[ind:ind+ beta_wagep.size,0]

		ind=ind + beta_wagep.size
		x_vector[ind: ind+ beta_wage_spouse.size,0] = beta_wage_spouse - self.moments_vector[ind:ind+ beta_wage_spouse.size,0]
		
		ind=ind +beta_wage_spouse.size
		x_vector[ind: ind+ beta_emp_spouse.size,0] = beta_emp_spouse - self.moments_vector[ind:ind+ beta_emp_spouse.size,0]

		ind = ind + beta_emp_spouse.size
		x_vector[ind:ind + beta_inputs.size,0] = beta_inputs - self.moments_vector[ind:ind + beta_inputs.size,0]

		ind = ind + beta_inputs.size
		x_vector[ind:ind + betas_init_prod.size,0] = betas_init_prod - self.moments_vector[ind:ind + betas_init_prod.size,0]
			
		
		#The Q metric
		q_w = np.dot(np.dot(np.transpose(x_vector),self.w_matrix),x_vector)
		print ('')
		print ('The objetive function value equals ', q_w)
		print ('')

		time_opt=time.time() - start_time
		print ('Done aux model generation in')
		print("--- %s seconds ---" % (time_opt))

		return q_w



	def optimizer(self):
		
		
		#symmetric interval constraint
		def syminv(g):
			out = -np.log((2/(g+1)) - 1)
			return out
		
				
		beta0 = np.array([self.param0.eta,self.param0.alphap,self.param0.alphaf,
			self.param0.betaw[0],
			self.param0.betaw[1],self.param0.betaw[2],
			np.log(self.param0.betaw[3]),self.param0.betaw[4],
			self.param0.beta_spouse[0],self.param0.beta_spouse[1],
			np.log(self.param0.beta_spouse[2]),
			self.param0.c_emp_spouse,
			self.param0.gamma1,self.param0.gamma2,self.param0.gamma3,
			self.param0.tfp,
			self.param0.sigma_z[0],self.param0.sigma_z[1],
			syminv(self.param0.rho_theta_epsilon)]) 

		
		#Here we go
		opt = minimize(self.ll, beta0,  method='Nelder-Mead', options={'maxiter':5000, 'maxfev': 90000, 'ftol': 1e-3, 'disp': True});
		#opt = minimize(self.ll, beta0,  method='Nelder-Mead', options={'maxiter':5000, 'gtol': 1e-3, 'disp': True});
		#opt = pybobyqa.solve(self.ll, beta0)

		return opt



