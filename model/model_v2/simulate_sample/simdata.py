"""
This class takes a dictionary of emax functions and simulate
fake data taking as given state variables at period 0.

It returns the utility values as well (including option values) 

"""
from __future__ import division #omit for python 3.x
import numpy as np
import itertools
import sys, os
from scipy import stats
from scipy import interpolate
#sys.path.append("C:\\Users\\Jorge\\Dropbox\\Chicago\\Research\\Human capital and the household\]codes\\model")
sys.path.append("/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model/simulate_sample")
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
		x_w,x_m,x_k,x_wmk,passign,theta0,nkids0,married0,agech,hours_p,hours_f):
		self.N,self.param,self.emax_function=N,param,emax_function
		self.x_w,self.x_m,self.x_k,self.x_wmk=x_w,x_m,x_k,x_wmk
		self.passign,self.theta0,self.nkids0,self.married0=passign,theta0,nkids0,married0
		self.agech=agech
		self.hours_p, self.hours_f=hours_p,hours_f
		
		

	def choice(self,periodt,bigt,theta0,nkids0,married0,wage0,free0,price0):
		"""
		Takes a set of state variables and computes the utility +option value
		of different set of choices for a given periodt

		These state variables do not change with period (set them equal at t=0):
		x_w,x_m,x_k,passign. The rest of the state variables change according to
		the period

		It returns a list containing the utility value and the emaxt+1 that is 
		computed in period t


		"""

		#Set number of choices
		J=6

		#save choices utility  here
		util_values=np.zeros((self.N,J))
		

		#The choice loop
		for j in range(0,J):

			if j<=2:

				if j==0:
					hours_aux=0
				elif j==1:
					hours_aux=self.hours_p
				elif j==2:
					hours_aux=self.hours_f

				hours=np.full(self.N,hours_aux,dtype=float)
				childcare=np.zeros(self.N)

			else:
				if j==3:
					hours_aux=0
				elif j==4:
					hours_aux=self.hours_p
				elif j==5:
					hours_aux=self.hours_f

				hours=np.full(self.N,hours_aux,dtype=float)
				childcare=np.ones(self.N)

			
			#Computing utility
			model=util.Utility(self.param,self.N,self.x_w,self.x_m,self.x_k,self.passign,
				theta0,nkids0,married0,hours,childcare,self.agech,self.hours_p,self.hours_f)

			util_values[:,j]=model.simulate(periodt,wage0,free0,price0)


			####Only for periods t<T (compute an emax function)
			#For period T, only current utility
			if periodt<bigt:
				#Data for computing emaxt+1, given choices and state at t
				married_t1=model.marriaget(periodt+1,married0)
				married_t1=np.reshape(married_t1,(self.N,1))
				nkids_t1=model.kidst(periodt+1,np.reshape(nkids0,(self.N,1)),
					married0)+nkids0
				#current income to get future theta
				dincome_t=model.dincomet(periodt,hours,wage0,married0,nkids0)
				theta_t1=model.thetat(periodt+1,theta0,hours,childcare,dincome_t,
					married0,nkids0,wage0,free0,price0) #theta at t+1 uses inputs at t

			
				data_int_t1=np.concatenate((np.reshape(np.log(theta_t1),(self.N,1)), 
					np.reshape(nkids_t1,(self.N,1)),married_t1,
					np.reshape(np.square(np.log(theta_t1)),(self.N,1)),
					np.reshape(self.passign,(self.N,1)), 
					self.x_wmk), axis=1)

				#Getting dictionary to incorporate emax_t+1, choice j
				emax_ins=self.emax_function[0]['emax'+str(periodt+1)][j]
				emax_betas=emax_ins.betas()
				emax_t1=emax_ins.int_values(data_int_t1,emax_betas)
	
				#Including option value (dicount factor 0.95)
				util_values[:,j]=util_values[:,j]+0.95*emax_t1

		return util_values


	def fake_data(self,n_periods):
		"""
		This function computes the trajectory of choices and state variables
		It also returns the emax for each period

		"""
		
		#saving here
		theta_matrix=np.zeros((self.N,n_periods))
		choice_matrix=np.zeros((self.N,n_periods))
		dincome_matrix=np.zeros((self.N,n_periods))
		consumption_matrix=np.zeros((self.N,n_periods))
		wage_matrix=np.zeros((self.N,n_periods))
		hours_matrix=np.zeros((self.N,n_periods))
		childcare_matrix=np.zeros((self.N,n_periods))
		marr_matrix=np.zeros((self.N,n_periods))
		kids_matrix=np.zeros((self.N,n_periods))
		util_values_dic=[] #list of t=0,..,8 periods
		ssrs_t2=np.zeros(self.N)
		ssrs_t5=np.zeros(self.N)

		#initialize state variables
		theta0=self.theta0.copy()
		married0=self.married0.copy()
		nkids0=self.nkids0.copy()
		#wage0=np.zeros((self.N,1))

		#Re-compute wages (don't observe w on those unemployed)
		hours=np.zeros(self.N)
		childcare=np.zeros(self.N)
		model=util.Utility(self.param,self.N,self.x_w,self.x_m,self.x_k,self.passign,
			theta0,nkids0,married0,hours,childcare,self.agech,self.hours_p,self.hours_f)
		wage0=model.waget(0)
		free0=model.q_prob()
		price0=model.price_cc()
		
	
		for periodt in range(0,n_periods): #from t=0 to t=8
			
			wage_matrix[:,periodt]=wage0.copy()
			theta_matrix[:,periodt]=theta0.copy()
			kids_matrix[:,periodt]=nkids0[:,0].copy()
			marr_matrix[:,periodt]=married0[:,0].copy()

			hours_t=np.zeros(self.N)
			childcare_t=np.zeros(self.N)
			
			#Use self.choice function to obtain choices and saving u_ijt
			#array of J columns
			utiliy_values=self.choice(periodt,n_periods-1,theta0,nkids0,married0,wage0,
				free0,price0)
			util_values_dic.append(utiliy_values)

			#Young vs OLD: maximization
			age_child=np.reshape(self.agech,(self.N)) + periodt
			choices_index=np.zeros(self.N)
			choices_index[age_child<=6]=np.argmax(utiliy_values[age_child<=6,:],axis=1) #young
			choices_index[age_child>6]=np.argmax(utiliy_values[age_child>6,0:3],axis=1) #old
			choice_matrix[:,periodt]=choices_index.copy()
			
			#at periodt=0, if choice>4, individual chooses childcare=1	
			hours_t[choices_index==0]=0
			hours_t[choices_index==1]=self.hours_p
			hours_t[choices_index==2]=self.hours_f
			hours_t[choices_index==3]=0
			hours_t[choices_index==4]=self.hours_p
			hours_t[choices_index==5]=self.hours_f
			childcare_t[choices_index>2]=1

			#Saving
			hours_matrix[:,periodt]=hours_t.copy()
			childcare_matrix[:,periodt]=childcare_t.copy()

			#Current income
			model=util.Utility(self.param,self.N,self.x_w,self.x_m,
				self.x_k,self.passign,theta0,nkids0,married0,hours_t,childcare_t,self.agech,
				self.hours_p,self.hours_f)
			
			dincome0=model.dincomet(periodt,hours_t,wage0,married0,nkids0)
			dincome_matrix[:,periodt]=dincome0.copy()
			consumption0=model.consumptiont(periodt,hours_t,childcare_t,dincome0,married0,nkids0,wage0,
				free0,price0)
			consumption_matrix[:,periodt]=consumption0.copy()

			#SSRS measures
			if periodt==2: 
				ssrs_t2=model.measures(periodt,theta0)
			elif periodt==5:
				ssrs_t5=model.measures(periodt,theta0)


			#Next period states (only if periodt<8): update

			if periodt<n_periods-1:
				
				married_t1=model.marriaget(periodt+1,married0)
				married_t1=np.reshape(married_t1,(self.N,1))
				nkids_t1=model.kidst(periodt+1,np.reshape(nkids0,(self.N,1)),
					married0)+nkids0 #baseline kids + if they have a kid next period
				
				theta_t1=model.thetat(periodt+1,theta0,hours_t,childcare_t,dincome0,
				married0,nkids0,wage0,free0,price0) #theta at t+1 uses inputs at t
				wage_t1=model.waget(periodt+1)
				free_t1=model.q_prob()
				price_t1=model.price_cc()

				#updating
				married0=married_t1.copy()
				nkids0=nkids_t1.copy()
				theta0=theta_t1.copy()
				wage0=wage_t1.copy()
				free0=free_t1.copy()
				price0=price_t1.copy()

				
		return {'Choices': choice_matrix, 'Theta': theta_matrix,
		 'Income': dincome_matrix, 'Hours':hours_matrix, 'Childcare': childcare_matrix,
		 'Wage': wage_matrix, 'Uti_values_dic': util_values_dic,
		 'Marriage': marr_matrix, 'Kids': kids_matrix,'Consumption': consumption_matrix,
		 'SSRS_t2':ssrs_t2,'SSRS_t5':ssrs_t5}







		


