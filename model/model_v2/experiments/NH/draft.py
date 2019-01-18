"""
exec(open("/home/jrodriguez/NH_HC/codes/model/experiments/NH/draft.py").read())

This file computes a decomposition analysis of variables that explain ATE on theta

"""


#Choices
for periodt in range(nperiods-1):									

	for j in range(M):
		#theta0
		theta0 = []
		theta_00 = []
		theta_01 = []
		theta_00.append(choices_c['Choice_' + str(0)]['theta_matrix_a'][:,periodt,j])
		theta_00.append(choices_c['Choice_' + str(0)]['theta_matrix_b'][:,periodt,j])
		theta_01.append(choices_c['Choice_' + str(1)]['theta_matrix_a'][:,periodt,j])
		theta_01.append(choices_c['Choice_' + str(1)]['theta_matrix_b'][:,periodt,j])
		theta0.append(theta_00)
		theta0.append(theta_01)

		#the theta contribution
		ltheta_th1 = models[1].thetat(periodt,theta0[1],
			h_sim_matrix[0][:,periodt,j],cc_sim_matrix_a[0][:,periodt,j],
			cc_sim_matrix_b[0][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])
		ltheta_th0 = models[0].thetat(periodt,theta0[0],
			h_sim_matrix[0][:,periodt,j],cc_sim_matrix_a[0][:,periodt,j],
			cc_sim_matrix_b[0][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])

		ltheta_th1_aux = np.concatenate((ltheta_th1[0][d_childa[:,0]==1],
			ltheta_th1[1][d_childb[:,0]==1]),axis=0)

		ltheta_th0_aux = np.concatenate((ltheta_th0[0][d_childa[:,0]==1],
			ltheta_th0[1][d_childb[:,0]==1]),axis=0)

		ate_cont_theta[periodt,j] = np.mean(np.log(ltheta_th1_aux[boo_y]) - np.log(ltheta_th0_aux[boo_y]))/sd_matrix[periodt,j]
		

		#The leisure contribution
		ltheta_th1 = models[1].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[1][:,periodt,j],cc_sim_matrix_a[0][:,periodt,j],
			cc_sim_matrix_b[0][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])
		ltheta_th0 = models[0].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[0][:,periodt,j],cc_sim_matrix_a[0][:,periodt,j],
			cc_sim_matrix_b[0][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])
		
		ltheta_th1_aux = np.concatenate((ltheta_th1[0][d_childa[:,0]==1],
			ltheta_th1[1][d_childb[:,0]==1]),axis=0)

		ltheta_th0_aux = np.concatenate((ltheta_th0[0][d_childa[:,0]==1],
			ltheta_th0[1][d_childb[:,0]==1]),axis=0)


		ate_cont_lt[periodt,j] = np.mean(np.log(ltheta_th1_aux[boo_y]) - np.log(ltheta_th0_aux[boo_y]))/sd_matrix[periodt,j]
		


		
		#The CC contribution
		ltheta_th1 = models[1].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[1][:,periodt,j],cc_sim_matrix_a[1][:,periodt,j],
			cc_sim_matrix_b[1][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])
		ltheta_th0 = models[0].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[1][:,periodt,j],cc_sim_matrix_a[0][:,periodt,j],
			cc_sim_matrix_b[0][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])
		
		ltheta_th1_aux = np.concatenate((ltheta_th1[0][d_childa[:,0]==1],
			ltheta_th1[1][d_childb[:,0]==1]),axis=0)

		ltheta_th0_aux = np.concatenate((ltheta_th0[0][d_childa[:,0]==1],
			ltheta_th0[1][d_childb[:,0]==1]),axis=0)

		ate_cont_cc[periodt,j] = np.mean(np.log(ltheta_th1_aux[boo_y]) - np.log(ltheta_th0_aux[boo_y]))/sd_matrix[periodt,j]
		

	
		#The consumption contribution
		ltheta_th1 = models[1].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[1][:,periodt,j],cc_sim_matrix_a[1][:,periodt,j],
			cc_sim_matrix_b[1][:,periodt,j],
			ct_sim_matrix[1][:,periodt,j])
		ltheta_th0 = models[0].thetat(periodt,theta_sim_matrix[1][:,periodt,j],
			h_sim_matrix[1][:,periodt,j],cc_sim_matrix_a[1][:,periodt,j],
			cc_sim_matrix_b[1][:,periodt,j],
			ct_sim_matrix[0][:,periodt,j])

		ltheta_th1_aux = np.concatenate((ltheta_th1[0][d_childa[:,0]==1],
			ltheta_th1[1][d_childb[:,0]==1]),axis=0)

		ltheta_th0_aux = np.concatenate((ltheta_th0[0][d_childa[:,0]==1],
			ltheta_th0[1][d_childb[:,0]==1]),axis=0)

		ate_cont_ct[periodt,j] = np.mean(np.log(ltheta_th1_aux[boo_y]) - np.log(ltheta_th0_aux[boo_y]))/sd_matrix[periodt,j]
		
