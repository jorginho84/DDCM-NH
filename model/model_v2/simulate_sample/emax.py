"""
This class obtains the emax functions from period T up to period 1

The emax are computed using montecarlo integration and linear interpolation
from a grid of the state variables.

The size of the grid is controlled in gridemax.py. Here, it is taken 
as a given

##find a way of computing this class much faster: have to do it
#for very run in the optimization algorithm!!

"""

from __future__ import division #omit for python 3.x
import numpy as np
import itertools
from numba import jit
import sys, os
from scipy import stats
import gc
from scipy import interpolate
from pathos.multiprocessing import ProcessPool
#sys.path.append("C:\\Users\\Jorge\\Dropbox\\Chicago\\Research\\Human capital and the household\]codes\\model")
sys.path.append("/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model/simulate_sample")
import utility as util
import gridemax
import int_linear
import time


class Emaxt:
	"""
	Computes emax functions recursively
	"""


	def __init__(self,param,D,grid_dict,hours_p,hours_f,wr,cs,ws,model):

		"""
		D=number of shocks for a given individual to be drawn
		grid_dict: a dictionary with the grid. The variables
		must have been shuffled before

		also, include the x's from the data (not from the grid anymore)

		model: a utility instance (with arbitrary parameters)

		"""


		self.param=param
		self.D,self.grid_dict=D,grid_dict
		self.hours_p,self.hours_f=hours_p,hours_f
		self.wr,self.cs,self.ws=wr,cs,ws
		self.model = model

	def change_util(self,param,N,x_w,x_m,x_k,passign,
				nkids0,married0,hours,childcare,agech,hours_p,hours_f,
				wr,cs,ws):
		"""
		This function changes parameters of util instance
		"""
		self.model.__init__(param,N,x_w,x_m,x_k,passign,nkids0,married0,
			hours,childcare,agech,hours_p,hours_f,wr,cs,ws)

		
	def emax_bigt(self,bigT):
		"""
		Computes the emax function for the last period (takes T-1 states, and 
			integrates period T unobservables)
		In this period, there is no choice of child care. So the are
		only five choices.


		bigT: indicates the last period (in calendar time)
		"""

		#dictionary with the grid
		#dict_aux=gridemax.grid()

		#Defining state variables of T-1
		passign=self.grid_dict['passign']
		theta0=self.grid_dict['theta0']
		nkids0=self.grid_dict['nkids0']
		married0=self.grid_dict['married0']
		agech=self.grid_dict['agech']
		epsilon_1=self.grid_dict['epsilon_1']#initial shock
		

		x_w=self.grid_dict['x_w']
		x_m=self.grid_dict['x_m']
		x_k=self.grid_dict['x_k']
		x_wmk=self.grid_dict['x_wmk']



		#Sample size
		ngrid=theta0.shape[0]

		agech=np.reshape(agech,ngrid)
		#number of choices (hours worked * child care)
		J=6

		#I save emaxT(T-1) values here
		emax_t1=np.zeros((ngrid,J))

		#At T-1, possible choices
		hours=np.zeros(ngrid)
		childcare=np.zeros(ngrid)

		self.change_util(self.param,ngrid,x_w,x_m,x_k,passign,
			nkids0,married0,hours,childcare,agech,self.hours_p,self.hours_f,
			self.wr,self.cs,self.ws)
		wage0=self.model.waget(bigT-1,epsilon_1)
		free0=self.model.q_prob()
		price0=self.model.price_cc()		
		
		
		#Choice T-1 loop
		for jt in range(0,J):
			if jt<=2:
				if jt==0:
					hours_aux=0
				elif jt==1:
					hours_aux=self.hours_p
				elif jt==2:
					hours_aux=self.hours_f
				hours=np.full(ngrid,hours_aux,dtype=float)
				childcare=np.zeros(ngrid)

			else:
				if jt==3:
					hours_aux=0
				elif jt==4:
					hours_aux=self.hours_p
				elif jt==5:
					hours_aux=self.hours_f
				hours=np.full(ngrid,hours_aux,dtype=float)
				childcare=np.ones(ngrid)

			#Here I save array of Ut by schock/choice (at T)
			u_vec=np.zeros((ngrid,self.D,J))

			#Income and consumption at T-1
			dincome0=self.model.dincomet(bigT-1,hours,wage0,married0,nkids0)['income']
			consumption0=self.model.consumptiont(bigT-1,hours,childcare,dincome0,married0,
				nkids0,wage0,free0,price0)['income_pc']
			

			#At T, loop over possible shocks, for every future choice
			#Montecarlo integration: loop over shocks by choice (hours and childcare)
					
			for j,i in itertools.product(range(0,J),range(0,self.D)):
				

				#States at T
				self.change_util(self.param,ngrid,x_w,x_m,x_k,
					passign,nkids0,married0,hours,childcare,agech,
					self.hours_p,self.hours_f,self.wr,self.cs,self.ws)

				periodt=bigT 

				married_t1=self.model.marriaget(periodt,married0)
				married_t1=np.reshape(married_t1,(ngrid,1))
				nkids_t1=self.model.kidst(periodt,np.reshape(nkids0,(ngrid,1)),
					married0)+nkids0
				epsilon_t1 = self.model.epsilon(epsilon_1)
				wage_t1=self.model.waget(periodt,epsilon_t1)
				free_t1=self.model.q_prob()
				price_t1=self.model.price_cc()
				#using t-1 income to get theta_T
				
				theta_t1=self.model.thetat(periodt-1,theta0,hours,childcare,consumption0) #theta at t+1 uses inputs at t

				#future (at T) possible decision
				if j<=2:
					if j==0:
						hours_aux2=0
					elif j==1:
						hours_aux2=self.hours_p
					elif j==2:
						hours_aux2==self.hours_f
					hours_t1=np.full(ngrid,hours_aux2,dtype=float)
					childcare_t1=np.zeros(ngrid)
				else:
					if j==3:
						hours_aux2=0
					elif j==4:
						hours_aux2=self.hours_p
					elif j==5:
						hours_aux2==self.hours_f
					hours_t1=np.full(ngrid,hours_aux2,dtype=float)
					childcare_t1=np.ones(ngrid)				

				self.change_util(self.param,ngrid,x_w,x_m,x_k,
					passign,nkids_t1,married_t1,hours_t1,childcare,agech,
					self.hours_p,self.hours_f,self.wr,self.cs,self.ws)
				
				#This is the terminal value!
				u_vec[:,i,j]=self.model.simulate(bigT,wage_t1,free_t1,price_t1,theta_t1) #Last period is T=8. Terminal value=0

				


			#obtaining max over choices by random schocks: young vs old
			max_ut=np.zeros((ngrid,self.D))
			max_ut[agech<=6,:]=np.max(u_vec[agech<=6,:,:],axis=2) #young
			max_ut[agech>6,:]=np.max(u_vec[agech>6,:,0:3],axis=2) #old

			


			#This is the emax for a given (for a given at choice T-1)
			av_max_ut=np.average(max_ut,axis=1)

			#database for interpolation
			data_int=np.concatenate( ( np.reshape(np.log(theta0),(ngrid,1)), 
				np.reshape(nkids0,(ngrid,1)),np.reshape(married0,(ngrid,1)),
				np.reshape(np.square(np.log(theta0)),(ngrid,1)),
				np.reshape(passign,(ngrid,1)), 
				np.reshape(epsilon_1,(ngrid,1)),#using present shock
				np.reshape(np.square(epsilon_1),(ngrid,1)),
				x_wmk ), axis=1)


			#Saving in the big matrix
			emax_t1[:,jt]=av_max_ut

			#saving instances.
			if jt==0: 
				emax_inst=[int_linear.Int_linear(data_int,av_max_ut)]
			else:
				emax_inst.append(int_linear.Int_linear(data_int,av_max_ut))

			

					
			

		#the instance with the eitc function and emax values

		return [emax_inst,emax_t1]


	def emax_t(self,periodt,bigt,emax_t1_ins):
		"""
		Computes the emax function at period t<T, taking as input
		an interpolating instance at t+1	
		bigt: indicates the number of the final period 
		periodt indicate the period to compute emax (emax1,emax2,emax3,...)
		"""
		#dictionary with the grid
		#dict_aux=gridemax.grid()

		#Defining state variables at t-1
		passign=self.grid_dict['passign']
		theta0=self.grid_dict['theta0']
		nkids0=self.grid_dict['nkids0']
		married0=self.grid_dict['married0']
		agech=self.grid_dict['agech']
		epsilon_1=self.grid_dict['epsilon_1']#initial shock
		

		x_w=self.grid_dict['x_w']
		x_m=self.grid_dict['x_m']
		x_k=self.grid_dict['x_k']
		x_wmk=self.grid_dict['x_wmk']

		
		#Sample size
		ngrid=theta0.shape[0]

		agech=np.reshape(agech,ngrid)

		
		#Set number of choices at t-1
		Jt=6

		hours=np.zeros(ngrid)
		childcare=np.zeros(ngrid)
		
		self.change_util(self.param,ngrid,x_w,x_m,x_k,passign,
			nkids0,married0,hours,childcare,agech,
			self.hours_p,self.hours_f,self.wr,self.cs,self.ws)
		wage0=self.model.waget(periodt,epsilon_1)
		free0=self.model.q_prob()
		price0=self.model.price_cc()


		#I save interpolating instances here
		emax_inst=[]
		#I save emaxT(T-1) here
		emax_t1=np.zeros((ngrid,Jt))


		#Loop: choice at t-1
		
		for jt in range(0,Jt):

						
			#choices at t-1
			if jt<=2:
				if jt==0:
					hours_aux=0
				elif jt==1:
					hours_aux=self.hours_p
				elif jt==2:
					hours_aux=self.hours_f

				hours=np.full(ngrid,hours_aux,dtype=float)
				childcare=np.zeros(ngrid)

			else:
				if jt==3:
					hours_aux=0
				elif jt==4:
					hours_aux=self.hours_p
				elif jt==5:
					hours_aux=self.hours_f

				hours=np.full(ngrid,hours_aux,dtype=float)
				childcare=np.ones(ngrid)

			#I get these to compute theta_t1
			dincome0=self.model.dincomet(periodt-1,hours,wage0,married0,nkids0)['income']
			consumption0=self.model.consumptiont(periodt-1,hours,childcare,dincome0,married0,
				nkids0,wage0,free0,price0)['income_pc']
			

			J=6 #number of choides in the inner loop

			#Here I save array of Ut by schock/choice (at T)
			u_vec=np.zeros((ngrid,self.D,J))
			

			#Montecarlo integration: loop over shocks by choice at t (hours and childcare)
			for j,i in itertools.product(range(0,J),range(0,self.D)):
				#for i in range(0,D):
				
				#Computing states at t
				self.change_util(self.param,ngrid,x_w,x_m,x_k,
					passign,nkids0,married0,hours,childcare,agech,
					self.hours_p,self.hours_f,self.wr,self.cs,self.ws)
				
				
				married_t1=self.model.marriaget(periodt,married0)
				married_t1=np.reshape(married_t1,(ngrid,1))
				nkids_t1=self.model.kidst(periodt,np.reshape(nkids0,(ngrid,1)),
					married0)+nkids0 #previous kids + if they have a kid next period
				epsilon_t1=self.model.epsilon(epsilon_1)
				wage_t1=self.model.waget(periodt,epsilon_t1)
				free_t1=self.model.q_prob()
				price_t1=self.model.price_cc()
				#income at t-1 to compute theta_t
				theta_t1=self.model.thetat(periodt-1,theta0,hours,childcare,consumption0) #theta at t+1 uses inputs at t

				# Possible decision at t
				if j<=2:
					if j==0:
						hours_aux=0
					elif j==1:
						hours_aux=self.hours_p
					elif j==2:
						hours_aux=self.hours_f
					hours_t1=np.full(ngrid,hours_aux,dtype=float)
					childcare_t1=np.zeros(ngrid)
				else:
					if j==3:
						hours_aux=0
					elif j==4:
						hours_aux=self.hours_p
					elif j==5:
						hours_aux=self.hours_f
					hours_t1=np.full(ngrid,hours_aux,dtype=float)
					childcare_t1=np.ones(ngrid)

				
				#Instance at period t
				self.change_util(self.param,ngrid,x_w,x_m,x_k,
					passign,nkids_t1,married_t1,hours_t1,childcare_t1,agech,
					self.hours_p,self.hours_f,self.wr,self.cs,self.ws)

				#Current-period utility at t
				u_vec[:,i,j]=self.model.simulate(periodt,wage_t1,free_t1,price_t1,theta_t1) 

				#getting next-period already computed emaxt+1
				data_int_ex=np.concatenate(( np.reshape(np.log(theta_t1),(ngrid,1)), 
					np.reshape(nkids_t1,(ngrid,1)),np.reshape(married_t1,(ngrid,1)),
					np.reshape(np.square(np.log(theta_t1)),(ngrid,1)),
					np.reshape(passign,(ngrid,1)), 
					np.reshape(epsilon_t1,(ngrid,1)),
					np.reshape(np.square(epsilon_t1),(ngrid,1)),
					x_wmk ), axis=1)

				#
				#obtaining emaxT+1
				#Emax instance of t+1 for choice j
				emax_inst_choice=emax_t1_ins[j]
				betas_t1_choice=emax_inst_choice.betas()
				emax_t1_choice=emax_inst_choice.int_values(data_int_ex,betas_t1_choice)

				#Value function at t.
				u_vec[:,i,j]=u_vec[:,i,j]+0.86*emax_t1_choice

				

			#obtaining max over choices by random shock/choice at t-1. Young vs old
			max_ut=np.zeros((ngrid,self.D))
			max_ut[agech<=6,:]=np.max(u_vec[agech<=6,:,:],axis=2) #young
			max_ut[agech>6,:]=np.max(u_vec[agech>6,:,0:3],axis=2) #old

			

			#This is the emax for a given choice at t-1
			av_max_ut=np.average(max_ut,axis=1)

			#Data for interpolating emaxt (states at t-1)
			data_int=np.concatenate(( np.reshape(np.log(theta0),(ngrid,1)), 
				np.reshape(nkids0,(ngrid,1)),np.reshape(married0,(ngrid,1)),
				np.reshape(np.square(np.log(theta0)),(ngrid,1)),
				np.reshape(passign,(ngrid,1)), 
				np.reshape(epsilon_1,(ngrid,1)),#current period shock
				np.reshape(np.square(epsilon_1),(ngrid,1)),
				x_wmk ), axis=1)

			
			#Emax value for a given choice
			emax_t1[:,jt]=av_max_ut

			#saving instances

			if jt==0:
				emax_inst=[int_linear.Int_linear(data_int,av_max_ut)]
			else:
				emax_inst.append(int_linear.Int_linear(data_int,av_max_ut))





		#the instance with the eitc function and emax values

		return [emax_inst,emax_t1]


	def recursive(self):
		"""
		Recursively computes a series of interpolating instances
		Generates a dictionary with the emax instances

		There is a sequence of Emax for each child age (0-11)
		

		"""	
		
		
		def emax_gen(j):
			
			for t in range(j,0,-1):
				
				if t==j:#last period
					emax_bigt_ins=self.emax_bigt(j)
					
					
					emax_dic={'emax'+str(t): emax_bigt_ins[0]}
					emax_values={'emax'+str(t): emax_bigt_ins[1]}
				elif t==j-1: #at T-1
					emax_t1_ins=self.emax_t(t,j,emax_bigt_ins[0])
					
					
					emax_dic['emax'+str(t)]=emax_t1_ins[0]
					emax_values['emax'+str(t)]=emax_t1_ins[1]
					
				else:
					emax_t1_ins=self.emax_t(t,j,emax_t1_ins[0])
					
					
					emax_dic['emax'+str(t)]=emax_t1_ins[0]
					emax_values['emax'+str(t)]=emax_t1_ins[1]

			return [emax_dic,emax_values]

		pool = ProcessPool(nodes=10)

		#7: old child (11 years old) solves for 7 emax 
		#19: young child (0 years old) solves for 18 emax
		list_emax = pool.map(emax_gen,range(8,18))
		pool.close()
		pool.join()
		pool.clear()
		
		
		"""
		
		
		list_emax = []
		for j in range(7,19):
			print 'Im in emax j ', j
			
			for t in range(j,0,-1):
				print 'In period t ', t
				
				if t==j:#last period
					emax_bigt_ins=self.emax_bigt(j)
					emax_dic={'emax'+str(t): emax_bigt_ins[0]}
					emax_values={'emax'+str(t): emax_bigt_ins[1]}
				elif t==j-1: #at T-1
					emax_t1_ins=self.emax_t(t,j,emax_bigt_ins[0])
					emax_dic['emax'+str(t)]=emax_t1_ins[0]
					emax_values['emax'+str(t)]=emax_t1_ins[1]
					
				else:
					emax_t1_ins=self.emax_t(t,j,emax_t1_ins[0])
					emax_dic['emax'+str(t)]=emax_t1_ins[0]
					emax_values['emax'+str(t)]=emax_t1_ins[1]

			list_emax.append([emax_dic,emax_values])

		
		
		"""
		

		
		return list_emax






		

















