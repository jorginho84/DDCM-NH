"""
This class modifies treatment group's budget set
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
		dic_eitc=self.param.eitc[periodt]

		#The AFDC parameters
		afdc_param=self.param.afdc[0]

		#The SNAP parameters
		snap_param=self.param.snap[0]

		#family size
		nfam = np.ones(self.N) + kid[:,0] + marr[:,0]

		#EITC parameters [[control],[treatment]]
		r1 = []
		r2 = []
		b1 = []
		b2 = []
		state_eitc = []
		

		#parameters of the EITC treatment
		for nn in range(1,4):
			r1.append(dic_eitc['r1_' + str(nn)])
			r2.append(dic_eitc['r2_'+ str(nn)])
			b1.append(dic_eitc['b1_'+ str(nn)])
			b2.append(dic_eitc['b2_'+ str(nn)])
			state_eitc.append(dic_eitc['state_eitc'+ str(nn)])
			

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

		
		
		
		##Obtaining NH income supplement: shut down#

		nh_supp = np.zeros(self.N) 

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
		'NH': nh_supp }

	def consumptiont(self,periodt,h,cc,dincome,marr,nkids,wage, free,price):
		"""
		Computes per-capita consumption:
		(income - cc_payment)/family size

		where cc_payment is determined using NH formula and price offer

		"""
		pwage=np.reshape(h,self.N)*np.reshape(wage,self.N)*52

		d_work=h>=self.hours_p
		agech=np.reshape(self.age_t0,(self.N)) + periodt
		young=agech<=5
		boo_nfree = free==0
		

		nkids=np.reshape(nkids,self.N)
		marr=np.reshape(marr,self.N)
		ones=np.ones(self.N)

		#Assuming Wisconsin shares = NH
		copayment=np.zeros(self.N)
		copayment[price[:,0]<400]=price[price[:,0]<400,0].copy()
		copayment[(price[:,0]>400) & (pwage<=8500) ] = 400
		copayment[(price[:,0]>400) & (pwage>8500)] = 315 + 0.01*pwage[(price[:,0]>400) & (pwage>8500)] 
		
		#For those who copayment would be bigger than price
		copayment[price[:,0]<copayment] = price[price[:,0]<copayment,0].copy()

		cc_cost = np.zeros(self.N)
		
		#Child care cost: cc subsidy extended for all periods
		cc_cost[young & boo_nfree] = price[young & boo_nfree,0].copy()
		if self.cs==1:
			cc_cost[d_work & boo_nfree & young] = copayment[d_work & boo_nfree & young].copy()
			
		
		incomepc=(dincome - cc*cc_cost)/(ones+nkids+marr)
		incomepc[incomepc<=0]=1
		

		#New hope cost is zero:
		nh_cost = np.zeros(self.N)
		return {'income_pc': incomepc, 'nh_cc_cost': nh_cost}

	def elec(self):
		"""
		This function recovers ec and el
		"""
		ec = np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/EITC/ec.npy')
		el = np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/EITC/el.npy')
		ecc = np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/EITC/ecc.npy')
		e_age = np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/EITC/e_age.npy')
		return [ec, el, ecc,e_age]

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

		#adjustment for E[theta = 0]: this is shut down
		if periodt<=7:
			alpha = - ecel[3][periodt]*ecel[2][periodt]*tfp - ecel[0][periodt]*gamma2 - ecel[1][periodt]*gamma3
		else:
			alpha = - ecel[3][7]*ecel[2][7]*tfp - ecel[0][7]*gamma2 - ecel[1][7]*gamma3

		return np.exp(theta1 + alpha)
	
	