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
		This function recovers expected values to normalize the constant in the prod function
		"""
		ec = np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/NH/ec.npy')
		el = np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/NH/el.npy')
		ecc = np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/NH/el.npy')
		e_age = np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/NH/e_age.npy')
		return [ec, el, ecc, e_age]

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
		incomepc=np.log(ct)
		
		
		#log leisure (T=148 hours a week)
		#log time w child (T=148 hours a week)
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
		
		theta1=np.zeros(self.N)

		
		#The production of HC: young, cc=0
		boo_age=agech<=5
		theta1 = tfp*cc*boo_age + gamma1*np.log(theta0) + gamma2*incomepc +	gamma3*tch 

		#adjustment for E[theta = 0]
		alpha = - ecel[3][periodt]*ecel[2][periodt]*tfp - ecel[0][periodt]*gamma2 - ecel[1][periodt]*gamma3

		return np.exp(theta1)