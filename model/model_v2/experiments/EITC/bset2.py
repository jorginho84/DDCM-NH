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



"""
This class modifies the budget set
"""

class Budget(Utility):
	"""
	This class modifies the income and consumption processes
	"""
	def __init__(self,param,N,xwage,xmarr,xkid,ra,
		nkids0,married0,hours,cc,age_t0,hours_p,hours_f,wr,cs,ws):
		"""
		wr, cs, ws control working requirements, child care subsidy,
		and wage subsidy parameters
		"""
		Utility.__init__(self,param,N,xwage,xmarr,xkid,ra,
			nkids0,married0,hours,cc,age_t0,hours_p,hours_f,wr,cs,ws)

	def dincomet(self, periodt,hours,wage,marr,kid):
		"""
		Computes annual disposable income given weekly hours worked, hourly wage,
		marital status and number of kids. 
		Everyone receives EITC. Only the treatment group has NH. NH ends between t=2 and t=3
		
		EITC parameters: in the self.eitc list

		6r1,r2: phase-in and phase-out rates
		b1,b2: minimum income for max credit/beginning income for phase-out
		state_eitc=fraction of federal eitc

		""" 
		
		#from hourly wage to annual earnings
		pwage=np.reshape(hours,self.N)*np.reshape(wage,self.N)*52

		#To nominal prices (2003 prices)
		pwage=pwage/(self.param.cpi[8]/self.param.cpi[periodt])

		#the EITC parameters
		dic_eitc=[self.param.eitc['EITC'][periodt]]

		#The AFDC parameters
		afdc_param=self.param.afdc[0]

		#The SNAP parameters
		snap_param=self.param.snap[0]

		#family size
		nfam = np.ones(self.N) + kid[:,0] + marr[:,0]

		#EITC parameters
		r1 = []
		r2 = []
		b1 = []
		b2 = []
		state_eitc = []

		#parameters of the EITC treatment
		for nn in range(1,4):
			r1.append(dic_eitc[0]['r1_' + str(nn)])
			r2.append(dic_eitc[0]['r2_'+ str(nn)])
			b1.append(dic_eitc[0]['b1_'+ str(nn)])
			b2.append(dic_eitc[0]['b2_'+ str(nn)])
			state_eitc.append(dic_eitc[0]['state_eitc'+ str(nn)])

		
		#Obtaining individual's disposable income from EITC
		eitc_fed=np.zeros(self.N)
		eitc_state=np.zeros(self.N)
		
		for nn in range(0,3):

			if nn<=2:
				kid_boo=kid[:,0]==nn+1
			else:
				kid_boo=kid[:,0]>=nn+1
			
			eitc_fed[(pwage<b1[nn]) & (kid_boo) ]=r1[nn]*pwage[(pwage<b1[nn]) & (kid_boo)]
			eitc_fed[(pwage>=b1[nn]) & (pwage<b2[nn]) & (kid_boo)]=r1[nn]*b1[nn]
			eitc_fed[(pwage>=b2[nn]) & (kid_boo)]=np.maximum(r1[nn]*b1[nn]-r2[nn]*(pwage[(pwage>=b2[nn]) & (kid_boo)]-b2[nn]),np.zeros(pwage[(pwage>=b2[nn]) & (kid_boo)].shape[0]))
			eitc_state[kid_boo]=state_eitc[nn]*eitc_fed[kid_boo]

		dincome_eitc=pwage+eitc_fed+eitc_state

		##Obtaining NH income supplement#

		if periodt<=2:

			#the wage subsidy
			wsubsidy=np.zeros(self.N)
			wsubsidy[pwage<=8500]=0.25*pwage[pwage<=8500]
			wsubsidy[pwage>8500]=3825-0.2*pwage[pwage>8500]
			wsubsidy[wsubsidy<0]=0

			#Child allowance
			

			#Fade-out level (3 possible periods)
			bar_e_extra=[300,1200,2100] #for a family of four children or more
			bar_e=np.zeros(self.N)
			bar_e[kid[:,0]<=4]=30000
			bar_e[kid[:,0]>4]=30000+bar_e_extra[periodt]

			#Maximum level of CA
			xstar=np.zeros(self.N)
			xstar[kid[:,0]==1]=1600
			xstar[kid[:,0]==2]=1600 + 1500
			xstar[kid[:,0]==3]=1600 + 1500 + 1400
			xstar[kid[:,0]>=4]=1600 + 1500 + 1400 + 1300
			
			#r_e: phase-out rate
			beta_aux=xstar/(8500-bar_e)

			#per-child allowance
			childa=np.zeros(self.N) 
			childa[pwage<=8500]=xstar[pwage<=8500].copy()
			childa[pwage>8500]=xstar[pwage>8500] - beta_aux[pwage>8500]*(pwage[pwage>8500] - 8500)
			childa[childa<0]=0

			#disposable income
			dincome_nh=pwage+wsubsidy+childa
			
			if self.ws==1:
				nh_supp=dincome_nh-dincome_eitc
				if self.wr==1:
					nh_supp[(self.ra==0) | (hours<self.hours_f) | (nh_supp<0) ] = 0
				else:
					nh_supp[(self.ra==0) | (hours==0) | (nh_supp<0) ] = 0
			else:
				nh_supp = np.zeros(self.N) 
		else:
			nh_supp = np.zeros(self.N) #NH ends
			#dincome=boo_ra*(boo*dincome_nh+(1-boo)*dincome_eitc) + \
			#(1-boo_ra)*dincome_eitc 

		#The AFDC (1995-1996. TANF implemented 1997, t=2)
		afdc_benefit = np.zeros(self.N)
		if periodt<=1:
			afdc_takeup=self.prob_afdc() #generates random afdc take-up
			cutoff = np.zeros(self.N)
			benefit_std = np.zeros(self.N)
			for nf in range(1,13):
				if nf<12:
					boo_k=nfam == nf
				else:
					boo_k=nfam >= nf
				cutoff[boo_k] = afdc_param['cutoff'][nf-1]
				benefit_std[boo_k] = afdc_param['benefit_std'][nf-1]

			boo_eli=(pwage<=cutoff) & (afdc_takeup==1)
			boo_min=benefit_std<=benefit_std-(pwage - 30)*.67
			afdc_benefit[boo_eli]=(1-boo_min[boo_eli])*(benefit_std[boo_eli]-(pwage[boo_eli] - 30)*.67) + boo_min[boo_eli]*benefit_std[boo_eli]
			afdc_benefit[afdc_benefit<0]=0
			#boo_max=afdc_benefit>0
			#dincome[boo_max]=dincome[boo_max] + afdc_benefit[boo_max]
		
		#SNAP benefits: vary by period/family size.
		std_deduction=np.zeros(self.N)
		net_i_test=np.zeros(self.N)
		gross_i_test=np.zeros(self.N)
		max_b=np.zeros(self.N)
		snap_takeup = self.prob_snap()
		for nf in range(1,15):
			if nf<=4:
				std_deduction[nfam==nf]=snap_param['std_deduction'][nf-1,periodt]
			elif nf==5:
				std_deduction[nfam==nf]=snap_param['std_deduction'][2,periodt]
			elif nf>=6:
				std_deduction[nfam==nf]=snap_param['std_deduction'][3,periodt]
			
			if nf<=8:
				net_i_test[nfam==nf]=snap_param['net_income_test'][nf-1,periodt]
				gross_i_test[nfam==nf]=snap_param['gross_income_test'][nf-1,periodt]
				max_b[nfam==nf]=snap_param['max_benefit'][nf-1,periodt]


			else:
				net_i_test[nfam==nf] = snap_param['net_income_test'][7,periodt] + snap_param['net_income_test'][8,periodt]*nfam[nfam==nf]

				gross_i_test[nfam==nf] = snap_param['gross_income_test'][7,periodt] + snap_param['gross_income_test'][8,periodt]*nfam[nfam==nf]

				max_b[nfam==nf] = snap_param['max_benefit'][7,periodt] + snap_param['max_benefit'][8,periodt]*nfam[nfam==nf]
			
		net_inc = pwage + afdc_benefit + nh_supp - std_deduction
		boo_net_eli = net_inc <= net_i_test
		boo_gro_eli = pwage <= gross_i_test
		boo_unemp=hours==0
		snap = snap_takeup*((max_b - 0.3*net_inc)*boo_net_eli*boo_gro_eli*(1-boo_unemp) + boo_unemp*(max_b - 0.3*net_inc))*snap_takeup
		snap[snap<0]=0

		dincome = pwage + afdc_benefit + nh_supp + snap + eitc_fed + eitc_state

		#Back to real prices
		return {'income': dincome*(self.param.cpi[8]/self.param.cpi[periodt]),
		'NH': nh_supp, 'EITC_NH': nh_supp + eitc_fed + eitc_state}