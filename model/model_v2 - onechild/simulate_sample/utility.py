"""
Defines two classes: Parameters and Utility

-Parameters: defines a set of parameters

-Utility class: takes parameters, X's, and given choices and 
computes utility at a given point in time
It also computes next-period states: married, nkids, theta

pip2.7 install --user --upgrade panda

os.chdir("/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model")


"""
#from __future__ import division #omit for python 3.x
import numpy as np
import pandas as pd
import sys, os
from scipy import stats

class Parameters:

	"""

	List of structural parameters and prices

	"""
	def __init__(self,alphap,alphaf,mu_c,
		eta,gamma1,gamma2,gamma3,
		tfp,sigma2theta,rho_theta_epsilon,betaw,
		beta_spouse,c_emp_spouse,
		betam,betak,eitc,afdc,snap,cpi,fpl_list,
		lambdas,kappas,pafdc,psnap,mup,sigma_z):

		self.alphap,self.alphaf,self.eta,self.mu_c=alphap,alphaf,eta,mu_c
		self.gamma1,self.gamma2,self.gamma3=gamma1,gamma2,gamma3
		self.tfp=tfp
		self.rho_theta_epsilon=rho_theta_epsilon
		self.sigma2theta=sigma2theta
		self.betaw,self.betam,self.betak=betaw,betam,betak
		self.beta_spouse,self.c_emp_spouse=beta_spouse,c_emp_spouse
		self.eitc,self.afdc,self.snap,self.cpi,self.fpl_list=eitc,afdc,snap,cpi,fpl_list
		self.lambdas,self.kappas=lambdas,kappas
		self.pafdc,self.psnap=pafdc,psnap
		self.mup = mup
		self.sigma_z = sigma_z


class Utility(object):
	""" 
	
	This class defines the economic environment of the agent

	"""
	def __init__(self,param,N,xwage,xmarr,xkid,ra,
		nkids0,married0,hours,cc,age_t0,hours_p,hours_f,wr,cs,ws):
		"""
		Set up model's data and paramaters

		theta0, nkids0, married0: ability, number of kids, and marital status
		at period t-1 (periodt-1). "periodt" represents choice at 
		periodt-1. 

	
		"""
		
		self.param=param
		self.N,self.xwage,self.xmarr=N,xwage,xmarr
		self.xkid,self.ra=xkid,np.reshape(ra,self.N)
		self.nkids0,self.married0= nkids0,married0
		self.hours,self.cc,self.age_t0=hours,cc,age_t0
		self.hours_p,self.hours_f=hours_p,hours_f
		self.wr,self.cs,self.ws=wr,cs,ws

	def shocks_init(self):
		"""
		Initial shocks to human capital and individual productivity
		
		"""

		var =  np.random.multivariate_normal(np.zeros(2),
			np.array([[self.param.sigma2theta**2,
			self.param.rho_theta_epsilon*self.param.sigma2theta*
			np.sqrt(self.param.betaw[-2,0])],
			[self.param.rho_theta_epsilon*self.param.sigma2theta*
			np.sqrt(self.param.betaw[-2,0]),self.param.betaw[-2,0]]]),self.N)

		return {'epsilon_theta0': var[:,0], 'epsilon0': var[:,1]}

	def wage_init(self,epsilon_t):
		"""
		Initial shock to wages
		"""
		
		periodt = 0
		lt = np.zeros((self.N,1)) + periodt 

		xw=np.concatenate((np.reshape(self.xwage[:,0],(self.N,1)), #higrade
					lt,
					np.reshape(self.xwage[:,1],(self.N,1)),),axis=1) #constant

		betas=self.param.betaw[0:-2,0] #everything but rho and variance
		return {'wage':np.exp( np.dot(xw,betas)+ epsilon_t )}


	def theta_init(self,epsilon_theta0):
		"""
		The initial value of child human capital: [child A, child B]
		"""
		
		return np.exp( epsilon_theta0)

		
	def epsilon(self,epsilon_1):
		"""
		the law of motion of wage shock
		"""
		rho_eps = self.param.betaw[-1,0]*np.reshape(epsilon_1,self.N)
		nu = np.sqrt(self.param.betaw[-2,0])*np.random.randn(self.N)
		return rho_eps + nu 

	


	def waget(self,periodt,epsilon):
		"""
		Computes w (hourly wage) for periodt

		
		This method returns t=0,1...,8 
		(at t=0 we don't observe wages for those who do not work)
		(that's why I need to simulate w0 instead of just using observed one)

		lnw =beta1*age + beta1*age2 + beta3d_HS + beta4*log(periodt)
		 beta5 +  e

		 where e = rho*e(-1) + nu

		 nu iid normal

		"""



		lt =  np.zeros((self.N,1)) + periodt

		xw=np.concatenate((np.reshape(self.xwage[:,0],(self.N,1)), #HS
					lt,
					np.reshape(self.xwage[:,1],(self.N,1)),),axis=1) #constant

		betas=self.param.betaw[0:-2,0] #everything but rho and variance


		return np.exp( np.dot(xw,betas)+ epsilon)

	def employment_spouse(self):
		"""
		Computes income process for males

		"""
	
		return np.random.randn(self.N) > self.param.c_emp_spouse


	def income_spouse(self):
		"""
		Computes income process for males

		"""
		xw=np.concatenate((np.reshape(self.xwage[:,0],(self.N,1)), #HS
						np.reshape(self.xwage[:,1],(self.N,1)),),axis=1) #constant

		betas=self.param.beta_spouse[0:-1,0] #everything but variance

		epsilon = np.sqrt(self.param.beta_spouse[-1,0])*np.random.randn(self.N)

		#spouse income (for everyone)
		income_spouse = np.dot(xw,betas)+ epsilon 
		
		return np.exp(income_spouse)

	def q_prob(self):
		"""
		Draws a free child care slot from a binomial distribution
		#THIS IS SHUT DOWN
		"""
		return np.random.binomial(1,0.57,self.N)
		#return np.zeros(self.N)

	def price_cc(self):
		"""
		Draws a price offer for a child care slot
		"""
		return self.param.mup*12*np.ones((self.N,1))

	def prob_afdc(self):
		"""
		Draws a vector of participation shocks of AFDC
		"""
		#return np.random.binomial(1,self.param.pafdc,self.N)
		return np.ones(self.N)

	def prob_snap(self):
		"""
		Draws a vector of participation shocks of SNAP
		"""
		#return np.random.binomial(1,self.param.psnap,self.N)
		return np.ones(self.N)



	def marriaget(self,periodt,marriedt_1):
		"""
		Computes probability of marriage at periodt (t) conditional on marital status
		at t-1

		marriage0 is given, so this method returns t=1,2,3...
		

		pr(married)=F(beta1*age + beta7*married_t-1 + beta_constant )

		
		"""

		age_ra=self.xmarr[:,0].copy()
		age=age_ra+(periodt-1) #age at t-1
		betas=self.param.betam[0:-1,0]
		epsilon=self.param.betam[-1,0]*np.random.randn(self.N)
		x_marr2=np.concatenate( (np.reshape(age,(self.N,1)),
			np.reshape(marriedt_1,(self.N,1)),
			np.ones((self.N,1))),axis=1 )
		
		phat=np.dot(x_marr2,betas) + epsilon
		phat[phat<0]=0
		phat[phat>1]=1

		return np.random.binomial(1,phat) #1 if stayed married at t+1

	def kidst(self,periodt,nkids,marriage):
		"""
		Computes whether the individual has a kid in periodt (t).
		For a given array of marriage (1,0) and number of kids

		kids0 is given, so this method returns t=1,2,3...

		age and age2 are taking from baseline

		marriage and nkids are vectors or shape N,1

		The equation:
		pr(having kid t)=F(beta1*age + beta2*age2 + beta3*nkids + beta4*marriage 
			 + beta_constant)

		"""
		age_ra=self.xkid[:,0].copy()
		age=age_ra+(periodt-1) #age at period t-1
		age2=age**2
		betas=self.param.betak[0:-1,0]
		epsilon=self.param.betak[-1,0]*np.random.randn(self.N)
		xkids2=np.concatenate((np.reshape(age,(self.N,1)),np.reshape(age2,(self.N,1)),
					nkids,marriage,np.ones((self.N,1))),axis=1)

		phat=np.dot(xkids2,betas) + epsilon
		phat[phat<0]=0
		phat[phat>1]=1
		dummy=np.random.binomial(1,phat)

		return  np.reshape(dummy,(self.N,1)) #1 if have a kid a t+1


	def dincomet(self, periodt,hours,wage,marr,kid,income_spouse,employment_spouse):
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
		pwage = np.reshape(hours,self.N)*np.reshape(wage,self.N)*52

		#To nominal prices (2003 prices)
		pwage = pwage/(self.param.cpi[8]/self.param.cpi[periodt])

		#family earnings: used for eligibility
		pwage_family = pwage + income_spouse*employment_spouse*marr[:,0]

		#the EITC parameters
		dic_eitc=self.param.eitc[periodt]

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

		pwages = [pwage,pwage_family]

		for nn in range(1,4):
			#1 children
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
			
			for k in range(0,1): #spouse employment

				if k == 0:
					boo_spouse = marr[:,0] == 0 | ((marr[:,0] == 1) & (employment_spouse == 0))
				else:
					boo_spouse = (marr[:,0] == 1) & (employment_spouse == 1)
				
				eitc_fed[(pwages[k]<b1[nn]) & (kid_boo) & (boo_spouse) ]=r1[nn]*pwages[k][(pwages[k]<b1[nn]) & (kid_boo) & (boo_spouse)]
				eitc_fed[(pwages[k]>=b1[nn]) & (pwages[k]<b2[nn][k] & (boo_spouse)) & (kid_boo)]=r1[nn]*b1[nn]
				eitc_fed[(pwages[k]>=b2[nn][k]) & (kid_boo) & (boo_spouse)]=np.maximum(r1[nn]*b1[nn]-r2[nn]*(pwages[k][(pwages[k]>=b2[nn][k]) & (kid_boo) & (boo_spouse)]-b2[nn][k]),np.zeros(pwages[k][(pwages[k]>=b2[nn][k]) & (kid_boo) & (boo_spouse)].shape[0]))
				eitc_state[kid_boo]=state_eitc[nn]*eitc_fed[kid_boo]

		dincome_eitc=pwage+eitc_fed+eitc_state

		##Obtaining NH income supplement#

		if periodt<=2:

			#the wage subsidy: individual (not family) earnings
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

			#per-child allowance: includes spouse income
			childa=np.zeros(self.N)
			childa[pwage_family<=8500]=xstar[pwage_family<=8500].copy()
			childa[pwage_family>8500]=xstar[pwage_family>8500] - beta_aux[pwage_family>8500]*(pwage_family[pwage_family>8500] - 8500)
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

			boo_eli=(pwage_family<=cutoff) & (afdc_takeup==1)
			boo_min=benefit_std<=benefit_std-(pwage - 30*12)*.67
			afdc_benefit[boo_eli]=(1-boo_min[boo_eli])*(benefit_std[boo_eli]-(pwage_family[boo_eli] - 30*12)*.67) + boo_min[boo_eli]*benefit_std[boo_eli]
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
			
		net_inc = pwage_family + afdc_benefit + nh_supp - std_deduction
		boo_net_eli = net_inc <= net_i_test
		boo_gro_eli = pwage_family <= gross_i_test
		boo_unemp=hours==0
		snap = snap_takeup*((max_b - 0.3*net_inc)*boo_net_eli*boo_gro_eli*(1-boo_unemp) + boo_unemp*(max_b - 0.3*net_inc))
		snap[snap<0]=0

		#income of household less spouse's earnings
		dincome = pwage*(self.param.cpi[8]/self.param.cpi[periodt]) + afdc_benefit + nh_supp + snap + eitc_fed + eitc_state

		#Back to real prices, on monthly basis
		return {'income': dincome, 'NH': nh_supp, 'EITC_NH': nh_supp + eitc_fed + eitc_state}

	def consumptiont(self,periodt,h,cc,dincome,income_spouse,employment_spouse,
		marr,nkids,wage, free,price):
		"""
		Computes per-capita consumption:
		(income - cc_payment)/family size

		where cc_payment is determined using NH formula and price offer

		It also returns what New Hope pays (nh_cost) for cost/benefit calculations

		"""

		nkids=np.reshape(nkids,self.N)
		marr=np.reshape(marr,self.N)
			
		pwage=np.reshape(h,self.N)*np.reshape(wage,self.N)*52

		pwage_family = pwage + income_spouse*employment_spouse*marr

		d_full=h>=self.hours_f
		agech=np.reshape(self.age_t0,(self.N)) + periodt
		young=agech<=5
		boo_ra = self.ra==1

		#relevant threshold for Head Start
		nfam = nkids + marr
		line = self.param.fpl_list[periodt]['fpl'] + self.param.fpl_list[periodt]['multip']*(nfam)
		boo_nfree = (free==0) | ((free==1) & (pwage_family > line))

		#NH copayment
		copayment=np.zeros(self.N)
		copayment[price[:,0]<400]=price[price[:,0]<400,0].copy()
		copayment[(price[:,0]>400) & (pwage_family<=8500) ] = 400
		copayment[(price[:,0]>400) & (pwage_family>8500)] = 315 + 0.01*pwage_family[(price[:,0]>400) & (pwage_family>8500)]

		#For those who copayment would be bigger than price
		copayment[price[:,0]<copayment] = price[price[:,0]<copayment,0].copy()

		#if married, spouse must work
		copayment[(marr==1) & (employment_spouse==0) ] == price[(marr==1) & (employment_spouse==0),0].copy()

		
		#child care cost
		cc_cost = np.zeros(self.N)

		cc_cost[boo_nfree] = price[boo_nfree,0].copy()
		if periodt<=2:
			
			if self.cs==1:
				if self.wr==1:
					cc_cost[boo_ra & d_full & boo_nfree] = copayment[boo_ra & d_full & boo_nfree].copy()
					
				else:
					cc_cost[boo_ra &  boo_nfree] = copayment[boo_ra &  boo_nfree].copy()
					

				nh_cost = (cc*young)*(price[:,0] - cc_cost)
			else:
				nh_cost = np.zeros(self.N)



		else:
			if self.cs==1:
				cc_cost[boo_nfree] = copayment[boo_nfree].copy()

			nh_cost = np.zeros(self.N)

		
		incomepc=(dincome + income_spouse*employment_spouse*marr - cc*young*cc_cost)/(np.ones(self.N)+nkids+marr)
		incomepc[incomepc <= 0] = 1


		#in monthly figures
		return {'income_pc': incomepc/12, 'nh_cc_cost': nh_cost}



	def thetat(self,periodt,theta0,h,cc,ct):
		"""
		Computes theta at period (t+1) (next period)
		t+1 goes from 1-8
		
		Inputs must come from period t

		"""
		#age of child
		agech=np.reshape(self.age_t0,(self.N)) + periodt

		#log time w child (T=168 hours a week, -35 for older kids)
		tch = np.zeros(self.N)
		boo_p = h == self.hours_p
		boo_f = h == self.hours_f
		boo_u = h == 0

		tch[agech<=5] = cc[agech<=5]*(168 - self.hours_f) + (1-cc[agech<=5])*(168 - h[agech<=5] ) 
		tch[agech>5] = 133 - h[agech>5] 
			
				
		#The production of HC: (young, cc=0), (young,cc1), (old)
		boo_age = agech <= 5
		theta1 = np.exp(self.param.tfp*cc*boo_age)*(theta0**self.param.gamma1)*(ct**self.param.gamma2)*(tch**self.param.gamma3)

		#normalizing E(ln theta)=0 forall t
		cte = np.mean(np.log(theta1))

		return theta1*np.exp(-cte)


	def Ut(self,periodt,dincome,income_spouse,employment_spouse,marr,cc,nkids,ht,thetat,
		wage,free,price):
		"""
		Computes current-period utility

		"""

		#Work dummies
		d_workf = ht == self.hours_f
		d_workp = ht == self.hours_p
		d_unemp = ht == 0

		#Consumption: depends on ra, cc, and period
		ct = self.consumptiont(periodt,ht,cc,dincome,income_spouse,employment_spouse,
			marr,nkids,wage,free,price)['income_pc']
		
		#Current-period utility
		ut_h = d_workp*self.param.alphap + d_workf*self.param.alphaf
		ut = ((ct*np.exp(ut_h))**self.param.mu_c)/(self.param.mu_c) + self.param.eta*((thetat**(0.5))/0.5)
		#ut = ((ct**self.param.mu_c)/self.param.mu_c)*np.exp(ut_h)*(thetat**self.param.eta)
		#ut = np.log(ct) + ut_h + self.param.eta*ltheta

		if (np.any(np.isnan(ct))==True) | (np.any(np.isinf(ct))==True) :
			raise ValueError('Consumption is not a real number')

		if (np.any(np.isnan(ht))==True) | (np.any(np.isinf(ht))==True) :
			raise ValueError('Hours is not a real number')

		if (np.any(np.isnan(ut_h))==True) | (np.any(np.isinf(ut_h))==True) :
			raise ValueError('Hours contribution to utility is not a real number')

		if (np.any(np.isnan(thetat))==True) | (np.any(np.isinf(thetat))==True) :
			raise ValueError('Theta is not a real number')

		if (np.any(np.isnan(np.log(thetat)))==True) | (np.any(np.isinf(np.log(thetat)))==True) :
			raise ValueError('Log of Theta is not a real number')

		if (np.any(np.isnan(ut))==True) | (np.any(np.isinf(ut))==True) :
			raise ValueError('Utility is not a real number')

	
		return ut

	def measures(self,periodt,thetat):
		"""
		For a given periodt and measure, computes the SSRS, given a value for theta.
		There is only one measure for period
		"""
		if periodt == 2:
			loc=0
		elif periodt == 5:
			loc=1

		lambdam = self.param.lambdas[loc]
		mu = self.param.kappas[loc]
		sigma =self.param.sigma_z[loc]

		pi = np.exp(thetat + sigma*np.random.randn(self.N))/(1+np.exp(thetat + sigma*np.random.randn(self.N)))

		return 5*pi
	
	
	def simulate(self,periodt,wage0,free,price,theta0,income_spouse,employment_spouse):
		"""
		Takes states (theta0, nkids0, married0, wage0) and given choices
		(self: hours and childcare) to compute current-period utility value.

		"""

		income=self.dincomet(periodt, self.hours,wage0,self.married0,self.nkids0,income_spouse,employment_spouse)['income']
		#theta=self.thetat(periodt,self.theta0,self.hours,self.childcare,income,self.married0,self.nkids0)
		

		return self.Ut(periodt,income,income_spouse,employment_spouse,
			self.married0,self.cc,self.nkids0,self.hours,theta0,wage0,free,price)

	
			





