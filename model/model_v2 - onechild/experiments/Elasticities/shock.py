"""
This class modifies the wage offer (increases wage by shock(%)
"""
from __future__ import division #omit for python 3.x
import numpy as np
import itertools
from numba import jit
import sys, os
from scipy import stats
from scipy import interpolate
#sys.path.append("C:\\Users\\Jorge\\Dropbox\\Chicago\\Research\\Human capital and the household\]codes\\model")
sys.path.append("/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model/simulate_sample")
from utility import Utility
import gridemax
import int_linear
import time

class Shock(Utility):
	"""
	Modifies wage offer process
	"""

	def __init__(self,param,N,xwage,xmarr,xkid,ra,
		nkids0,married0,hours,cc,age_t0,hours_p,hours_f,wr,cs,ws):
		"""
		introduces shock
		"""
		Utility.__init__(self,param,N,xwage,xmarr,xkid,ra,
			nkids0,married0,hours,cc,age_t0,hours_p,hours_f,wr,cs,ws)

	def load(self):
		"""
		Loads shock (number)
		"""
		return np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/NH/shock.npy')

	def wage_init(self,epsilon_t):
		"""
		Initial shock to wages
		"""
		

		periodt = 0
		lt = np.zeros((self.N,1)) + periodt 

		xw=np.concatenate((np.reshape(self.xwage[:,0],(self.N,1)), #higrade
					lt,
					np.reshape(self.xwage[:,1],(self.N,1)),),axis=1) #constant

		betas=self.param.betaw[0:-2,0] #everything but rho and variance

		#recovering shock
		shock = self.load()

		return {'wage':np.exp( np.dot(xw,betas)+ epsilon_t )*(1+shock)}

	def waget(self,periodt,epsilon):
		"""
		Computes w (hourly wage) for periodt

		
		This method returns t=0,1...,8 
		(at t=0 we don't observe wages for those who do not work)
		(that's why I need to simulate w0 instead of just using observed one)

		lnw =beta1*age + beta1*age2 + beta3d_HS + beta4*log(periodt)
		 beta5 +  e

		 where e = rho*e(-1) + nu

		 nu iid normal

		"""

		lt =  np.zeros((self.N,1)) + periodt

		xw=np.concatenate((np.reshape(self.xwage[:,0],(self.N,1)), #HS
					lt,
					np.reshape(self.xwage[:,1],(self.N,1)),),axis=1) #constant

		betas=self.param.betaw[0:-2,0] #everything but rho and variance

		#recovering shock
		shock = self.load()

		return np.exp( np.dot(xw,betas)+ epsilon )*(1+shock)
