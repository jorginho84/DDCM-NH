#Graph parameters
alpha_plot1 = 0.8
alpha_plot2 = 0.4
loc_legen = 4
fontsize_axis = 24
bar_width=0.4

#Opening workbook
wb=openpyxl.load_workbook('/home/jrodriguez/NH_HC/results/model_v2/fit/fit.xlsx')
ws = wb["new_moments_data"]

#A. Labor supply and child care decisions
list_aux = [beta_childcare,beta_hours1,beta_hours2]
list_obs = [moments_vector[0,0],moments_vector[1,0],moments_vector[2,0]]
list_sig = [se_vector[0],se_vector[1],se_vector[2]]
for c in range(3):
	ws['B' + str(c + 2)] = np.float(list_aux[c])
	ws['D' + str(c + 2)] = np.float(list_obs[c])
	ws['F' + str(c + 2)] = np.float(list_sig[c])
	

#the graph
fig, ax=plt.subplots()
x = np.array(range(0,len(list_aux)))
plot1=ax.bar(x,list_aux,bar_width,label='Simulated',color='k',alpha=alpha_plot1)
plot2=ax.bar(x + bar_width,list_obs,bar_width,yerr=list_sig,label='Data',edgecolor='k',
	color='k',alpha=alpha_plot2)
ax.legend(loc=loc_legen,fontsize=fontsize_axis)
ax.set_ylabel(r'$Pr(choice)$', fontsize=fontsize_axis)
ax.set_xlabel(r'Moments', fontsize=fontsize_axis)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
ax.set_xticklabels([])
ax.set_xticks(x + bar_width)
plt.show()
fig.savefig('/home/jrodriguez/NH_HC/results/model_v2/fit/fit_utility.pdf', format='pdf')
plt.close()


#B. Log wage equation
ind = 3
pos = 5
list_aux = []
list_obs = []
list_sig = []
for c in range(5):
	ws['B' + str(c + pos)] = np.float(beta_wagep[c])
	ws['D' + str(c + pos)] = np.float(moments_vector[ind+c,0])
	ws['F' + str(c + pos)] = np.float(se_vector[ind+c])
	
	list_aux.append(np.float(beta_wagep[c]))
	list_obs.append(moments_vector[ind+c,0])
	list_sig.append(se_vector[ind+c])

#the graph
fig, ax=plt.subplots()
x = np.array(range(0,len(list_aux)))
plot1=ax.bar(x,list_aux,bar_width,label='Simulated',color='k',alpha=alpha_plot1)
plot2=ax.bar(x + bar_width,list_obs,bar_width,yerr=list_sig,label='Data',edgecolor='k',
	color='k',alpha=alpha_plot2)
ax.legend(loc=loc_legen,fontsize=fontsize_axis)
ax.set_ylabel(r'$\widehat{\beta}$ of log wage OLS regression', fontsize=fontsize_axis)
ax.set_xlabel(r'Moments', fontsize=fontsize_axis)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
ax.set_xticklabels([])
ax.set_xticks([])
plt.show()
fig.savefig('/home/jrodriguez/NH_HC/results/model_v2/fit/fit_wage.pdf', format='pdf')
plt.close()

#B. Spouse's log wage equation
ind = ind + 5
pos = 10
list_aux = []
list_obs = []
list_sig = []
for c in range(3):
	ws['B' + str(c + pos)] = np.float(beta_wage_spouse[c])
	ws['D' + str(c + pos)] = np.float(moments_vector[ind+c,0])
	ws['F' + str(c + pos)] = np.float(se_vector[ind+c])
	
	list_aux.append(np.float(beta_wage_spouse[c]))
	list_obs.append(moments_vector[ind+c,0])
	list_sig.append(se_vector[ind+c])

#Spouse's employment
ind = ind + 3
pos = 13

ws['B' + str(pos)] = np.float(beta_emp_spouse)
ws['D' + str(pos)] = np.float(moments_vector[ind,0])
ws['F' + str(pos)] = np.float(se_vector[ind])

#C. Measures of academic achievement and family choices
ind = ind + 1
pos = 14
list_aux = []
list_obs = []
list_sig = []
#C. prod fn
list_aux = [beta_inputs]
list_obs = [moments_vector[ind:ind + 4 ,0]]
list_sig = [se_vector[ind:ind + 4]]

for c in range(4):
	ws['B' + str(c + pos)] = np.float(list_aux[0][c])
	ws['D' + str(c + pos)] = np.float(list_obs[0][c])
	ws['F' + str(c + pos)] = np.float(list_sig[0][c])


		
#the graph
fig, ax=plt.subplots()
x = np.array(range(0,list_aux[0].shape[0]))
plot1=ax.bar(x,list_aux[0],bar_width,label='Simulated',color='k',alpha=alpha_plot1)
plot2=ax.bar(x + bar_width,list_obs[0],bar_width,yerr=list_sig[0],label='Data',edgecolor='k',
	color='k',alpha=alpha_plot2)
ax.legend(loc=9,fontsize=fontsize_axis)
ax.set_ylabel(r'Corr(SSRS,input)', fontsize=fontsize_axis)
ax.set_xlabel(r'Moments', fontsize=fontsize_axis)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
ax.set_xticklabels([])
ax.set_xticks([])
plt.show()
fig.savefig('/home/jrodriguez/NH_HC/results/model_v2/fit/fit_ssrs.pdf', format='pdf')
plt.close()



#A. t=2, kappas
ind = ind + 4
pos = 18
list_aux = []
list_obs = []
list_sig = []
for c in range(1):
	ws['B' + str(c + pos)] = np.float(beta_kappas_t2[c])
	ws['D' + str(c + pos)] = np.float(moments_vector[ind + c,0])
	ws['F' + str(c + pos)] = np.float(se_vector[ind + c])
	
	list_aux.append(np.float(beta_kappas_t2[c]))
	list_obs.append(moments_vector[ind + c,0])
	list_sig.append(se_vector[ind + c])


ind = ind + 1
pos = 19

#B. t=5, kappas
for c in range(1):
	ws['B' + str(c + pos)] = np.float(beta_kappas_t5[c])
	ws['D' + str(c + pos)] = np.float(moments_vector[ind + c,0])
	ws['F' + str(c + pos)] = np.float(se_vector[ind + c])


	list_aux.append(np.float(beta_kappas_t5[c]))
	list_obs.append(moments_vector[ind + c,0])
	list_sig.append(se_vector[ind + c])



#the graph
fig, ax=plt.subplots()
x = np.array(range(0,len(list_aux)))
plot1=ax.bar(x,list_aux,bar_width,label='Simulated',color='k',alpha=alpha_plot1)
plot2=ax.bar(x + bar_width,list_obs,bar_width,yerr=list_sig,label='Data',edgecolor='k',
	color='k',alpha=alpha_plot2)
ax.legend(loc=loc_legen,fontsize=fontsize_axis)
ax.set_ylabel(r'$Pr(SSRS = \kappa)$', fontsize=fontsize_axis)
ax.set_xlabel(r'Moments', fontsize=fontsize_axis)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
ax.set_xticklabels([])
ax.set_xticks([])
plt.show()
fig.savefig('/home/jrodriguez/NH_HC/results/model_v2/fit/fit_kappas.pdf', format='pdf')
plt.close()


#rho_theta_epsilon
ind = ind + 1
pos = 20
#B. t=5, kappas
for c in range(1):
	ws['B' + str(c + pos)] = np.float(betas_init_prod[c])
	ws['D' + str(c + pos)] = np.float(moments_vector[ind + c,0])
	ws['F' + str(c + pos)] = np.float(se_vector[ind + c])

wb.save('/home/jrodriguez/NH_HC/results/model_v2/fit/fit.xlsx')
