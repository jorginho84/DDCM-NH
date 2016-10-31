
from __future__ import division #omit for python 3.x
import numpy as np


class Int_linear:
	"""
	Implements OLS linear interpolation

	"""
	def __init__(self,x,y):
		self.x,self.y=x,y

	def betas(self):
		"""
		Calculates betas
		"""
		xx=np.dot(np.transpose(self.x),self.x)
		xy=np.dot(np.transpose(self.x),self.y)
		return np.dot(np.linalg.inv(xx),xy)

	def int_values(self,x,betas):
		"""
		Takes betas and computes interpolated values for 
		given x's.
		x is an array nxk
		betas: array kx1
		"""

		
		return np.dot(x,betas)
	