"""
execfile('draft.py')

(1) Defines a set of parameters and X's
(2) Defines a grid of state variables
(3) Obtains a dictionary with the set of emax functions
(4) Given (3), simulates fake data

The emax functions are interpolating instances (see int_linear.py for 
	more information)

(1). The parameters and X's are related to the specificaciones of the regressions
on marriage, number of kids, and the wage process. Make sure to match those in
"marriage_process/marriage_process.do";"kids_process/kids_process.do"; and
"wage_process/wage.do".

(2) and (3). Uses gridemax.py to construct the grid. Use this file to modify 
the size of the grid. Importantly, the variables in the grid must coincide
to those in (1). Then, it uses emax.py and int_linear.py to compute emax functions
that depends on the grid values. It returns a dictionary of emax functions, which
are instances of the class defined in int_linear

(4) The emax dictionary is an input in the class found in simdata.py.

pip2.7 install --user line_profiler


"""

#########Simulating data###############
print ''
print ''
print 'Simulating fake data'
start_time = time.time()
print ''
print ''


sim_ins=simdata.SimData(N,param,emax_dic,x_w,x_m,x_k,x_wmk,passign,nkids0,married0,agech0,hours_p,hours_f,wr,cs,ws,model)
data_dic=sim_ins.fake_data(17)


time_sim=time.time() - start_time
print ''
print ''
print 'Done with procedure in:'
print("--- %s seconds ---" % (time_sim))
print ''
print ''

#warning: for individuals with children over 18 yo, the problem is not well defined.
#look only until t=8 years after RA
ct=data_dic['Consumption']
income=data_dic['Income']
nh_sup=data_dic['nh_matrix']
theta_t=data_dic['Theta']
cc_t=data_dic['Childcare']
hours_t=data_dic['Hours']
wage_t=data_dic['Wage']
ssrs_t2=data_dic['SSRS_t2']
ssrs_t5=data_dic['SSRS_t5']
kids=data_dic['Kids']
marr=data_dic['Marriage']

#log theta in SD units
ltheta=np.log(theta_t)
np.mean(ltheta,axis=0)
np.std(ltheta,axis=0)

#Impact of NH on logtheta (SD units) in time
ate_theta=np.mean(ltheta[passign[:,0]==1,:],axis=0) - np.mean(ltheta[passign[:,0]==0,:],axis=0)

#NH supplement
np.mean(nh_sup[passign[:,0]==1,:],axis=0)
np.mean(nh_sup[passign[:,0]==1,:],axis=0)

np.mean(nh_sup[(passign[:,0]==1) & (nh_sup[:,0]>0)  & (nkids0[:,0]==3),0])

#Impact on income
np.mean(income,axis=0)
ate_income=np.mean(income[passign[:,0]==1,:],axis=0) - np.mean(income[passign[:,0]==0,:],axis=0)
ate_ct=np.mean(ct[passign[:,0]==1,:],axis=0) - np.mean(ct[passign[:,0]==0,:],axis=0)

np.mean(np.mean(ct[passign[:,0]==0,:],axis=0))

#var of ssrs2
d_1 = ssrs_t2>=3
np.std(d_1)

#Children's ranking
ssrs_freq_t2=np.zeros((N,5))
ssrs_freq_t5=np.zeros((N,5))
for j in range(1,6):
	ssrs_freq_t5[:,j-1]=ssrs_t5==j
	ssrs_freq_t2[:,j-1]=ssrs_t2==j


np.mean(ssrs_freq_t5,axis=0)
np.mean(ssrs_freq_t2,axis=0)


#Child care (t=0, all young)
np.mean(cc_t[agech0[:,0]<=6,:],axis=0)
ate_cc=np.mean(cc_t[(passign[:,0]==1) & (agech0[:,0]<=5),:],axis=0) - np.mean(cc_t[(passign[:,0]==0) & (agech0[:,0]<=5),:],axis=0)

#Child care (t=0, all young, employed)
np.mean(cc_t[(agech0[:,0]<=6),0],axis=0)
np.mean(cc_t[(agech0[:,0]<=6) & (hours_t[:,0]==40),0],axis=0)
np.mean(cc_t[(agech0[:,0]<=6) & (hours_t[:,0]==15),0],axis=0)


#Labor supply
unemp_t=hours_t==0
part_t=hours_t==hours_p
full_t=hours_t==hours_f

np.mean(hours_t[passign[:,0]==0,:],axis=0)

np.mean(unemp_t[agech0[:,0]<=6,:],axis=0)

np.mean(unemp_t,axis=0)
np.mean(full_t,axis=0)
np.mean(part_t,axis=0)


np.mean(wage_t[unemp_t[:,0]==0,0])

gross = wage_t*hours_t*52
np.mean(gross[unemp_t[:,0]==0,0])
np.mean(wage_t[(part_t[:,0]==1) & (passign[:,0]==1),0],axis=0)
np.mean(gross[(part_t[:,0]==1) & (passign[:,0]==1),0],axis=0)
np.mean(income[(unemp_t[:,0]==1) & (passign[:,0]==1),0],axis=0)

ate_income_all=np.mean(income[passign[:,0]==1,0],axis=0) - np.mean(income[passign[:,0]==0,0],axis=0)
ate_income_ft=np.mean(income[(full_t[:,0]==1) & (passign[:,0]==1),0],axis=0) - np.mean(income[(full_t[:,0]==1) & (passign[:,0]==0),0],axis=0)
ate_income_pt=np.mean(income[(part_t[:,0]==1) & (passign[:,0]==1),0],axis=0) - np.mean(income[(part_t[:,0]==1) & (passign[:,0]==0),0],axis=0)
ate_income_un=np.mean(income[(unemp_t[:,0]==1) & (passign[:,0]==1),0],axis=0) - np.mean(income[(unemp_t[:,0]==1) & (passign[:,0]==0),0],axis=0)

#ATE on employment
ate_unem=np.mean(unemp_t[passign[:,0]==1,:],axis=0) - np.mean(unemp_t[passign[:,0]==0,:],axis=0)
ate_part=np.mean(part_t[passign[:,0]==1,:],axis=0) - np.mean(part_t[passign[:,0]==0,:],axis=0)
ate_full=np.mean(full_t[passign[:,0]==1,:],axis=0) - np.mean(full_t[passign[:,0]==0,:],axis=0)

#Child care cost
np.mean(ct[agech0[:,0]<=6,:],axis=0)
np.mean(ct[(cc_t[:,0]==1) & (agech0[:,0]<=6),:],axis=0)
np.mean(ct[(cc_t[:,0]==1) & (agech0[:,0]<=6) & (passign[:,0]==0) & (full_t[:,0]==1),:],axis=0)
np.mean(ct[(cc_t[:,0]==0) & (agech0[:,0]<=6) & (passign[:,0]==0) & (full_t[:,0]==1),:],axis=0)

