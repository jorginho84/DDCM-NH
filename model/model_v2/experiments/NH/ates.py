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
	def __init__(self,N,M,choices,models,agech0_a,agech0_b,d_childa,d_childb,passign,hours_p,hours_f,nperiods,
		nperiods_cc,nperiods_ct,nperiods_emp,nperiods_theta,period_y,
		sd_matrix):


		self.N,self.M=N,M
		self.choices = choices
		self.models = models
		self.agech0_a,self.agech0_b=agech0_a,agech0_b
		self.d_childa,self.d_childb=d_childa,d_childb
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
		agech_a = np.zeros((self.N,nperiods))
		agech_b = np.zeros((self.N,nperiods))

		for periodt in range(nperiods):
			agech_a[self.d_childa[:,0] == 1,periodt] = self.agech0_a[self.d_childa[:,0] == 1] + periodt
			agech_b[self.d_childb[:,0] == 1,periodt] = self.agech0_b[self.d_childb[:,0] == 1] + periodt


		agech = np.concatenate((agech_a[self.d_childa[:,0] == 1,:],
			agech_b[self.d_childb[:,0] == 1,:]),axis=0)

		return agech


	def cc(self,choices):

		#ATE on child care
		nperiods = self.nperiods_cc
		cc_t_0_a = choices['Choice_0']['childcare_a_matrix'][:,0:nperiods,:]
		cc_t_1_a = choices['Choice_1']['childcare_a_matrix'][:,0:nperiods,:]
		cc_t_0_b = choices['Choice_0']['childcare_a_matrix'][:,0:nperiods,:]
		cc_t_1_b = choices['Choice_1']['childcare_a_matrix'][:,0:nperiods,:]
		
		cc_t_0 = np.concatenate((cc_t_0_a[self.d_childa[:,0]==1,:,:],
			cc_t_0_b[self.d_childb[:,0]==1,:,:]),axis=0)

		cc_t_1 = np.concatenate((cc_t_1_a[self.d_childa[:,0]==1,:,:],
			cc_t_1_b[self.d_childb[:,0]==1,:,:]),axis=0)

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

		boo_sample = np.zeros(self.N)
		boo_sample[self.agech0_a>=self.agech0_b] = self.agech0_a[self.agech0_a>=self.agech0_b] <=6
		boo_sample[self.agech0_a<self.agech0_b] = self.agech0_b[self.agech0_a<self.agech0_b] <=6
				
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
			
		boo_sample = np.zeros(self.N)
		boo_sample[self.agech0_a>=self.agech0_b] = self.agech0_a[self.agech0_a>=self.agech0_b] <=6
		boo_sample[self.agech0_a<self.agech0_b] = self.agech0_b[self.agech0_a<self.agech0_b] <=6
		
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
		ltheta_0_a = np.log(choices['Choice_0']['theta_matrix_a'][:,1:nperiods,:])
		ltheta_0_b = np.log(choices['Choice_0']['theta_matrix_b'][:,1:nperiods,:])

		ltheta_0 = np.concatenate((ltheta_0_a[self.d_childa[:,0]==1,:,:],
			ltheta_0_b[self.d_childb[:,0]==1,:,:]),axis=0)

		ltheta_1_a = np.log(choices['Choice_1']['theta_matrix_a'][:,1:nperiods,:])
		ltheta_1_b = np.log(choices['Choice_1']['theta_matrix_b'][:,1:nperiods,:])

		ltheta_1 = np.concatenate((ltheta_1_a[self.d_childa[:,0]==1,:,:],
			ltheta_1_b[self.d_childb[:,0]==1,:,:]),axis=0)

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
		cc_sim_matrix_a = []
		cc_sim_matrix_b = []
		ct_sim_matrix = []
		h_sim_matrix = []

		for j in range(2):
			cc_sim_matrix_a.append(choices['Choice_' + str(j)]['childcare_a_matrix'])
			cc_sim_matrix_b.append(choices['Choice_' + str(j)]['childcare_b_matrix'])
			ct_sim_matrix.append(choices['Choice_' + str(j)]['consumption_matrix'])
			h_sim_matrix.append(choices['Choice_' + str(j)]['hours_matrix'])


		#The sample
		age_child = self.agech(nperiods)
		boo_y = (age_child[:,self.period_y]<=6)

		ate_cont_theta = np.zeros((nperiods-1,self.M))
		ate_cont_lt = np.zeros((nperiods-1,self.M))
		ate_cont_cc = np.zeros((nperiods-1,self.M))
		ate_cont_ct = np.zeros((nperiods-1,self.M))
		
		#Generating contributions
		for periodt in range(nperiods-1):									

			for j in range(self.M):

				#theta0
				theta0 = []
				theta_00 = []
				theta_01 = []
				theta_00.append(choices['Choice_' + str(0)]['theta_matrix_a'][:,periodt,j])
				theta_00.append(choices['Choice_' + str(0)]['theta_matrix_b'][:,periodt,j])
				theta_01.append(choices['Choice_' + str(1)]['theta_matrix_a'][:,periodt,j])
				theta_01.append(choices['Choice_' + str(1)]['theta_matrix_b'][:,periodt,j])
				theta0.append(theta_00)
				theta0.append(theta_01)

				#the theta contribution
				ltheta_th1 = models[1].thetat(periodt,theta0[1],
					h_sim_matrix[0][:,periodt,j],cc_sim_matrix_a[0][:,periodt,j],
					cc_sim_matrix_b[0][:,periodt,j],
					ct_sim_matrix[0][:,periodt,j])
				ltheta_th0 = models[0].thetat(periodt,theta0[0],
					h_sim_matrix[0][:,periodt,j],cc_sim_matrix_a[0][:,periodt,j],
					cc_sim_matrix_b[0][:,periodt,j],
					ct_sim_matrix[0][:,periodt,j])

				ltheta_th1_aux = np.concatenate((ltheta_th1[0][self.d_childa[:,0]==1],
					ltheta_th1[1][self.d_childb[:,0]==1]),axis=0)

				ltheta_th0_aux = np.concatenate((ltheta_th0[0][self.d_childa[:,0]==1],
					ltheta_th0[1][self.d_childb[:,0]==1]),axis=0)

				ate_cont_theta[periodt,j] = np.mean(np.log(ltheta_th1_aux[boo_y]) - np.log(ltheta_th0_aux[boo_y]))/self.sd_matrix[periodt,j]

				#time contribution
				ltheta_th1 = models[1].thetat(periodt,theta0[1],
					h_sim_matrix[1][:,periodt,j],cc_sim_matrix_a[0][:,periodt,j],
					cc_sim_matrix_b[0][:,periodt,j],
					ct_sim_matrix[0][:,periodt,j])
				ltheta_th0 = models[0].thetat(periodt,theta0[0],
					h_sim_matrix[0][:,periodt,j],cc_sim_matrix_a[0][:,periodt,j],
					cc_sim_matrix_b[0][:,periodt,j],
					ct_sim_matrix[0][:,periodt,j])
				
				ltheta_th1_aux = np.concatenate((ltheta_th1[0][self.d_childa[:,0]==1],
					ltheta_th1[1][self.d_childb[:,0]==1]),axis=0)

				ltheta_th0_aux = np.concatenate((ltheta_th0[0][self.d_childa[:,0]==1],
					ltheta_th0[1][self.d_childb[:,0]==1]),axis=0)


				ate_cont_lt[periodt,j] = np.mean(np.log(ltheta_th1_aux[boo_y]) - np.log(ltheta_th0_aux[boo_y]))/self.sd_matrix[periodt,j]

				#CC contribution
				ltheta_th1 = models[1].thetat(periodt,theta0[1],
					h_sim_matrix[1][:,periodt,j],cc_sim_matrix_a[1][:,periodt,j],
					cc_sim_matrix_b[1][:,periodt,j],
					ct_sim_matrix[0][:,periodt,j])
				ltheta_th0 = models[0].thetat(periodt,theta0[0],
					h_sim_matrix[1][:,periodt,j],cc_sim_matrix_a[0][:,periodt,j],
					cc_sim_matrix_b[0][:,periodt,j],
					ct_sim_matrix[0][:,periodt,j])
				
				ltheta_th1_aux = np.concatenate((ltheta_th1[0][self.d_childa[:,0]==1],
					ltheta_th1[1][self.d_childb[:,0]==1]),axis=0)

				ltheta_th0_aux = np.concatenate((ltheta_th0[0][self.d_childa[:,0]==1],
					ltheta_th0[1][self.d_childb[:,0]==1]),axis=0)

				ate_cont_cc[periodt,j] = np.mean(np.log(ltheta_th1_aux[boo_y]) - np.log(ltheta_th0_aux[boo_y]))/self.sd_matrix[periodt,j]

				#Consumption contribution
				ltheta_th1 = models[1].thetat(periodt,theta0[1],
					h_sim_matrix[1][:,periodt,j],cc_sim_matrix_a[1][:,periodt,j],
					cc_sim_matrix_b[1][:,periodt,j],
					ct_sim_matrix[1][:,periodt,j])
				ltheta_th0 = models[0].thetat(periodt,theta0[0],
					h_sim_matrix[1][:,periodt,j],cc_sim_matrix_a[1][:,periodt,j],
					cc_sim_matrix_b[1][:,periodt,j],
					ct_sim_matrix[0][:,periodt,j])

				ltheta_th1_aux = np.concatenate((ltheta_th1[0][self.d_childa[:,0]==1],
					ltheta_th1[1][self.d_childb[:,0]==1]),axis=0)

				ltheta_th0_aux = np.concatenate((ltheta_th0[0][self.d_childa[:,0]==1],
					ltheta_th0[1][self.d_childb[:,0]==1]),axis=0)

				ate_cont_ct[periodt,j] = np.mean(np.log(ltheta_th1_aux[boo_y]) - np.log(ltheta_th0_aux[boo_y]))/self.sd_matrix[periodt,j]

		return {'Theta': ate_cont_theta, 'Time': ate_cont_lt, 'CC':ate_cont_cc, 'Money': ate_cont_ct }



	def sim_ate(self):
		"""
		Generates treatment effects and contributions
		"""

		return {'ATES': {'CC': self.cc(self.choices),'Consumption': self.ct(self.choices),
				'Part-time': self.emp(self.choices)[0],'Full-time': self.emp(self.choices)[1],
				'Hours': self.emp(self.choices)[2],'Theta': self.theta(self.choices)[0]},
				'Contributions': self.mechanisms(self.choices,self.models)}

