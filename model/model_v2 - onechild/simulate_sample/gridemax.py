#from __future__ import division #omit for python 3.x
import numpy as np
import pandas as pd
import itertools
import sys, os
from scipy import stats
import matplotlib.pyplot as plt
import itertools

def grid(n_grid):
	"""
	Defines a grid of state variable to compute the Emax interpolation
	
	"""
	"""
	#Lists of state variables (that determine emax)
	married_grid = [i for i in range(0,2)]
	passign_grid = [i for i in range(0,2)]
	hs_grid = [i for i in range(0,2)]
			
	iterables=[nkids_grid,married_grid, passign_grid,age_grid,hs_grid]
	#copy the names here
	keys=['nkids_grid','married_grid','passign_grid','hs_grid']

	#Array of combinations (cartesian product)
	it=1
	for t in itertools.product(*iterables):
	    
	    if it==1:
	    	grid=np.reshape(np.array(t),(1,len(iterables)))
	    else:
	    	grid=np.concatenate((grid,np.reshape(np.array(t),(1,len(iterables)))),axis=0)

	    it+=1


	print ('the grid has size', grid.shape)

	#assign columns to names (dict)
	dict_grid=dict(zip(keys,grid.T))

	
	married0 = np.reshape(np.array(dict_grid['married_grid']).astype(float),(grid.shape[0],1) )
	passign = np.reshape(np.array(dict_grid['passign_grid']).astype(float),(grid.shape[0],1) )
	d_hs = np.reshape(np.array(dict_grid['hs_grid']).astype(float),(grid.shape[0],1) )
	"""
	
	print ('the grid has size', n_grid)
	d_hs = np.random.randint(0,2,(n_grid,1))
	passign = np.random.randint(0,2,(n_grid,1))
	married0 = np.random.randint(0,2,(n_grid,1))
	theta0 = np.random.uniform(0.01,2,(n_grid,1))
	epsilon_1 = np.random.uniform(-2,2,(n_grid,1))
	agech = np.random.randint(0,11,(n_grid,1))
	age = np.random.randint(18,46,(n_grid,1))
	nkids0 = np.random.randint(1,7,(n_grid,1))



	#Shuffling variables 
	#to avoid collinearity on interpolation rutines
	#for var in [nkids0,married0,passign,d_hs,age,agech,epsilon_1]:
	#	np.random.shuffle(var) 

	#follow the same order as master_sim (line 71)
	#ngrid=theta0.shape[0]
	age2=np.square(age)
	x_w=np.concatenate(( d_hs,np.ones((n_grid,1)) ),axis=1)
	x_m=np.concatenate(( age,np.ones((n_grid,1)) ),axis=1)
	x_k=np.concatenate(( age,age2,np.ones((n_grid,1)) ),axis=1)
	x_wmk=np.concatenate(( age,age2,d_hs,np.ones((n_grid,1)) ),axis=1)

	
	return { 'passign': passign,'theta0': theta0,'nkids0': nkids0,
		'married0': married0,'x_w': x_w, 'x_m':x_m, 'x_k': x_k, 'x_wmk': x_wmk,
		'agech':agech,'epsilon_1':epsilon_1 }

