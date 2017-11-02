sim_list = [ate_hours_2[0],ate_hours_2[1],ate_cc_2,ate_inc[1]]
obs_list = [ate_hours_obs_2[0,0],ate_hours_obs_2[1,0],ate_cc_obs[0,0],ate_inc_obs_2[0,0]]
obs_list_se = [se_ate_hours_obs_2[0,0],se_ate_hours_obs_2[1,0],se_ate_cc_obs[0,0],se_ate_inc_obs_2[0,0]]
var_list = [r'Hours worked ($t=0$)', r'Hours worked ($t=1$)', r'Child care ($t=1$)',r'Log consumption ($t=1$)']

#writing the table
with open('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/table_validation.tex','w') as f:
	f.write(r'\begin{tabular}{llccc}'+'\n')
	f.write(r'\hline' + '\n')
	f.write(r'\textbf{Treatment effect} && \textbf{Simulated} && \textbf{Observed} \bigstrut\\' + '\n')
	f.write(r'\cline{1-1}\cline{3-3}\cline{5-5}&&&&  \bigstrut[t]\\' + '\n')
	for j in range(len(sim_list)):
		f.write(var_list[j]+' && ' + 
			'{:04.3f}'.format(sim_list[j]) + 
			r'  & &'+ '{:04.3f}'.format(obs_list[j])+r' \\'+'\n')
		f.write(r' & & & & ( '+ '{:04.3f}'.format(obs_list_se[j])+ r' )\\'+'\n')
		f.write(r'  &       &       &       &  \\'+'\n')

	

	f.write(r'\hline'+'\n')
	f.write(r'\end{tabular}' + '\n')
	f.close()



