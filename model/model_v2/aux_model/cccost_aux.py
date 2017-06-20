"""
execfile('cccost_aux.py')
This file finds the weibull parameters consistent with the variance of the sample
and mean as reported in mdrc reports of child care cost

"""

from __future__ import division #omit for python 3.x
import numpy as np
import pandas as pd
import pickle
import itertools
import sys, os
import scipy
from scipy import stats
#from scipy.optimize import minimize
from scipy.optimize import fsolve


def equations(p):
	lambd,kapa=p
	return (lambd*scipy.special.gamma(1 + 1/kapa) - 750*12,  
		(lambd**2)*(scipy.special.gamma(1 + 2/kapa) - (scipy.special.gamma(1 + 1/kapa))**2) - 12*192**2)


lambd, kapa = fsolve(equations,(1,1))

print equations((lambd, kapa))