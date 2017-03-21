"""
This Class generates ATEs on child care, labor supply, income, and theta
"""
from __future__ import division #omit for python 3.x
import numpy as np



class ATE:
	"""
	Computes a dictionary of ATEs

	nperiods_cc,nperiods_ct,nperiods_emp,nperiods_theta: # of periods to measure
	changes in cc, ct, emp, and theta, from t=0...nperiodsx (in the case of theta
	, starting at t=1)

	period_y = I measure changes in inputs for the sample that were young until t=period_y
	"""
	def __init__(self,M,choices,agech0,passign,hours_p,hours_f,
		nperiods_cc,nperiods_ct,nperiods_emp,nperiods_theta,period_y):


		self.M=M
		self.choices = choices
		self.agech0=agech0
		self.passign=passign
		self.hours_p,self.hours_f=hours_p,hours_f
		self.nperiods_cc = nperiods_cc
		self.nperiods_ct = nperiods_ct
		self.nperiods_emp = nperiods_emp
		self.nperiods_theta = nperiods_theta
		self.period_y = period_y
		

	def cc(self,choices):

		#ATE on child care
		nperiods = self.nperiods_cc
		cc_t = choices['choice_matrix'][:,0:nperiods,:]>=3
		age_child = np.zeros((cc_t.shape[0],nperiods))
		for x in range(nperiods):
			age_child[:,x]=self.agech0[:,0] + x

		boo_sample = age_child[:,self.period_y]<=6
		boo_young = age_child<=6
		boo_t = (self.passign[:,0]==1) & (boo_sample)
		boo_c = (self.passign[:,0]==0) & (boo_sample)

		ate_cc=np.zeros(nperiods)
		for t in range(nperiods):
			ate_cc[t] = np.mean(np.mean(cc_t[(boo_young[:,t]) & (boo_t),t,:],axis = 0) - np.mean(cc_t[(boo_young[:,t]) & (boo_c),t,:],axis = 0),axis=0)


		return np.mean(ate_cc) #average over all periods

	def ct(self,choices):

		nperiods = self.nperiods_ct
		ct = choices['consumption_matrix'][:,0:nperiods,:]
		age_child = np.zeros((ct.shape[0],nperiods))
		for x in range(nperiods):
			age_child[:,x]=self.agech0[:,0] + x

		boo_sample = age_child[:,self.period_y]<=6
		boo_t = (self.passign[:,0]==1) & (boo_sample)
		boo_c = (self.passign[:,0]==0) & (boo_sample)
		
		ate_inc = np.mean( np.mean(ct[boo_t,:,:],axis=0) - np.mean(ct[boo_c,:,:],axis=0),axis=1)

		return np.mean(ate_inc)

	def emp(self,choices):

		nperiods = self.nperiods_emp
		part = choices['hours_matrix']==self.hours_p
		full = choices['hours_matrix']==self.hours_f
		part = part[:,0:nperiods,:]
		full = full[:,0:nperiods,:]
		age_child = np.zeros((part.shape[0],nperiods))
		for x in range(nperiods):
			age_child[:,x]=self.agech0[:,0] + x

		boo_sample = age_child[:,self.period_y]<=6
		boo_t = (self.passign[:,0]==1) & (boo_sample)
		boo_c = (self.passign[:,0]==0) & (boo_sample)

		ate_part = np.mean(np.mean(part[boo_t,:,:],axis=0) - np.mean(part[boo_c,:,:],axis=0),axis=1 )
		ate_full = np.mean(np.mean(full[boo_t,:,:],axis=0) - np.mean(full[boo_c,:,:],axis=0),axis=1 )

		return [np.mean(ate_part), np.mean(ate_full)]

	def theta(self,choices):
		
		nperiods=self.nperiods_theta
		ltheta = np.log(choices['theta_matrix'][:,1:nperiods,:])
		for j in range(self.M):
			for t in range(nperiods-1):
				ltheta[:,t,j] = ltheta[:,t,j]/np.std(ltheta[:,t,j],axis=0)

		age_child = np.zeros((ltheta.shape[0],nperiods))
		for x in range(nperiods):
			age_child[:,x]=self.agech0[:,0] + x

		boo_sample = age_child[:,self.period_y]<=6
		boo_t = (self.passign[:,0]==1) & (boo_sample)
		boo_c = (self.passign[:,0]==0) & (boo_sample)


		ate_ltheta = np.mean(np.mean(ltheta[boo_t,:,:],axis=0) - np.mean(ltheta[boo_c,:,:],axis=0),axis=1)
		return np.mean(ate_ltheta)

	
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


		age_child = np.zeros((N,9)) #all periods
		for x in range(9):#all periods
			age_child[:,x]=self.agech0[:,0] + x

		boo_sample = age_child[:,self.period_y]<=6
		boo_t = (self.passign[:,0]==1) & (boo_sample)
		boo_c = (self.passign[:,0]==0) & (boo_sample)

		return np.mean(np.mean(npv[boo_t,:],axis=0) - np.mean(npv[boo_c,:],axis=0) )
		

	def sim_ate(self):

		return {'CC': self.cc(self.choices),'Consumption': self.ct(self.choices),
		'Part-time': self.emp(self.choices)[0],'Full-time': self.emp(self.choices)[1],
		'Theta': self.theta(self.choices),'Welfare':self.util(self.choices)}







