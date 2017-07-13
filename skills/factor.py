"""
This class estimates a factor model from ordered measures.

Inputs:
n: sample size
n_m: number of measures
n_r: number of points in the multinomial (cutoffs+1)

ymatrix: array of measures
kappa_m: (n_r-1)*n_m (initial values for cutoffs in the measurement system)
lambda_m: n_m-1 (initial value for factor loadings in the measurement system)

The number of parameters in the cdf of theta

2+2+2=(probabilities, means, variances)
probs: prob of mixtures
mus: means
vars: variances

"""
from __future__ import division #omit for python 3.x
import numpy as np
import pandas as pd
from numba import jit
import sys, os
from scipy import stats
from scipy.optimize import minimize
from scipy.optimize import fmin_bfgs
from scipy.stats import norm
from pathos.multiprocessing import ProcessPool


class Factor:
	def __init__(self,n,n_m,n_r,ymatrix,d_RA,lambda_m,kappa_m,prob_0,mu_0,vars_theta_0,
		prob_1,mu_1,vars_theta_1):
		self.n,self.n_m,self.n_r=n,n_m,n_r
		self.ymatrix,self.d_RA=ymatrix,d_RA
		self.lambda_m=lambda_m
		self.kappa_m=kappa_m
		self.prob_0,self.mu_0,self.vars_theta_0=prob_0,mu_0,vars_theta_0
		self.prob_1,self.mu_1,self.vars_theta_1=prob_1,mu_1,vars_theta_1


	def ll(self,param1):
		"""
		Takes initial vector of parameters and computes the likelihood
		"""
		lambda_m=np.ones((self.n_m,1))
		lambda_m[1:(self.n_m),0]=param1[0:(self.n_m-1)] #factor loadings
		kappa_m=np.zeros((self.n_r-1,self.n_m)) #4 cutoffs x # measures
        
		ind  = self.n_m-1

		for v in range(self.n_m):#the measure loop
			kappa_m[:,v]=param1[ind:ind+(self.n_r-1)]#add 4 cutoffs
			ind = ind + (self.n_r-1)

		#these parameters change by treatment status [control,treatment]
		
		#control
		p = []

		p.append(np.exp(param1[ind])/(1+np.exp(param1[ind]))) #to ensure 0<p<1
		p_aux = param1[ind].copy()

		ind = ind+1
		mu=[np.array( [param1[ind], -p_aux*param1[ind]/(1-p_aux)])]#mean of theta normalized to 0
				
		ind = ind +1
		sig_theta=[np.exp(param1[ind:ind+2])]

		
		#treatment
		ind = ind + 2

		p.append(np.exp(param1[ind])/(1+np.exp(param1[ind]))) #to ensure 0<p<1
		p_aux = param1[ind].copy()

		ind = ind+1
		mu.append(np.array( [param1[ind], param1[ind+1]]))#mean of theta not normalized to 0

		ind = ind +2

		sig_theta.append(np.exp(param1[ind:ind+2]))

		#Approximating integral
		#Change this line if you want to modify accuracy of approx.
		deg=8
		xi_w=np.polynomial.hermite.hermgauss(deg)

		xi=np.zeros((self.n,deg))
		w=np.zeros((self.n,deg))
		for i in range(self.n):
			xi[i,:]=xi_w[0].T
			w[i,:]=xi_w[1].T

		#this is total likelihood
		int_p = np.zeros(self.n)
		for dra in range(2): #the treatment indicator loop

			boo_ra = self.d_RA[:,0] == dra
			
			for l in range(2):#the mixture loop
				
			
				#COV
				x=xi[boo_ra,:]*np.sqrt(2*sig_theta[dra][l])+mu[dra][l]

				A=np.zeros((x.shape[0],deg))        
	                    
				for k in range(deg):#the quadrature (integral) loop

					for j in range(self.n_m):#the measures loop

						for v in range(self.n_r):#the choice loop

							d = self.ymatrix[boo_ra,j] == v+1

							if v==0:
								prob = norm.cdf(kappa_m[v,j] - lambda_m[j,:]*x[:,k],0,1)**d
								f_aux = prob

							elif (v>0) & (v<self.n_r-1):
								
								prob  = (norm.cdf(kappa_m[v,j] - lambda_m[j,:]*x[:,k],0,1) - norm.cdf(kappa_m[v-1,j] - lambda_m[j,:]*x[:,k],0,1))**d
								f_aux = f_aux*prob
							else:
								prob  = (1 - norm.cdf(kappa_m[v-1,j] - lambda_m[j,:]*x[:,k],0,1))**d
								f_aux = f_aux*prob
						if j == 0:
							f=f_aux
	          
						else:
							f=f*f_aux

					A[:,k]=f
            
					#gauss-H weight
					A=A*w[boo_ra]
            
				#approx integral
				inte=np.sum(A,axis=1)*np.pi**(-0.5)
	            
				#prob of mixture
				if l==0:
					
					int_p[boo_ra]=inte*p[dra]
				else:
					int_p[boo_ra]=int_p[boo_ra]+inte*(1-p[dra])
        
		return -np.sum(np.log(int_p))/10000


	def optimizer(self):

		kappas = self.kappa_m.T.reshape(((self.n_r-1)*self.n_m,1))
		
		beta0 = np.concatenate((self.lambda_m,kappas,np.log(self.prob_0/(1-self.prob_0)),
			self.mu_0,np.log(self.vars_theta_0),
			np.log(self.prob_1/(1-self.prob_1)),self.mu_1,np.log(self.vars_theta_1))
		,axis=0)

		#here we go
		opt = minimize(self.ll, beta0,  method='BFGS', options={'gtol': 1e-5, 'disp': True}) 

		return opt



