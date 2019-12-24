"""
This class takes a dictionary of emax functions and simulate
fake data taking as given state variables at period 0.

It returns the utility values as well (including option values) 

"""
#from __future__ import division #omit for python 3.x
import numpy as np
import itertools
import sys, os
from scipy import stats
from scipy import interpolate
sys.path.append("/home/jrodriguez/NH_HC/codes/model_v2/simulate_sample")
import utility as util
import int_linear
import time


class SimData:
	"""
	eitc: eitc function
	emax_function: interpolating instance
	The rest are state variables at period 0
	"""
	def __init__(self,N,param,emax_function,
		x_w,x_m,x_k,x_wmk,passign,nkids0,married0,agech,
		hours_p,hours_f,wr,cs,ws,model):
		"""
		model: a utility instance (with arbitrary parameters)
		"""
		self.N,self.param,self.emax_function=N,param,emax_function
		self.x_w,self.x_m,self.x_k,self.x_wmk=x_w,x_m,x_k,x_wmk
		self.passign,self.nkids0,self.married0=passign,nkids0,married0
		self.agech=agech
		self.hours_p, self.hours_f=hours_p,hours_f
		self.wr,self.cs,self.ws=wr,cs,ws
		self.model = model
		
	def change_util(self,param,N,x_w,x_m,x_k,passign,
				nkids0,married0,hours,childcare,
				agech,hours_p,hours_f,wr,cs,ws):
		"""
		This function changes parameters of util instance
		"""
		self.model.__init__(param,N,x_w,x_m,x_k,passign,nkids0,married0,
			hours,childcare,agech,
			hours_p,hours_f,wr,cs,ws)

		

	def choice(self,periodt,bigt,theta0,nkids0,married0,wage0,epsilon0,free0,price0,
		spouse_income0,spouse_employment0):
		"""
		Takes a set of state variables and computes the utility +option value
		of different set of choices for a given periodt

		These state variables do not change with period (set them equal at t=0):
		x_w,x_m,x_k,passign. The rest of the state variables change according to
		the period

		It returns a list containing the utility value and the emaxt+1 that is 
		computed in period t

		epsilon 0: shock consistent with wage0


		"""

		#Set number of choices
		J=3*2

		#save choices utility  here
		util_values=np.zeros((self.N,J))
		#save current value here
		util_values_c=np.zeros((self.N,J))
		
		hours_aux  = [0,self.hours_p,self.hours_f,
					0,self.hours_p,self.hours_f]

		cc_aux  = [0,0,0,1,1,1]

	
		
		for j in range(0,J):

			hours = np.full(self.N,hours_aux[j],dtype=float)
			childcare = np.full(self.N,cc_aux[j],dtype=float)
								
			#Computing utility
			self.change_util(self.param,self.N,self.x_w,self.x_m,self.x_k,self.passign,
				nkids0,married0,hours,childcare,self.agech,
				self.hours_p,self.hours_f,self.wr,self.cs,self.ws)

			#current consumption to get future theta
			dincome0=self.model.dincomet(periodt,hours,wage0,married0,nkids0,spouse_income0,spouse_employment0)['income']
			consumption0=self.model.consumptiont(periodt,hours,childcare,dincome0,spouse_income0,spouse_employment0,married0,
				nkids0,wage0,free0,price0)['income_pc']

			util_values[:,j]=self.model.simulate(periodt,wage0,free0,price0,
				theta0,spouse_income0,spouse_employment0)
			util_values_c[:,j]=util_values[:,j]


			####Only for periods t<T (compute an emax function)
			#For period T, only current utility
			if periodt<bigt:
				#Data for computing emaxt+1, given choices and state at t
				married_t1=self.model.marriaget(periodt+1,married0)
				married_t1=np.reshape(married_t1,(self.N,1))
				nkids_t1=self.model.kidst(periodt+1,np.reshape(nkids0,(self.N,1)),
					married0)+nkids0
				
				theta_t1=self.model.thetat(periodt,theta0,hours,childcare,consumption0) #theta at t+1 uses inputs at t
				epsilon_t1=self.model.epsilon(epsilon0)

			
				data_int_t1=np.concatenate((np.reshape(np.log(theta_t1),(self.N,1)),
					np.reshape(nkids_t1,(self.N,1)),married_t1,
					np.reshape(np.square(np.log(theta_t1)),(self.N,1)),
					np.reshape(self.passign,(self.N,1)), 
					np.reshape(epsilon_t1,(self.N,1)),
					np.reshape(np.square(epsilon_t1),(self.N,1)),
					self.x_wmk), axis=1)
				
				#arbitrary initializacion
				emax_ins = int_linear.Int_linear()
				

				#Getting dictionary to incorporate emax_t+1, choice j
				for age in range(1,11):

					#from this age, individuals solve a shorter problem
					if age>=2:
						if periodt+1>=19-age:
							emax_t1 = np.zeros(self.N)
						else:
							emax_betas=self.emax_function[10-age][0]['emax'+str(periodt+1)][j]
							emax_t1=emax_ins.int_values(data_int_t1,emax_betas)

					else:
						emax_betas=self.emax_function[10-age][0]['emax'+str(periodt+1)][j]
						emax_t1=emax_ins.int_values(data_int_t1,emax_betas)
		
					#Including option value (discount factor 0.86), youngest child
					util_values[self.agech[:,0]==age,j]=util_values[self.agech[:,0]==age,j]+0.86*emax_t1[self.agech[:,0]==age]

		return [util_values,util_values_c]


	def fake_data(self,n_periods):
		"""
		This function computes the trajectory of choices and state variables
		It also returns the emax for each period

		n_period: max # of periods to run the model (youngest child)

		"""
		
		#saving here
		theta_matrix=np.zeros((self.N,n_periods))
		choice_matrix=np.zeros((self.N,n_periods))
		dincome_matrix=np.zeros((self.N,n_periods))
		nh_matrix=np.zeros((self.N,n_periods))
		consumption_matrix=np.zeros((self.N,n_periods))
		wage_matrix=np.zeros((self.N,n_periods))
		spouse_income_matrix=np.zeros((self.N,n_periods))
		spouse_employment_matrix=np.zeros((self.N,n_periods))
		hours_matrix=np.zeros((self.N,n_periods))
		childcare_matrix=np.zeros((self.N,n_periods))
		marr_matrix=np.zeros((self.N,n_periods))
		kids_matrix=np.zeros((self.N,n_periods))
		cs_cost_matrix=np.zeros((self.N,n_periods))
		

		#choice index
		J = 3*2
		hours_aux  = [0,self.hours_p,self.hours_f,
					0,self.hours_p,self.hours_f]

		cc_aux  = [0,0,0,
					1,1,1]

		#initialize state variables
		married0=self.married0
		nkids0=self.nkids0
		
		hours=np.zeros(self.N)
		childcare=np.zeros(self.N)
		self.change_util(self.param,self.N,self.x_w,self.x_m,self.x_k,self.passign,
			nkids0,married0,hours,childcare,self.agech,self.hours_p,self.hours_f,
			self.wr,self.cs,self.ws)
		
		shocks_dic = self.model.shocks_init()
		epsilon0= shocks_dic['epsilon0']
		epsilon_theta0= shocks_dic['epsilon_theta0']

		wage_init_dic = self.model.wage_init(epsilon0)
		wage0= wage_init_dic['wage']
		theta0 = self.model.theta_init(epsilon_theta0)
		free0=self.model.q_prob()
		price0=self.model.price_cc()
		spouse_income0 = self.model.income_spouse()
		spouse_employment0 = self.model.employment_spouse()
				
		#Generating data
		for periodt in range(0,n_periods):
			
			wage_matrix[:,periodt]=wage0
			spouse_income_matrix[:,periodt]=spouse_income0
			spouse_employment_matrix[:,periodt]=spouse_employment0
			theta_matrix[:,periodt]=theta0
			kids_matrix[:,periodt]=nkids0[:,0]
			marr_matrix[:,periodt]=married0[:,0]

			hours_t=np.zeros(self.N)
			childcare_t=np.zeros(self.N)
					
			#Use self.choice function to obtain choices and saving u_ijt
			#array of J columns
			utils = self.choice(periodt,n_periods-1,theta0,nkids0,married0,wage0,
				epsilon0,free0,price0,spouse_income0,spouse_employment0)

			#Young vs OLD: maximization
			age_child=np.reshape(self.agech,(self.N)) + periodt
			choices_index=np.zeros(self.N)
			choices_index[age_child<=5]=np.argmax(utils[0][age_child<=5,:],axis=1) #young
			choices_index[age_child>5]=np.argmax(utils[0][age_child>5,0:3],axis=1) #old
			
			choice_matrix[:,periodt] = choices_index
			
			#Saving choices
			for j in range(J):
				hours_t[choices_index==j] = hours_aux[j]
				childcare_t[choices_index==j] = cc_aux[j]
						
			#Saving
			hours_matrix[:,periodt]=hours_t
			childcare_matrix[:,periodt]=childcare_t
			

			#Current income
			self.change_util(self.param,self.N,self.x_w,self.x_m,
				self.x_k,self.passign,nkids0,married0,hours_t,childcare_t,
				self.agech,
				self.hours_p,self.hours_f,self.wr,self.cs,self.ws)
			
			dincome0=self.model.dincomet(periodt,hours_t,wage0,married0,nkids0,
				spouse_income0,spouse_employment0)['income']
			dincome_matrix[:,periodt]=dincome0
			nh_matrix[:,periodt]=self.model.dincomet(periodt,hours_t,wage0,married0,
				nkids0,spouse_income0,spouse_employment0)['NH']
			consumption0=self.model.consumptiont(periodt,hours_t,childcare_t,
				dincome0,spouse_income0,spouse_employment0,
				married0,nkids0,wage0,free0,price0)['income_pc']
			consumption_matrix[:,periodt]=consumption0
			

			#SSRS measures
			if periodt==2: 
				ssrs_t2=self.model.measures(periodt,theta0)
			elif periodt==5:
				ssrs_t5=self.model.measures(periodt,theta0)


			
			#Next period states (only if periodt<8): update

			if periodt<n_periods-1:
				
				married_t1=self.model.marriaget(periodt+1,married0)
				married_t1=np.reshape(married_t1,(self.N,1))
				nkids_t1=self.model.kidst(periodt+1,np.reshape(nkids0,(self.N,1)),
					married0)+nkids0 #baseline kids + if they have a kid next period
				
				theta_t1 = self.model.thetat(periodt,theta0,hours_t,childcare_t,consumption0) #theta at t+1 uses inputs at t
				epsilon_t1 = self.model.epsilon(epsilon0)
				wage_t1 = self.model.waget(periodt+1,epsilon_t1)
				free_t1 = self.model.q_prob()
				price_t1 = self.model.price_cc()
				spouse_income1 = self.model.income_spouse()
				spouse_employment1 = self.model.employment_spouse()

				#updating
				married0 = married_t1
				nkids0 = nkids_t1
				theta0 = theta_t1
				wage0 = wage_t1
				epsilon0 = epsilon_t1
				free0 = free_t1
				price0 = price_t1
				spouse_income0 = spouse_income1
				spouse_employment0 = spouse_employment1

				
		return {'Choices': choice_matrix, 'Theta': theta_matrix,
		 'Income': dincome_matrix, 'Spouse_income': spouse_income_matrix, 
		 'Spouse_employment_matrix': spouse_employment_matrix, 'Hours':hours_matrix, 
		 'Childcare': childcare_matrix,
		 'Wage': wage_matrix, 'Marriage': marr_matrix, 'Kids': kids_matrix,'Consumption': consumption_matrix,
		 'SSRS_t2':ssrs_t2,'SSRS_t5':ssrs_t5, 'nh_matrix':nh_matrix}







		


