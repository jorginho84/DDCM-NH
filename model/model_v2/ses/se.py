"""
This class computes standard errors (ses) of structural parameters

need:
1. computing binding function (numerically)
1.1 estimate aux parameters from simulated data
1.2 compute first derivative of binding function (change in betas for a small change in theta)

2. compute J_0: hessian of Q w/r to aux parameters (either analitically of numerically)
2.2 computing Q
2.2 forming derivatives

3.Computing I0-K0
3.1 first derivatives of Q

4. Calling optimal values of structural parameters

5. Calling observed auxiliary parameters

6. code to make derivatives
options: (i) numpy.gradient
"""

from __future__ import division #omit for python 3.x
import numpy as np
import sys, os
sys.path.append("/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample")
import utility as util
import gridemax
import time
import int_linear
import emax as emax
import simdata as simdata
sys.path.append("/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/estimation")
import estimate as estimate


class SEs:
	"""
	The class defines the objects to compute SEs
	"""

	def __init__(self,output_ins,var_cov,psi):
		"""
		output_ins: instance of the estimate class
		var_cov: var-cov matrix of auxiliary estimates
		psi: structural parameters (estimated in II)
		"""

		self.output_ins=output_ins
		self.var_cov=var_cov
		self.psi = psi
		

	def betas_struct(self,bs):
		"""
		Takes structural parameters and update the parameter instance
		bs: structural parameters

		"""

		#these are defined inside the output_ins instance and are held fixed
		marriagep_betas = self.output_ins.__dict__['param0'].__dict__['betam']
		kidsp_betas =  self.output_ins.__dict__['param0'].__dict__['betak']
		eitc_list =  self.output_ins.__dict__['param0'].__dict__['eitc']
		afdc_list =  self.output_ins.__dict__['param0'].__dict__['afdc']
		snap_list =  self.output_ins.__dict__['param0'].__dict__['snap']
		cpi =  self.output_ins.__dict__['param0'].__dict__['cpi']
		pafdc =  self.output_ins.__dict__['param0'].__dict__['pafdc']
		psnap =  self.output_ins.__dict__['param0'].__dict__['psnap']
		mup =  self.output_ins.__dict__['param0'].__dict__['mup']
		sigma2theta =  self.output_ins.__dict__['param0'].__dict__['sigma2theta']
		
		#Utility function
		eta=bs[0]
		alphap=bs[1]
		alphaf=bs[2]
		
		#wage process
		wagep_betas=np.array([bs[3],bs[4],bs[5],bs[6],
			bs[7],np.exp(bs[8]),bs[9]]).reshape((7,1))

		#Production function [young[cc0,cc1],old]
		gamma1=bs[10]
		gamma2=bs[11]
		gamma3=bs[12]
		tfp=bs[13]
		
				
		def sym(a):
			return ((1/(1+np.exp(-a))) - 0.5)*2

		kappas=[[bs[14],bs[15],bs[16],bs[17]],[bs[18],bs[19],bs[20],bs[21]]]

		rho_theta_epsilon =  sym(bs[22])

		lambdas=[1,1]


		#Re-defines the instance with parameters 
		param0=util.Parameters(alphap,alphaf,eta,gamma1,gamma2,gamma3,
			tfp,sigma2theta,rho_theta_epsilon,wagep_betas, marriagep_betas,
			kidsp_betas, eitc_list,afdc_list,snap_list,cpi,lambdas,kappas,
			pafdc,psnap,mup)

		return param0 

	def emax(self,param0,model):
		"""
		Computes the emax for a given set of parameters
		"""
		return self.output_ins.emax(param0,model)


	def choices(self,param0,emax_instance,model):
		"""
		Simulates M samples
		"""
		return self.output_ins.samples(param0,emax_instance,model)


	def sim_moments(self,samples):
		"""
		Computes simulated moments for a given sample
		"""
		dic_betas = self.output_ins.aux_model(samples)

		beta_childcare=np.mean(dic_betas['beta_childcare'],axis=0) #1x1
		beta_hours1=np.mean(dic_betas['beta_hours1'],axis=0) #1x1
		beta_hours2=np.mean(dic_betas['beta_hours2'],axis=0) #1x1
		beta_kappas_t2=np.mean(dic_betas['beta_kappas_t2'],axis=1) #4 x 1
		beta_kappas_t5=np.mean(dic_betas['beta_kappas_t5'],axis=1) #4 x 1
		beta_wagep=np.mean(dic_betas['beta_wagep'],axis=1) # 7 x 1
		beta_inputs=np.mean(dic_betas['beta_inputs'],axis=1) #5 x 1
		betas_init_prod=np.mean(dic_betas['betas_init_prod'],axis=1) #1 x 1
		

		return [beta_childcare,beta_hours1,beta_hours2,beta_wagep,
		beta_kappas_t2,beta_kappas_t5,
		beta_inputs, betas_init_prod]

	

	def obj_fn(self,betas):
		"""
		Computes objective function given s
		"""

		beta_childcare=betas[0]
		beta_hours1=betas[1]
		beta_hours2=betas[2]
		beta_wagep=betas[3]
		beta_kappas_t2=betas[4]
		beta_kappas_t5=betas[5]
		beta_inputs=betas[6]
		betas_init_prod=betas[7]
		#Number of moments to match
		num_par=beta_childcare.size + beta_hours1.size + beta_hours2.size + beta_wagep.size + + beta_kappas_t2.size +  beta_kappas_t5.size + beta_inputs.size + betas_init_prod.size
		
		#Outer matrix
		x_vector=np.zeros((num_par,1))

		
		x_vector[0:beta_childcare.size,0]=beta_childcare - self.output_ins.moments_vector[0,0]
		
		ind=beta_childcare.size
		x_vector[ind:ind+beta_hours1.size,0]=beta_hours1 - self.output_ins.moments_vector[ind,0]

		ind = ind + beta_hours1.size
		x_vector[ind:ind+beta_hours2.size,0]=beta_hours2 - self.output_ins.moments_vector[ind,0]
		
		ind=ind + beta_hours2.size
		x_vector[ind: ind+ beta_wagep.size,0]=beta_wagep - self.output_ins.moments_vector[ind:ind+ beta_wagep.size,0]
		
		ind = ind + beta_wagep.size
		x_vector[ind:ind + beta_kappas_t2.size,0]=beta_kappas_t2 - self.output_ins.moments_vector[ind:ind + beta_kappas_t2.size,0]

		ind = ind + beta_kappas_t2.size
		x_vector[ind: ind + beta_kappas_t5.size,0] = beta_kappas_t5 - self.output_ins.moments_vector[ind: ind + beta_kappas_t5.size,0]
		
		ind = ind + beta_kappas_t5.size
		x_vector[ind:ind + beta_inputs.size,0] = beta_inputs - self.output_ins.moments_vector[ind:ind + beta_inputs.size,0]
		
		ind = ind + beta_inputs.size
		x_vector[ind:ind + betas_init_prod.size,0] = betas_init_prod - self.output_ins.moments_vector[ind:ind + betas_init_prod.size,0]
		
		
		#The Q metric
		q_w=np.dot(np.dot(np.transpose(x_vector),np.linalg.inv(self.output_ins.w_matrix)),x_vector)
		
		return {'x_vector': x_vector, 'obj_fn': q_w}

	def binding(self,psi):
		"""
		1. Computes the binding function for a given psi (structural parameter)
		2. Computes the X vector
		"""

		#Calling parameters instance based on betas
		param0 = self.betas_struct(psi)

		#The model instance
		N=self.output_ins.__dict__['N']
		x_w=self.output_ins.__dict__['x_w']
		x_m=self.output_ins.__dict__['x_m']
		x_k=self.output_ins.__dict__['x_k']
		passign=self.output_ins.__dict__['passign']
		nkids0=self.output_ins.__dict__['nkids0']
		married0=self.output_ins.__dict__['married0']
		hours = np.zeros(N)
		childcare = np.zeros(N)
		agech0=self.output_ins.__dict__['agech0']
		hours_p=self.output_ins.__dict__['hours_p']
		hours_f=self.output_ins.__dict__['hours_f']
		wr=self.output_ins.__dict__['wr']
		cs=self.output_ins.__dict__['cs']
		ws=self.output_ins.__dict__['ws']


		model  = util.Utility(param0,N,x_w,x_m,x_k,	passign,nkids0,
			married0,hours,childcare,agech0,hours_p,hours_f,wr,cs,ws)

		#Computing the emax
		emax_instance = self.emax(param0,model)

		#Computing M samples
		samples = self.choices(param0,emax_instance,model)

		#Computing aux model (binding function)

		betas = self.sim_moments(samples)

		x_vector = self.obj_fn(betas)['x_vector']

		return {'betas': betas, 'x_vector': x_vector}


	def db_dtheta(self,psi,eps,K,S):
		"""
		Computes ingredients to compute sandwich matrix

		1*db/dtheta:
		It returns a K \times S matrix, where
		K: number of aux moments
		S: number of structural parameters
		K \geq S

		psi: structural parameters
		eps: marginal difference

		"""

		#save results here
		db_dt = np.zeros((K,S))
		
		
		for s in range(S):

			#evaluating at optimum
			psi_low = psi.copy()
			psi_high = psi.copy()

			#changing only relevant parameter, one at a time
			psi_low[s] = psi[s] - eps
			psi_high[s] = psi[s] + eps

			#Computing betas
			betas_low = self.binding(psi_low)['betas']
			betas_high = self.binding(psi_high)['betas']
			
			#From list to numpy array
			betas_low_array = np.array([[betas_low[0]]])
			betas_high_array = np.array([[betas_high[0]]])

			
			for l in range(1,len(betas_low)):
				
				if type(betas_low[l]) is np.float64:
					betas_low_array = np.concatenate( (betas_low_array,np.array([[betas_low[l]]])),axis=0 )
					betas_high_array = np.concatenate( (betas_high_array,np.array([[betas_high[l]]])),axis=0 )
				else:
					betas_low_array = np.concatenate( (betas_low_array,betas_low[l].reshape(betas_low[l].shape[0],1)),axis=0 )
					betas_high_array = np.concatenate( (betas_high_array,betas_high[l].reshape(betas_high[l].shape[0],1)),axis=0 )


			db_dt[:,s] = (betas_high_array[:,0] - betas_low_array[:,0]) / (psi_high[s]-psi_low[s])

			

		return db_dt

	
	def big_sand(self,h,nmoments,npar):
		"""
		Computes the big sandwich matrix (standard errors of structural parameters)
		h: marginal difference
		"""

		#The gradient of binding function
		dbdt = self.db_dtheta(self.psi,h,nmoments,npar)

		#The weighting matrix used in estimation
		w_matrix = self.output_ins.__dict__['w_matrix'].copy()

		for i in range(w_matrix.shape[0]):
			w_matrix[i,i] = w_matrix[i,i]**(-1)

		#The V matrix
		x_vector = self.binding(self.psi)['x_vector']
		v_matrix = np.dot(x_vector,np.transpose(x_vector))

		#The big sandwhich matrix: a_matrix*a_inn*var_cov*a_inn'a_matrix
		a_inn = np.dot(np.transpose(dbdt),w_matrix)
		a_matrix = np.linalg.inv(np.dot(a_inn,dbdt))
		a_left = np.dot(a_matrix,a_inn)

		return np.dot(np.dot(a_left,v_matrix),np.transpose(a_left))



