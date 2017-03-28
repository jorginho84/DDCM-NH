"""
execfile('draft.py')
"""
boo_y = age_ch<=6
boo_o = age_ch>6

for periodt in range(8):


	#the theta contribution
	for j in range(M):
		ltheta_th1 = models[1].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[0][:,periodt,j],cc_sim_matrix[0][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])
		ltheta_th0 = models[0].thetat(periodt,theta_sim_matrix[0][:,periodt,j],
			h_sim_matrix[0][:,periodt,j],cc_sim_matrix[0][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])
		ate_cont_theta[0][periodt,j] = np.mean(np.log(ltheta_th1[boo_y[:,periodt]]) - np.log(ltheta_th0[boo_y[:,periodt]]))
		ate_cont_theta[1][periodt,j] = np.mean(np.log(ltheta_th1[boo_o[:,periodt]]) - np.log(ltheta_th0[boo_o[:,periodt]]))


	#The leisure contribution
	for j in range(M):
		ltheta_th1 = models[1].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[1][:,periodt,j],cc_sim_matrix[0][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])
		ltheta_th0 = models[0].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[0][:,periodt,j],cc_sim_matrix[0][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])
		ate_cont_lt[0][periodt,j] = np.mean(np.log(ltheta_th1[boo_y[:,periodt]]) - np.log(ltheta_th0[boo_y[:,periodt]]))
		ate_cont_lt[1][periodt,j] = np.mean(np.log(ltheta_th1[boo_o[:,periodt]]) - np.log(ltheta_th0[boo_o[:,periodt]]))

	#The CC contribution
	for j in range(M):
		ltheta_th1 = models[1].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[1][:,periodt,j],cc_sim_matrix[1][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])
		ltheta_th0 = models[0].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[1][:,periodt,j],cc_sim_matrix[0][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])
		ate_cont_cc[0][periodt,j] = np.mean(np.log(ltheta_th1[boo_y[:,periodt]]) - np.log(ltheta_th0[boo_y[:,periodt]]))
		ate_cont_cc[1][periodt,j] = np.mean(np.log(ltheta_th1[boo_o[:,periodt]]) - np.log(ltheta_th0[boo_o[:,periodt]]))

	#The consumption contribution
	for j in range(M):
		ltheta_th1 = models[1].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[1][:,periodt,j],cc_sim_matrix[1][:,periodt,j],
			ct_sim_matrix[1][:,periodt,j])
		ltheta_th0 = models[0].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[1][:,periodt,j],cc_sim_matrix[1][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])
		ate_cont_ct[0][periodt,j] = np.mean(np.log(ltheta_th1[boo_y[:,periodt]]) - np.log(ltheta_th0[boo_y[:,periodt]]))
		ate_cont_ct[1][periodt,j] = np.mean(np.log(ltheta_th1[boo_o[:,periodt]]) - np.log(ltheta_th0[boo_o[:,periodt]]))

	


for j in range(2):
	print 'This is age', j
	print 'Contribution of theta', np.mean(ate_cont_theta[j],axis=1)
	print 'Contribution of hours', np.mean(ate_cont_lt[j],axis=1)
	print 'Contribution of child care', np.mean(ate_cont_cc[j],axis=1)
	print 'Contribution of consumption', np.mean(ate_cont_ct[j],axis=1)

