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
		q =  self.output_ins.__dict__['param0'].__dict__['q']
		scalew =  self.output_ins.__dict__['param0'].__dict__['scalew']
		shapew =  self.output_ins.__dict__['param0'].__dict__['shapew']
		pafdc =  self.output_ins.__dict__['param0'].__dict__['pafdc']
		psnap =  self.output_ins.__dict__['param0'].__dict__['psnap']
		
		#Utility function
		eta=bs[0]
		alphap=bs[1]
		alphaf=bs[2]

		#wage process
		wagep_betas=np.array([bs[3],bs[4],bs[5],
			bs[6],bs[7]]).reshape((5,1))

		#Production function [young[cc0,cc1],old]
		gamma1=[bs[8],bs[10]]
		gamma2=[bs[9],bs[11]] 
		tfp=bs[12]
		sigmatheta=0

		#Measurement system: three measures for t=2, one for t=5
		kappas=[[bs[13],bs[14],bs[15],bs[16]],[bs[17],bs[18],bs[19],bs[20]]]
		lambdas=[1,1]


		#Re-defines the instance with parameters 
		param0=util.Parameters(alphap, alphaf, eta, gamma1, gamma2, tfp, sigmatheta,
			wagep_betas, marriagep_betas, kidsp_betas, eitc_list,
			afdc_list,snap_list,cpi,q,scalew,shapew,
			lambdas,kappas,pafdc,psnap)
		return param0 

	def emax(self,param0):
		"""
		Computes the emax for a given set of parameters
		"""
		return self.output_ins.emax(param0)


	def choices(self,param0,emax_instance):
		"""
		Simulates M samples
		"""
		return self.output_ins.samples(param0,emax_instance)


	def sim_moments(self,samples):
		"""
		Computes simulated moments for a given sample
		"""
		dic_betas = self.output_ins.aux_model(samples)

		beta_childcare=np.mean(dic_betas['beta_childcare'],axis=0) #1x1
		beta_hours2=np.mean(dic_betas['beta_hours2'],axis=0) #1x1
		beta_hours3=np.mean(dic_betas['beta_hours3'],axis=0) #1x1
		beta_wagep=np.mean(dic_betas['beta_wagep'],axis=1) # 5 x 1
		beta_kappas_t2=np.mean(dic_betas['beta_kappas_t2'],axis=1) #4 x 1
		beta_kappas_t5=np.mean(dic_betas['beta_kappas_t5'],axis=1) #4 x 1
		beta_inputs_old=np.mean(dic_betas['beta_inputs_old'],axis=1) #2 x 1
		beta_inputs_young_cc1=np.mean(dic_betas['beta_inputs_young_cc1'],axis=1) #3 x 1

		return [beta_childcare, beta_hours2,beta_hours3,beta_wagep,beta_kappas_t2,
		  beta_kappas_t5, beta_inputs_old,beta_inputs_young_cc1]

	def binding(self,psi):
		"""
		Computes the binding function for a given psi (structural parameter)
		"""

		#Calling parameters instance based on betas
		param0 = self.betas_struct(psi)

		#Computing the emax
		emax_instance = self.emax(param0)

		#Computing M samples
		samples = self.choices(param0,emax_instance)

		#Computing aux model (binding function)

		return self.sim_moments(samples)

	def db_dtheta(self,psi,eps,K,S):
		"""
		Computes d b/d theta using finite differences
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
			psi_low = psi.copy()
			psi_high = psi.copy()
			psi_low[s] = psi[s] - eps 
			psi_high[s] = psi[s] + eps

			#Computing betas
			betas_low = self.binding(psi_low)
			betas_high = self.binding(psi_high)

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


			db_dt[:,s] = (betas_high_array[:,0] - betas_low_array[:,0]) / eps



		return db_dt

	
	def big_sand(self,h,nmoments,npar):
		"""
		Computes the big sandwich matrix (standard errors of structural parameters)
		h: marginal difference
		"""

		#The gradient of binding function
		dbdt = self.db_dtheta(self.psi,h,nmoments,npar)

		#The weighting matrix used in estimation
		w_matrix = self.output_ins.__dict__['w_matrix']

		#The big sandwhich matrix: a_matrix*a_inn*var_cov*a_inn'a_matrix
		a_inn = np.dot(np.transpose(dbdt),w_matrix)
		a_matrix = np.linalg.inv(np.dot(a_inn,dbdt))
		a_left = np.dot(a_matrix,a_inn)

		return np.dot(np.dot(a_left,self.var_cov),np.transpose(a_left))



