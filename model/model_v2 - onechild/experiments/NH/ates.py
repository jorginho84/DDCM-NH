"""
This Class generates ATEs on child care, labor supply, income, and theta. It also
generates contribution of inputs in explaining the impact of a policy

"""
#from __future__ import division #omit for python 3.x
import numpy as np



class ATE:
	"""
	Computes a dictionary of ATEs

	nperiods_cc,nperiods_ct,nperiods_emp,nperiods_theta: # of periods to measure
	changes in cc, ct, emp, and theta, from t=0...nperiodsx (in the case of theta
	, starting at t=1)

	period_y = I measure changes in inputs for the sample that were young until t=period_y

	models: a list of two different models: one where everybody is in treatment other in control
	"""
	def __init__(self,N,M,choices,models,agech0,passign,hours_p,hours_f,nperiods,
		nperiods_cc,nperiods_ct,nperiods_emp,nperiods_theta,period_y,
		sd_matrix):


		self.N,self.M=N,M
		self.choices = choices
		self.models = models
		self.agech0=agech0
		self.passign=passign
		self.hours_p,self.hours_f=hours_p,hours_f
		self.nperiods = nperiods
		self.nperiods_cc = nperiods_cc
		self.nperiods_ct = nperiods_ct
		self.nperiods_emp = nperiods_emp
		self.nperiods_theta = nperiods_theta
		self.period_y = period_y
		self.sd_matrix = sd_matrix
		
	def agech(self,nperiods):
		agech = np.zeros((self.N,nperiods))
		
		for periodt in range(nperiods):
			agech[:,periodt] = self.agech0[:,0] + periodt
			
		return agech


	def cc(self,choices):

		#ATE on child care
		nperiods = self.nperiods_cc
		cc_t_0 = choices['Choice_0']['childcare_matrix'][:,0:nperiods,:]
		cc_t_1 = choices['Choice_1']['childcare_matrix'][:,0:nperiods,:]
		
		age_child = self.agech(nperiods)

		boo_sample = (age_child[:,self.period_y]<=6)
		
		ate_cc=np.zeros((nperiods,self.M))
		for t in range(nperiods):
			ate_cc[t,:] = np.mean(cc_t_1[boo_sample,t,:],axis = 0) - np.mean(cc_t_0[boo_sample,t,:],axis = 0)


		return ate_cc #average over all periods


	def ct(self,choices):

		nperiods = self.nperiods_ct
		ct_0 = choices['Choice_0']['consumption_matrix'][:,0:nperiods,:]
		ct_1 = choices['Choice_1']['consumption_matrix'][:,0:nperiods,:]

		boo_sample = self.agech0[:,0] <= 6
						
		ate_inc=np.zeros((nperiods,self.M))
		for t in range(nperiods):
			ate_inc[t,:] = np.mean(ct_1[boo_sample==1,t,:],axis=0) - np.mean(ct_0[boo_sample==1,t,:],axis=0)

		return ate_inc

	def emp(self,choices):

		nperiods = self.nperiods_emp
		hours = []
		part = []
		full = []

		for k in range(2):
			hours.append(choices['Choice_'+str(k)]['hours_matrix'][:,0:nperiods,:])
			part.append(choices['Choice_'+str(k)]['hours_matrix'][:,0:nperiods,:]==self.hours_p)
			full.append(choices['Choice_'+str(k)]['hours_matrix'][:,0:nperiods,:]==self.hours_f)
			
		boo_sample = self.agech0[:,0] <= 6
				
		ate_part = np.zeros((nperiods,self.M))
		ate_full = np.zeros((nperiods,self.M))
		ate_hours = np.zeros((nperiods,self.M))
		for t in range(nperiods):
			ate_part[t,:] = np.mean(part[1][boo_sample==1,t,:],axis=0) - np.mean(part[0][boo_sample==1,t,:],axis=0)
			ate_full[t,:] = np.mean(full[1][boo_sample==1,t,:],axis=0) - np.mean(full[0][boo_sample==1,t,:],axis=0)
			ate_hours[t,:] = np.mean(hours[1][boo_sample==1,t,:],axis=0) - np.mean(part[0][boo_sample==1,t,:],axis=0)

		return [ate_part,ate_full,ate_hours]

	def theta(self,choices):
		
		nperiods=self.nperiods_theta
		
		ltheta_0 = np.log(choices['Choice_0']['theta_matrix'][:,1:nperiods,:])
		ltheta_1 = np.log(choices['Choice_1']['theta_matrix'][:,1:nperiods,:])
		
		long_theta = np.concatenate((ltheta_0,ltheta_1),axis=0)
		sd_matrix_long = np.zeros((nperiods-1,self.M))
		for j in range (self.M):
			for t in range(nperiods-1):
				sd_matrix_long[t,j] = np.std(long_theta[:,t,j],axis=0)

		
		age_child = self.agech(nperiods)
		boo_sample = (age_child[:,self.period_y]<=6)
		
		ate_ltheta = np.zeros((nperiods-1,self.M))
		for t in range(nperiods-1):
			ate_ltheta[t,:] = np.mean(ltheta_1[boo_sample,t,:],axis=0) - np.mean(ltheta_0[boo_sample,t,:],axis=0)
		return [ate_ltheta/self.sd_matrix[1:,:],sd_matrix_long]

	
	def mechanisms(self,choices,models):
		"""
		Computes contribution of inputs in the production function
		"""

		nperiods=self.nperiods_theta

		#Choices
		cc_sim_matrix = []
		ct_sim_matrix = []
		h_sim_matrix = []

		for j in range(2):
			cc_sim_matrix.append(choices['Choice_' + str(j)]['childcare_matrix'])
			ct_sim_matrix.append(choices['Choice_' + str(j)]['consumption_matrix'])
			h_sim_matrix.append(choices['Choice_' + str(j)]['hours_matrix'])


		#The sample
		age_child = self.agech(nperiods)
		boo_y = (age_child[:,self.period_y]<=6)

		ate_cont_theta = np.zeros((nperiods-1,self.M))
		ate_cont_lt = np.zeros((nperiods-1,self.M))
		ate_cont_cc = np.zeros((nperiods-1,self.M))
		ate_cont_ct = np.zeros((nperiods-1,self.M))

		#The SD matrix to normalize
		sd_matrix = self.theta(self.choices)[1]
		
		#Generating contributions
		for periodt in range(nperiods-1):									

			for j in range(self.M):

				#theta0
				theta0 = []
				theta0.append(choices['Choice_' + str(0)]['theta_matrix'][:,periodt,j])
				theta0.append(choices['Choice_' + str(1)]['theta_matrix'][:,periodt,j])
				

				#the theta contribution
				ltheta_th1 = models[1].thetat(periodt,theta0[1],
					h_sim_matrix[0][:,periodt,j],cc_sim_matrix[0][:,periodt,j],
					ct_sim_matrix[0][:,periodt,j])
				ltheta_th0 = models[0].thetat(periodt,theta0[0],
					h_sim_matrix[0][:,periodt,j],cc_sim_matrix[0][:,periodt,j],
					ct_sim_matrix[0][:,periodt,j])

				ate_cont_theta[periodt,j] = np.mean(np.log(ltheta_th1[boo_y]) - np.log(ltheta_th0[boo_y]))/sd_matrix[periodt,j]

				#time contribution
				ltheta_th1 = models[1].thetat(periodt,theta0[1],
					h_sim_matrix[1][:,periodt,j],cc_sim_matrix[0][:,periodt,j],
					ct_sim_matrix[0][:,periodt,j])
				ltheta_th0 = models[0].thetat(periodt,theta0[1],
					h_sim_matrix[0][:,periodt,j],cc_sim_matrix[0][:,periodt,j],
					ct_sim_matrix[0][:,periodt,j])
				
				ate_cont_lt[periodt,j] = np.mean(np.log(ltheta_th1[boo_y]) - np.log(ltheta_th0[boo_y]))/sd_matrix[periodt,j]

				#CC contribution
				ltheta_th1 = models[1].thetat(periodt,theta0[1],
					h_sim_matrix[1][:,periodt,j],cc_sim_matrix[1][:,periodt,j],
					ct_sim_matrix[0][:,periodt,j])
				ltheta_th0 = models[0].thetat(periodt,theta0[1],
					h_sim_matrix[1][:,periodt,j],cc_sim_matrix[0][:,periodt,j],
					ct_sim_matrix[0][:,periodt,j])
				
				ate_cont_cc[periodt,j] = np.mean(np.log(ltheta_th1[boo_y]) - np.log(ltheta_th0[boo_y]))/sd_matrix[periodt,j]

				#Consumption contribution
				ltheta_th1 = models[1].thetat(periodt,theta0[1],
					h_sim_matrix[1][:,periodt,j],cc_sim_matrix[1][:,periodt,j],
					ct_sim_matrix[1][:,periodt,j])
				ltheta_th0 = models[0].thetat(periodt,theta0[1],
					h_sim_matrix[1][:,periodt,j],cc_sim_matrix[1][:,periodt,j],
					ct_sim_matrix[0][:,periodt,j])

				ate_cont_ct[periodt,j] = np.mean(np.log(ltheta_th1[boo_y]) - np.log(ltheta_th0[boo_y]))/sd_matrix[periodt,j]

		return {'Theta': ate_cont_theta, 'Time': ate_cont_lt, 'CC':ate_cont_cc, 'Money': ate_cont_ct }



	def sim_ate(self):
		"""
		Generates treatment effects and contributions
		"""

		return {'ATES': {'CC': self.cc(self.choices),'Consumption': self.ct(self.choices),
				'Part-time': self.emp(self.choices)[0],'Full-time': self.emp(self.choices)[1],
				'Hours': self.emp(self.choices)[2],'Theta': self.theta(self.choices)[0]},
				'Contributions': self.mechanisms(self.choices,self.models)}

