
#Opening workbook

wb=openpyxl.load_workbook('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/fit.xlsx')
ws = wb["new_moments_data"]

#A. Labor supply and child care decisions
list_aux = [beta_childcare,beta_hours2,beta_hours3]
list_obs = [moments_vector[0,0],moments_vector[1,0],moments_vector[2,0]]
list_sig = [se_vector[0],se_vector[1],se_vector[2]]
for c in range(3):
	sim_moment = ws.cell('B' + str(c + 2))
	obs_moment = ws.cell('D' + str(c + 2))
	obs_sigma = ws.cell('F' + str(c + 2))
	sim_moment.value = np.float(list_aux[c])
	obs_moment.value = np.float(list_obs[c])
	obs_sigma.value = np.float(list_sig[c])

ind = 3
#B. Log wage equation
for c in range(5):
	sim_moment = ws.cell('B' + str(c + 5))
	obs_moment = ws.cell('D' + str(c + 5))
	obs_sigma = ws.cell('F' + str(c + 5))
	sim_moment.value = np.float(beta_wagep[c])
	obs_moment.value = np.float(moments_vector[ind+c,0])
	obs_sigma.value = np.float(se_vector[ind+c])

ind = ind + 5

#A. t=2, kappas
for c in range(4):
	sim_moment = ws.cell('B' + str(c + 10))
	obs_moment = ws.cell('D' + str(c + 10))
	obs_sigma = ws.cell('F' + str(c + 10))
	sim_moment.value = np.float(beta_kappas_t2[c])
	obs_moment.value = np.float(moments_vector[ind + c,0])
	obs_sigma.value = np.float(se_vector[ind + c])


ind = ind + 4
#B. t=5, kappas
for c in range(4):
	sim_moment = ws.cell('B' + str(c + 14))
	obs_moment = ws.cell('D' + str(c + 14))
	obs_sigma = ws.cell('F' + str(c + 14))
	sim_moment.value = np.float(beta_kappas_t5[c])
	obs_moment.value = np.float(moments_vector[ind + c,0])
	obs_sigma.value = np.float(se_vector[ind + c])


#C. Measures of academic achievement and family choices
ind = ind +4
#C.1 and C.2 Age>5 and Age<=5
list_aux = [beta_inputs_old_sim, beta_inputs_young_cc0_sim, 
beta_inputs_young_cc1_sim]
list_obs = [moments_vector[ind:ind + 3,0], moments_vector[ind+3 : ind + 6,0], 
moments_vector[ind+6 : ind + 9,0]]
list_sig = [se_vector[ind:ind + 3], se_vector[ind+3: ind + 6], 
se_vector[ind+6: ind + 9]]

for j in range(3):
	if j==0:
		pos = 18
	elif j==1:
		pos = 21
	else:
		pos = 24
	
	for c in range(3): # 3 moments each
		sim_moment = ws.cell('B' + str(c + pos))
		obs_moment = ws.cell('D' + str(c + pos))
		obs_sigma = ws.cell('F' + str(c + pos))
		sim_moment.value = np.float(list_aux[j][c])
		obs_moment.value = np.float(list_obs[j][c])
		obs_sigma.value = np.float(list_sig[j][c])



wb.save('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/fit.xlsx')