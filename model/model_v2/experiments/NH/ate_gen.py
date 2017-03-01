"""
This Class generates ATEs on child care, labor supply, income, and theta
"""
from __future__ import division #omit for python 3.x
import numpy as np



class ATE:
	def __init__(self,choices,agech0,passign,hours_p,hours_f):

		self.choices = choices
		self.agech0=agech0
		self.passign=passign
		self.hours_p,self.hours_f=hours_p,hours_f
		

	def cc(self,choices):

		#ATE on child care
		nperiods = 3
		cc_t = choices['choice_matrix']>=3
		cc_t = cc_t[:,0:nperiods,:]
		age_child = np.zeros((cc_t.shape[0],nperiods))
		for x in range(nperiods):
			age_child[:,x]=self.agech0[:,0] + x

		boo_young = age_child<=6
		boo_t = self.passign[:,0]==1
		boo_c = self.passign[:,0]==0

		ate_cc=np.zeros(nperiods)
		for t in range(nperiods):
			ate_cc[t] = np.mean(np.mean(cc_t[(boo_young[:,t]) & (boo_t),t,:],axis = 0) - np.mean(cc_t[(boo_young[:,t]) & (boo_c),t,:],axis = 0),axis=0)


		return np.mean(ate_cc) #average over all periods

	def ct(self,choices):

		nperiods = 3 #during new hope
		ct = choices['consumption_matrix'][:,0:nperiods,:]
		ate_inc = np.mean( np.mean(ct[self.passign[:,0]==1,:,:],axis=0) - np.mean(ct[self.passign[:,0]==0,:,:],axis=0),axis=1)

		return np.mean(ate_inc)

	def emp(self,choices):

		nperiods = 3
		part = choices['hours_matrix']==self.hours_p
		full = choices['hours_matrix']==self.hours_f
		part = part[:,0:nperiods,:]
		full = full[:,0:nperiods,:]

		ate_part = np.mean(np.mean(part[self.passign[:,0]==1,:,:],axis=0) - np.mean(part[self.passign[:,0]==0,:,:],axis=0),axis=1 )
		ate_full = np.mean(np.mean(full[self.passign[:,0]==1,:,:],axis=0) - np.mean(full[self.passign[:,0]==0,:,:],axis=0),axis=1 )

		return [np.mean(ate_part), np.mean(ate_full)]

	def theta(self,choices):

		ltheta = np.log(choices['theta_matrix'][:,1:,:])
		ate_ltheta = np.mean(np.mean(ltheta[self.passign[:,0]==1,:,:],axis=0) - np.mean(ltheta[self.passign[:,0]==0,:,:],axis=0),axis=1)
		return np.mean(ate_ltheta)

	#this is wrong b/c util includes emax! have to compute utility from model
	def util(self,choices): 

		utils = choices['utils_c_periodt'] #current-value utils
		argmax = choices['choice_matrix']
		N = utils.shape[0]
		J = utils.shape[1]
		T = utils.shape[2]
		M = utils.shape[3]

		npv = np.zeros((N,M))

		for m in range(M):
			for t in range(T):

				for j in range(J):
					if t==0:
						npv[argmax[:,t,m]==j,m] = utils[argmax[:,t,m]==j,j,t,m]
					else:
						npv[argmax[:,t,m]==j,m] = npv[argmax[:,t,m]==j,m] + utils[argmax[:,t,m]==j,j,t,m]*0.95**t

		return np.mean(npv)

	def sim_ate(self):

		return {'CC': self.cc(self.choices),'Consumption': self.ct(self.choices),
		'Part-time': self.emp(self.choices)[0],'Full-time': self.emp(self.choices)[1],
		'Theta': self.theta(self.choices),'Welfare':self.util(self.choices)}







