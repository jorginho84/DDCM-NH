"""
This class modifies the production function
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


class Prod2(Utility):
	"""
	This class modifies the production function
	"""

	def __init__(self,param,N,xwage,xmarr,xkid,ra,
		nkids0,married0,hours,cc,age_t0,hours_p,hours_f,wr,cs,ws):
		"""	
		ec, el: E[log()] of consumption and leisure from original (simulated)
		data
		"""
		Utility.__init__(self,param,N,xwage,xmarr,xkid,ra,
			nkids0,married0,hours,cc,age_t0,hours_p,hours_f,wr,cs,ws)
	
	def elec(self):
		"""
		This function recovers ec and el
		"""
		ec = np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/NH/ec.npy')
		el = np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/NH/el.npy')
		return [ec, el]

	def thetat(self,periodt,theta0,h,cc,ct):
		"""
		Computes theta at period (t+1) (next period)
		t+1 goes from 1-8
		
		Inputs must come from period t

		"""
		#age of child
		agech=np.reshape(self.age_t0,(self.N)) + periodt

		#recovering ec and el
		ecel = self.elec()

		#log consumption pc
		incomepc_aux=np.log(ct)
		incomepc=incomepc_aux - ecel[0][periodt]
		
		#log leisure (T=148 hours a week)
		leisure=np.log(148-h) - ecel[1][periodt]

		#random shock
		omega=self.param.sigmatheta*np.random.randn(self.N)
		
				
		#Parameters
		gamma1=self.param.gamma1
		gamma2=self.param.gamma2
		tfp=self.param.tfp
		
		theta1=np.zeros(self.N)

		#The production of HC: young, cc=0
		boo=(agech<=6) & (cc==0)
		theta1[boo] = gamma1[0]*np.log(theta0[boo]) + gamma2[0]*incomepc[boo] +\
		(1 - gamma1[0] - gamma2[0] )*leisure[boo] + omega[boo]

		#The production of HC: young, cc=1
		boo=(agech<=6) & (cc==1)
		theta1[boo] = gamma1[0]*np.log(theta0[boo]) + gamma2[0]*incomepc[boo] +\
		(1 - gamma1[0] - gamma2[0] )*leisure[boo] + tfp + omega[boo]

		#The production of HC: old
		boo=(agech>6)
		theta1[boo] = gamma1[1]*np.log(theta0[boo]) + gamma2[1]*incomepc[boo] +\
		(1 - gamma1[1] - gamma2[1] )*leisure[boo] + omega[boo]

		return np.exp(theta1)