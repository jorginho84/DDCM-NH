"""
This class modifies the production function
"""
#from __future__ import division #omit for python 3.x
import numpy as np
import itertools
from numba import jit
import sys, os
from scipy import stats
from scipy import interpolate
#sys.path.append("C:\\Users\\Jorge\\Dropbox\\Chicago\\Research\\Human capital and the household\]codes\\model")
sys.path.append("/home/jrodriguez/NH_HC/codes/simulate_sample")
from utility import Utility
import gridemax
import int_linear
import time


class Prod2(Utility):
	"""
	This class modifies the production function
	"""

	def __init__(self,param,N,xwage,xmarr,xkid,ra,
		nkids0,married0,hours,cc_a,cc_b,age_t0a,age_t0b,d_childa,
		d_childb,hours_p,hours_f,wr,cs,ws):
		"""	
		ec, el: E[log()] of consumption and leisure from original (simulated)
		data
		"""
		Utility.__init__(self,param,N,xwage,xmarr,xkid,ra,
			nkids0,married0,hours,cc_a,cc_b,age_t0a,age_t0b,d_childa,
		d_childb,hours_p,hours_f,wr,cs,ws)
	
	def elec(self):
		"""
		This function recovers expected values to normalize the constant in the prod function
		"""
		ec = np.load('/home/jrodriguez/NH_HC/results/Model/experiments/NH/ec.npy')
		el_a = np.load('/home/jrodriguez/NH_HC/results/Model/experiments/NH/el_a.npy')
		el_b = np.load('/home/jrodriguez/NH_HC/results/Model/experiments/NH/el_b.npy')
		ecc_a = np.load('/home/jrodriguez/NH_HC/results/Model/experiments/NH/ecc_a.npy')
		ecc_b = np.load('/home/jrodriguez/NH_HC/results/Model/experiments/NH/ecc_b.npy')
		e_age_a = np.load('/home/jrodriguez/NH_HC/results/Model/experiments/NH/e_age_a.npy')
		e_age_b = np.load('/home/jrodriguez/NH_HC/results/Model/experiments/NH/e_age_b.npy')
		return [ec, el_a,el_b, ecc_a,ecc_b, e_age_a,e_age_b]

	def thetat(self,periodt,theta0,h,cc_a,cc_b,ct):
		"""
		Computes theta at period (t+1) (next period)
		t+1 goes from 1-8
		
		Inputs must come from period t

		"""
		theta0_a = theta0[0].copy()
		theta0_b = theta0[1].copy()

		#age of child
		agech_a = np.zeros((self.N))
		agech_b = np.zeros((self.N))
		agech_a[self.d_childa[:,0] == 1] = self.age_t0a[self.d_childa[:,0] == 1] + periodt
		agech_b[self.d_childb[:,0] == 1] = self.age_t0b[self.d_childb[:,0] == 1] + periodt

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

		tch_a = np.zeros(self.N)
		tch_b = np.zeros(self.N)
		boo_p = h == self.hours_p
		boo_f = h == self.hours_f
		boo_u = h == 0

		tch_a[agech_a<=5] = cc_a[agech_a<=5]*(168 - self.hours_f) + (1-cc_a[agech_a<=5])*(168 - h[agech_a<=5] ) 
		tch_a[agech_a>5] = 133 - h[agech_a>5] 
		tch_a=np.log(tch_a)

		tch_b[agech_b<=5] = cc_b[agech_b<=5]*(168 - self.hours_f) + (1-cc_b[agech_b<=5])*(168 - h[agech_b<=5] ) 
		tch_b[agech_b>5] = 133 - h[agech_b>5] 
		tch_b=np.log(tch_b)
		
						
		#Parameters
		gamma1=self.param.gamma1
		gamma2=self.param.gamma2
		gamma3=self.param.gamma3
		tfp=self.param.tfp
		
		theta1_a=np.zeros(self.N)
		theta1_b=np.zeros(self.N)

		#adjustment for E[theta = 0]
		alpha_a = - ecel[0][periodt]*gamma2 - ecel[1][periodt]*gamma3
		alpha_b = - ecel[0][periodt]*gamma2 - ecel[2][periodt]*gamma3

		#The production of HC: young, cc=0
		boo_age_a=agech_a<=5
		boo_age_b=agech_b<=5
		theta1_a = tfp*cc_a*boo_age_a + gamma1*np.log(theta0_a) + gamma2*incomepc +	gamma3*tch_a + alpha_a
		theta1_b = tfp*cc_b*boo_age_b + gamma1*np.log(theta0_b) + gamma2*incomepc +	gamma3*tch_b + alpha_b

		#When child A/B is not present
		theta1_a[self.d_childa[:,0] == 0] = 0
		theta1_b[self.d_childb[:,0] == 0] = 0
		
		return [np.exp(theta1_a),np.exp(theta1_b)]