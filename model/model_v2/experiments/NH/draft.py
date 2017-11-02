"""
execfile('draft.py')

"""


#Computing contribution to ATE theta by age [young,old,overall]
ate_cont_theta  = [np.zeros((nperiods-1,M)),np.zeros((nperiods-1,M)),np.zeros((nperiods-1,M))]
ate_cont_lt  = [np.zeros((nperiods-1,M)),np.zeros((nperiods-1,M)),np.zeros((nperiods-1,M))]
ate_cont_cc  = [np.zeros((nperiods-1,M)),np.zeros((nperiods-1,M)),np.zeros((nperiods-1,M))]
ate_cont_ct  = [np.zeros((nperiods-1,M)),np.zeros((nperiods-1,M)),np.zeros((nperiods-1,M))]


for periodt in range(nperiods-1):									

	for j in range(M):
	#the theta contribution
	
		
		#the sample
		boo_y = (h_sim_matrix[1][:,0,j]==40) & (h_sim_matrix[0][:,0,j]<40) & (age_ch[:,2]<=6)
		boo_o = (((h_sim_matrix[1][:,0,j]==40) & (h_sim_matrix[0][:,0,j]==40)) | (h_sim_matrix[1][:,0,j]<40)) & (age_ch[:,2]<=6)
		boo_all = (age_ch[:,2]<=6)
		
		ltheta_th1 = models[1].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[0][:,periodt,j],cc_sim_matrix[0][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])
		ltheta_th0 = models[0].thetat(periodt,theta_sim_matrix[0][:,periodt,j],
			h_sim_matrix[0][:,periodt,j],cc_sim_matrix[0][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])
		ate_cont_theta[0][periodt,j] = np.mean(np.log(ltheta_th1[boo_y]) - np.log(ltheta_th0[boo_y]))/sd_matrix[periodt,j]
		ate_cont_theta[1][periodt,j] = np.mean(np.log(ltheta_th1[boo_o]) - np.log(ltheta_th0[boo_o]))/sd_matrix[periodt,j]
		ate_cont_theta[2][periodt,j] = np.mean(np.log(ltheta_th1[boo_all]) - np.log(ltheta_th0[boo_all]))/sd_matrix[periodt,j]


	#The leisure contribution
		ltheta_th1 = models[1].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[1][:,periodt,j],cc_sim_matrix[0][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])
		ltheta_th0 = models[0].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[0][:,periodt,j],cc_sim_matrix[0][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])
		ate_cont_lt[0][periodt,j] = np.mean(np.log(ltheta_th1[boo_y]) - np.log(ltheta_th0[boo_y]))/sd_matrix[periodt,j]
		ate_cont_lt[1][periodt,j] = np.mean(np.log(ltheta_th1[boo_o]) - np.log(ltheta_th0[boo_o]))/sd_matrix[periodt,j]
		ate_cont_lt[2][periodt,j] = np.mean(np.log(ltheta_th1[boo_all]) - np.log(ltheta_th0[boo_all]))/sd_matrix[periodt,j]

	#The CC contribution
		ltheta_th1 = models[1].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[1][:,periodt,j],cc_sim_matrix[1][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])
		ltheta_th0 = models[0].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[1][:,periodt,j],cc_sim_matrix[0][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])
		ate_cont_cc[0][periodt,j] = np.mean(np.log(ltheta_th1[boo_y]) - np.log(ltheta_th0[boo_y]))/sd_matrix[periodt,j]
		ate_cont_cc[1][periodt,j] = np.mean(np.log(ltheta_th1[boo_o]) - np.log(ltheta_th0[boo_o]))/sd_matrix[periodt,j]
		ate_cont_cc[2][periodt,j] = np.mean(np.log(ltheta_th1[boo_all]) - np.log(ltheta_th0[boo_all]))/sd_matrix[periodt,j]

	#The consumption contribution
		ltheta_th1 = models[1].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[1][:,periodt,j],cc_sim_matrix[1][:,periodt,j],
			ct_sim_matrix[1][:,periodt,j])
		ltheta_th0 = models[0].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[1][:,periodt,j],cc_sim_matrix[1][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])
		ate_cont_ct[0][periodt,j] = np.mean(np.log(ltheta_th1[boo_y]) - np.log(ltheta_th0[boo_y]))/sd_matrix[periodt,j]
		ate_cont_ct[1][periodt,j] = np.mean(np.log(ltheta_th1[boo_o]) - np.log(ltheta_th0[boo_o]))/sd_matrix[periodt,j]
		ate_cont_ct[2][periodt,j] = np.mean(np.log(ltheta_th1[boo_all]) - np.log(ltheta_th0[boo_all]))/sd_matrix[periodt,j]

	
###The graphs##

exp = ['extensive-margin', 'intensive-margin', 'overall']

for j in range(3): #the experiment loop
	x = np.array(range(1,nperiods))
	y1 = np.mean(ate_cont_theta[j],axis=1)
	y2 = np.mean(ate_cont_lt[j],axis=1)
	y3 = np.mean(ate_cont_cc[j],axis=1)
	y4 = np.mean(ate_cont_ct[j],axis=1)
	total = y1 + y2 + y3 + y4

	fig, ax=plt.subplots()
	ax.plot(x,y2, color='k',linewidth=3,marker='o')
	ax.bar(x,y1, color='k' ,alpha=.8,bottom=y2,align='center')
	ax.bar(x,y3, color='k' , alpha=.4, bottom=y1+y2,align='center')
	ax.bar(x,y4,color='w',bottom=y3+y1+y2,align='center',edgecolor='k',
		linewidth=1)
	ax.set_ylabel(r'Effect on child human capital ($\sigma$s)', fontsize=14)
	ax.set_xlabel(r'Years after random assignment ($t$)', fontsize=14)
	ax.spines['right'].set_visible(False)
	ax.spines['top'].set_visible(False)
	ax.yaxis.set_ticks_position('left')
	ax.xaxis.set_ticks_position('bottom')
	ax.margins(0, 0)
	ax.set_ylim(-0.03,.18)
	ax.legend(['Time', r'$\theta_t$','Child care','Consumption'],loc=4)
	plt.show()
	fig.savefig('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/NH/mech_' + exp[j] + '.pdf', format='pdf')
	plt.close()



#Contribution % pc
j=0
ate_cont_ct_pc = np.mean(ate_cont_ct[j],axis=1)/ (np.mean(ate_cont_theta[j],axis=1)+ np.mean(ate_cont_lt[j],axis=1) + np.mean(ate_cont_cc[j],axis=1) + np.mean(ate_cont_ct[j],axis=1))
np.mean(ate_cont_cc[j],axis=1)/ (np.mean(ate_cont_theta[j],axis=1)+ np.mean(ate_cont_lt[j],axis=1) + np.mean(ate_cont_cc[j],axis=1) + np.mean(ate_cont_ct[j],axis=1))
np.mean(ate_cont_lt[j],axis=1)/ (np.mean(ate_cont_theta[j],axis=1)+ np.mean(ate_cont_lt[j],axis=1) + np.mean(ate_cont_cc[j],axis=1) + np.mean(ate_cont_ct[j],axis=1))

#Impact of income, sd units, for 1st period
ate_theta_sim_sd[1]*ate_cont_ct_pc[0] 

(y2[0] + y3[0] + y4[0])*gamma1

#additional income
income = []
income.append(choices_c['Choice_0']['income_matrix'])
income.append(choices_c['Choice_1']['income_matrix'])

np.mean(np.mean(income[1] - income[0],axis=2),axis=0)