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
sys.path.append("/home/jrodriguez/NH_HC/codes/model_v2/simulate_sample")
from utility import Utility
import gridemax
import int_linear
import time


class Prod2(Utility):

	"""
	This class modifies the constant in the production function
	"""

	def __init__(self,param,N,xwage,xmarr,xkid,ra,
		nkids0,married0,hours,cc,age_t0,hours_p,hours_f,wr,cs,ws):

		"""	
		ec, el: E[log()] of consumption and leisure from original (simulated)
		data
		"""

		Utility.__init__(self,param,N,xwage,xmarr,xkid,ra,
			nkids0,married0,hours,cc,age_t0,hours_p,hours_f,wr,cs,ws)

	def thetat(self,periodt,theta0,h,cc,ct):
		"""
		Computes theta at period (t+1) (next period)
		t+1 goes from 1-8
		
		Inputs must come from period t
		"""
		#age of child
		agech=np.reshape(self.age_t0,(self.N)) + periodt

		#log consumption pc
		incomepc=np.log(ct)
		
		#log time w child (T=168 hours a week, -35 for older kids)
		tch = np.zeros(self.N)
		boo_p = h == self.hours_p
		boo_f = h == self.hours_f
		boo_u = h == 0

		tch[agech<=5] = cc[agech<=5]*(168 - self.hours_f) + (1-cc[agech<=5])*(168 - h[agech<=5] ) 
		tch[agech>5] = 133 - h[agech>5] 
		tch=np.log(tch)
	
				
		#Parameters
		gamma1=self.param.gamma1
		gamma2=self.param.gamma2
		gamma3=self.param.gamma3
		tfp=self.param.tfp
		
				
		#The production of HC: (young, cc=0), (young,cc1), (old)
		boo_age=agech<=5
		theta1 = self.param.tfp*cc*boo_age + self.param.gamma1*np.log(theta0) + self.param.gamma2*incomepc + self.param.gamma3*tch
		
		return np.exp(theta1)


