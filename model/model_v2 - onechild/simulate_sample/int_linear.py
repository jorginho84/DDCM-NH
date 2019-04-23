
#from __future__ import division #omit for python 3.x
import numpy as np


class Int_linear:
	"""
	Implements OLS linear interpolation

	"""
	def __init__(self):
		self.x = 0

	def betas(self,x,y):
		"""
		Calculates betas
		"""
		xx=np.dot(np.transpose(x),x)
		xy=np.dot(np.transpose(x),y)
		return np.dot(np.linalg.inv(xx),xy)

	def int_values(self,x,betas):
		"""
		Takes betas and computes interpolated values for 
		given x's.
		x is an array nxk
		betas: array kx1
		"""

		
		return np.dot(x,betas)
	