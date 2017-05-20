
#Opening workbook

wb=openpyxl.load_workbook('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/fit.xlsx')
ws = wb["new_moments_data"]

#A. Labor supply and child care decisions
list_aux = [beta_childcare,beta_hours1,beta_hours2,beta_hours3,beta_cc_home]
list_obs = [moments_vector[0,0],moments_vector[1,0],moments_vector[2,0],moments_vector[3,0],moments_vector[4,0]]
list_sig = [se_vector[0],se_vector[1],se_vector[2],se_vector[3],se_vector[4]]
for c in range(5):
	sim_moment = ws.cell('B' + str(c + 2))
	obs_moment = ws.cell('D' + str(c + 2))
	obs_sigma = ws.cell('F' + str(c + 2))
	sim_moment.value = np.float(list_aux[c])
	obs_moment.value = np.float(list_obs[c])
	obs_sigma.value = np.float(list_sig[c])

ind = 5
#B. Log wage equation
for c in range(6):
	sim_moment = ws.cell('B' + str(c + 7))
	obs_moment = ws.cell('D' + str(c + 7))
	obs_sigma = ws.cell('F' + str(c + 7))
	sim_moment.value = np.float(beta_wagep[c])
	obs_moment.value = np.float(moments_vector[ind+c,0])
	obs_sigma.value = np.float(se_vector[ind+c])

ind = ind + 6

#A. t=2, kappas
for c in range(4):
	sim_moment = ws.cell('B' + str(c + 13))
	obs_moment = ws.cell('D' + str(c + 13))
	obs_sigma = ws.cell('F' + str(c + 13))
	sim_moment.value = np.float(beta_kappas_t2[c])
	obs_moment.value = np.float(moments_vector[ind + c,0])
	obs_sigma.value = np.float(se_vector[ind + c])


ind = ind + 4
#B. t=5, kappas
for c in range(4):
	sim_moment = ws.cell('B' + str(c + 17))
	obs_moment = ws.cell('D' + str(c + 17))
	obs_sigma = ws.cell('F' + str(c + 17))
	sim_moment.value = np.float(beta_kappas_t5[c])
	obs_moment.value = np.float(moments_vector[ind + c,0])
	obs_sigma.value = np.float(se_vector[ind + c])


#C. Measures of academic achievement and family choices
ind = ind +4
#C. prod fn
list_aux = [beta_inputs]
list_obs = [moments_vector[ind:ind +4 ,0]]
list_sig = [se_vector[ind:ind + 4]]

for j in range(2):
	pos = 21
	for c in range(3): 
		sim_moment = ws.cell('B' + str(c + pos))
		obs_moment = ws.cell('D' + str(c + pos))
		obs_sigma = ws.cell('F' + str(c + pos))
		sim_moment.value = np.float(list_aux[0][c])
		obs_moment.value = np.float(list_obs[0][c])
		obs_sigma.value = np.float(list_sig[0][c])
		
	
wb.save('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/fit.xlsx')