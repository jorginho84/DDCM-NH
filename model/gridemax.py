from __future__ import division #omit for python 3.x
import numpy as np
import pandas as pd
import itertools
import sys, os
from scipy import stats
import matplotlib.pyplot as plt
import itertools

def grid():
	"""
	Defines a grid of state variable to compute the Emax interpolation

	"""

	#MOdify these parameters to set the grid length
	#ACA voy: set a dense grid for age/nkids near the mean

	#Lists of nkids,married,theta
	nkids_grid=np.linspace(0,5,2).astype(int).tolist() #approx 95% of obs are in this region
	married_grid=[i for i in range(0,2)]
	theta_grid=np.linspace(0.01,3,5).tolist()
	wage_grid=np.linspace(1,50,6).tolist()
	passign_grid=[i for i in range(0,2)]
	dhs_grid=[i for i in range(0,2)]
	age_grid=np.linspace(18,45,5).astype(int).tolist() #approx 95% of obs are in this region
	
	

	iterables=[nkids_grid,theta_grid,married_grid,wage_grid, passign_grid, dhs_grid,age_grid]
	#copy the above names here
	keys=['nkids_grid', 'theta_grid','married_grid','wage_grid' , 'passign_grid', 'dhs_grid', 'age_grid']

	#Array of combinations (cartesian product)
	it=1
	for t in itertools.product(*iterables):
	    
	    if it==1:
	    	grid=np.reshape(np.array(t),(1,len(iterables)))
	    else:
	    	grid=np.concatenate((grid,np.reshape(np.array(t),(1,len(iterables)))),axis=0)

	    it+=1


	print 'the grid has size', grid.shape

	#assign columns to names (dict)
	dict_grid=dict(zip(keys,grid.T))

	#Generate X's (theta0,nkids0,married0,x_m,x_k,x_w)
	theta0=np.array(dict_grid['theta_grid'])
	nkids0=np.reshape(np.array(dict_grid['nkids_grid']).astype(int),(grid.shape[0],1))
	married0=np.reshape(np.array(dict_grid['married_grid']).astype(int),(grid.shape[0],1) )
	passign=np.reshape(np.array(dict_grid['passign_grid']).astype(int),(grid.shape[0],1) )
	wage0=np.array(dict_grid['wage_grid'])
	d_hs=np.reshape(np.array(dict_grid['dhs_grid']).astype(int),(grid.shape[0],1) )
	age=np.reshape(np.array(dict_grid['age_grid']).astype(int),(grid.shape[0],1) )
	

	

	#Shuffling variables 
	#to avoid collinearity on interpolation rutines
	for var in [passign,theta0,nkids0,married0,wage0,d_hs,age]:
		np.random.shuffle(var) 

	#follow the same order as master_sim (line 71)
	ngrid=theta0.shape[0]
	age2=np.square(age)
	x_w=np.concatenate(( age,age2,d_hs,np.ones((ngrid,1)) ),axis=1)
	x_m=np.concatenate(( age,d_hs,np.ones((ngrid,1)) ),axis=1)
	x_k=np.concatenate(( age,age2,np.ones((ngrid,1)) ),axis=1)
	x_wmk=np.concatenate(( age,age2,d_hs,np.ones((ngrid,1)) ),axis=1)


	return { 'passign': passign,'theta0': theta0, 'nkids0': nkids0 , 'married0': married0, 
		'wage0': wage0, 'x_w': x_w, 'x_m':x_m, 'x_k': x_k, 'x_wmk': x_wmk }

