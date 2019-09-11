"""

exec(open("/home/jrodriguez/NH_HC/codes/model_v2/experiments/EITC/draft.py").read())


This file computes EITC experiments using the whole sample to build counterfactuals
"""
##Recovering choices
cc_sim_matrix = []
ct_sim_matrix = []
h_sim_matrix = []
part_sim_matrix = []
full_sim_matrix = []
emp_sim_matrix = []
theta_sim_matrix = []
wage_sim_matrix = []
income_sim_matrix = []
theta_sd = [np.zeros((N,nperiods,M)),np.zeros((N,nperiods,M)),
	np.zeros((N,nperiods,M)),np.zeros((N,nperiods,M))]

for j in range(len(experiments)): #the experiment loop
	cc_sim_matrix.append(choices[j]['childcare_matrix'])
	ct_sim_matrix.append(choices[j]['consumption_matrix'])
	income_sim_matrix.append(choices[j]['income_matrix'])
	h_sim_matrix.append(choices[j]['hours_matrix'])
	theta_sim_matrix.append(choices[j]['theta_matrix'])
	wage_sim_matrix.append(choices[j]['wage_matrix'])
	part_sim_matrix.append(choices[j]['hours_matrix'] == hours_p)
	full_sim_matrix.append(choices[j]['hours_matrix'] == hours_f)
	emp_sim_matrix.append(choices[j]['hours_matrix'] > 0)



######The Contribution to ATE theta#####

#the sample
boo_all = (age_ch[:,2]<=6)


#Impact on ln theta
ate_theta_sd = [np.zeros((nperiods,M)),np.zeros((nperiods,M)),np.zeros((nperiods,M)),np.zeros((nperiods,M))]
av_impact = []
sd_long = []
for k in range(len(experiments)):
	
	if k % 2 == 0:
		z = 0
	else:
		z = 1

	sd_long.append(np.concatenate((np.log(theta_sim_matrix[k]),np.log(theta_sim_matrix_baseline[z])),axis=0))

	for j in range(M):
		for t in range(nperiods):

			ate_theta_sd[k][t,j] = np.mean(np.log(theta_sim_matrix[k][boo_all==1,t,j]) - np.log(theta_sim_matrix_baseline[z][boo_all==1,t,j]))/np.std(sd_long[k][:,t,j],axis=0)

	av_impact.append(np.mean(ate_theta_sd[k],axis=1)) 

#Impact on consumption, child care, labor supply
ate_ct = [np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods))]
ate_cc = [np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods))]
ate_hours = [np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods))]
ate_income = [np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods))]
ate_part = [np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods))]
ate_full = [np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods))]
ate_emp = [np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods)),np.zeros((nperiods))]

for k in range(len(experiments)):

	if k % 2 == 0:
		z = 0
	else:
		z = 1

	ate_ct[k] = np.mean(np.mean(ct_sim_matrix[k][boo_all==1,:,:] - ct_sim_matrix_baseline[z][boo_all==1,:,:],axis=0),axis=1)*12/100
	ate_cc[k] = np.mean(np.mean(cc_sim_matrix[k][boo_all==1,:,:] - cc_sim_matrix_baseline[z][boo_all==1,:,:],axis=0),axis=1)
	ate_hours[k] = np.mean(np.mean(h_sim_matrix[k][boo_all==1,:,:] - h_sim_matrix_baseline[z][boo_all==1,:,:],axis=0),axis=1)
	ate_part[k] = np.mean(np.mean(part_sim_matrix[k][boo_all==1,:,:],axis=0) - np.mean(part_sim_matrix_baseline[z][boo_all==1,:,:],axis=0),axis=1)
	ate_full[k] = np.mean(np.mean(full_sim_matrix[k][boo_all==1,:,:],axis=0) - np.mean(full_sim_matrix_baseline[z][boo_all==1,:,:],axis=0),axis=1)
	ate_emp[k] = np.mean(np.mean(emp_sim_matrix[k][boo_all==1,:,:],axis=0) - np.mean(emp_sim_matrix_baseline[z][boo_all==1,:,:],axis=0),axis=1)
	ate_income[k] = np.mean(np.mean(income_sim_matrix[k][boo_all==1,:,:] - income_sim_matrix_baseline[z][boo_all==1,:,:],axis=0),axis=1)



#For 4 counterfactuals
ate_cont_theta  = [np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M))]
ate_cont_lt  = [np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M))]
ate_cont_cc  = [np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M))]
ate_cont_ct  = [np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M)),np.zeros((nperiods - 1,M))]


for t in range(nperiods - 1):
	for j in range(M):


		for k in range(len(experiments)): #the counterfactual loop

			if k % 2 == 0:
				z = 0
			else:
				z = 1

			#the theta contribution
			ltheta_th1 = models[k].thetat(t,theta_sim_matrix[k][:,t,j],
				h_sim_matrix_baseline[z][:,t,j],cc_sim_matrix_baseline[z][:,t,j],
				ct_sim_matrix_baseline[z][:,t,j])
			ltheta_th0 = models[k].thetat(t,theta_sim_matrix_baseline[z][:,t,j],
				h_sim_matrix_baseline[z][:,t,j],cc_sim_matrix_baseline[z][:,t,j],
				ct_sim_matrix_baseline[z][:,t,j])
		
			ate_cont_theta[k][t,j] = np.mean(np.log(ltheta_th1[boo_all]) - np.log(ltheta_th0[boo_all]))/np.std(sd_long[k][:,t,j],axis=0)
		
			#The leisure contribution
			ltheta_th1 = models[k].thetat(t,theta_sim_matrix[k][:,t,j],
				h_sim_matrix[k][:,t,j],cc_sim_matrix_baseline[z][:,t,j],
				ct_sim_matrix_baseline[z][:,t,j])
			ltheta_th0 = models[k].thetat(t,theta_sim_matrix[k][:,t,j],
			h_sim_matrix_baseline[z][:,t,j],cc_sim_matrix_baseline[z][:,t,j],
			ct_sim_matrix_baseline[z][:,t,j])
			
			ate_cont_lt[k][t,j] = np.mean(np.log(ltheta_th1[boo_all]) - np.log(ltheta_th0[boo_all]))/np.std(sd_long[k][:,t,j],axis=0)

			#The CC contribution
			ltheta_th1 = models[k].thetat(t,theta_sim_matrix[k][:,t,j],
				h_sim_matrix[k][:,t,j],cc_sim_matrix[k][:,t,j],
				ct_sim_matrix_baseline[z][:,t,j])
			ltheta_th0 = models[k].thetat(t,theta_sim_matrix[k][:,t,j],
				h_sim_matrix[k][:,t,j],cc_sim_matrix_baseline[z][:,t,j],
				ct_sim_matrix_baseline[z][:,t,j])
			ate_cont_cc[k][t,j] = np.mean(np.log(ltheta_th1[boo_all]) - np.log(ltheta_th0[boo_all]))/np.std(sd_long[k][:,t,j],axis=0)

			#The consumption contribution
			ltheta_th1 = models[k].thetat(t,theta_sim_matrix[k][:,t,j],
				h_sim_matrix[k][:,t,j],cc_sim_matrix[k][:,t,j],
				ct_sim_matrix[k][:,t,j])
			ltheta_th0 = models[k].thetat(t,theta_sim_matrix[k][:,t,j],
				h_sim_matrix[k][:,t,j],cc_sim_matrix[k][:,t,j],
				ct_sim_matrix_baseline[z][:,t,j])
			ate_cont_ct[k][t,j] = np.mean(np.log(ltheta_th1[boo_all]) - np.log(ltheta_th0[boo_all]))/np.std(sd_long[k][:,t,j],axis=0)


###The graphs##


#Table: average effects
outcome_list = [r'Money (US\$ 100)', 'Weekly hours worked', 'Child care (percentage points)']

output_list =  [ate_ct,ate_hours,ate_cc]

for j in range(len(experiments)):
	ate_cc[j] = ate_cc[j]*100

#number of periods to consider averaging
periods = [3,3,3]

with open('/home/jrodriguez/NH_HC/results/model_v2/experiments/EITC/table_eitc_mech.tex','w') as f:
	f.write(r'\begin{tabular}{llccccccc}'+'\n')	
	f.write(r'\hline'+'\n')
	f.write(r'Variable &       & (1)   &       & (2)   &       & (3)   &       & (4) \bigstrut\\'+'\n')
	f.write(r'\hline'+'\n')
	for j in range(len(output_list)):
		f.write(
			outcome_list[j]+ '&&'+ '{:3.2f}'.format(np.mean(output_list[j][0][0:periods[j]]))  
			+'&& '+ '{:3.2f}'.format(np.mean(output_list[j][1][0:periods[j]])) 
			+'&& '+ '{:3.2f}'.format(np.mean(output_list[j][2][0:periods[j]]))
			+'&& '+ '{:3.2f}'.format(np.mean(output_list[j][3][0:periods[j]]))
			)

		f.write(r' \bigstrut[t]\\'+'\n')

		
	f.write(r'\hline'+'\n')
	f.write(r'EITC (1995-2003) &       & Yes   &       & Yes   &       & No    &       & No \bigstrut[t]\\'+'\n')
	f.write(r'Unconditional transfer &       & No    &       & No    &       & Yes   &       & Yes \\'+'\n')
	f.write(r'Child care subsidy &       & No    &       & Yes   &       & No    &       & Yes \bigstrut[b]\\'+'\n')
	f.write(r'\hline'+'\n')
	f.write(r'\end{tabular}%'+'\n')



#Effects on ln theta
names_list_v2 = [r'EITC $\checkmark$ - CC subsidy $\times$ ',
r'EITC $\checkmark$ - CC subsidy $\checkmark$',
r'Unconditional $\checkmark$ - CC subsidy $\times$',
r'Unconditional $\checkmark$ - CC subsidy $\checkmark$']


markers_list = ['k-','k--','k-o','k-.']
facecolor_list = ['k','k','k','k']

nper = av_impact[0].shape[0]
fig, ax=plt.subplots()
x = np.array(range(0,nper))
for k in range(len(experiments)):
	ax.plot(x,av_impact[k],markers_list[k],markerfacecolor= facecolor_list[k],
		markeredgewidth=1.0,label=names_list_v2[k],linewidth=3,markersize=11,alpha=0.9)
ax.set_ylabel(r'Effect on child human capital ($\sigma$s)', fontsize=15)
ax.set_xlabel(r'Years after random assignment ($t$)', fontsize=15)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
ax.legend(loc=0)
plt.yticks(fontsize=15)
plt.xticks(fontsize=15)
#ax.set_ylim(-0.01,.50)
plt.show()
fig.savefig('/home/jrodriguez/NH_HC/results/model_v2/experiments/EITC/ate_theta_eitc.pdf', format='pdf')
plt.close()


#Mechanisms Figures
phi_money = np.zeros((nperiods-1,len(experiments)))
phi_cc = np.zeros((nperiods-1,len(experiments)))
phi_time = np.zeros((nperiods-1,len(experiments)))

for k in range(len(experiments)):
	c_money = np.mean(ate_cont_ct[k],axis=1)
	c_cc = np.mean(ate_cont_cc[k],axis=1)
	c_time = np.mean(ate_cont_lt[k],axis=1)

	phi_money[0,k] = c_money[0]
	phi_cc[0,k] = c_cc[0]
	phi_time[0,k] = c_time[0]
	for t in range(c_money.shape[0]-1):
		phi_money[t+1,k] = c_money[t+1] + gamma1*phi_money[t,k]
		phi_cc[t+1,k] = c_cc[t+1] + gamma1*phi_cc[t,k]
		phi_time[t+1,k] = c_time[t+1] + gamma1*phi_time[t,k]

#Plot accumulated contributions up to period nt
nt = 2

x = np.array(len(experiments))
total = phi_time[nt,:] + phi_cc[nt,:] + phi_money[nt,:]
bar1 =  phi_time[nt,:]/total #Time
bar2 = phi_money[nt,:]/total # Income
bar3 = phi_cc[nt,:]/total # CC
y = np.arange(len(experiments))

y_labels = [r'EITC, CS $\times$', r'EITC, CS $\checkmark$', 
r'Uncond, CS $\times$', r'Uncond, CS $\checkmark$']

fig, ax=plt.subplots()
ax.barh(y,bar1.tolist(),height=0.5,color='gray',edgecolor='black',label='Time')
ax.barh(y,bar2.tolist(),height=0.5,left=bar1,color='blue',alpha=0.7,edgecolor='black',label='Money')
ax.barh(y,bar3.tolist(),height=0.5,left=list(map(lambda g,y:g+y,bar1.tolist(),bar2.tolist())),color='green',alpha=0.7,edgecolor='black',hatch='//',label='Child care')
#ax.set_xlabel(r'Share explained by input', fontsize=14)
ax.legend(loc='upper center',bbox_to_anchor=(0.5, -0.05),fontsize=12,ncol=3)
plt.yticks(y,y_labels,fontsize=11)
plt.show()
fig.savefig('/home/jrodriguez/NH_HC/results/model_v2/experiments/EITC/mech_share_income.pdf', format='pdf')
plt.close()


