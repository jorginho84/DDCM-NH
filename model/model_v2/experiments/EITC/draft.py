"""
execfile('draft.py')
"""
output_list_v2 = [ate_part,ate_full,ate_cc]
for k in range(3):
	for j in range(3):
		output_list[k+1][j] = output_list[k+1][j]*100

#number of periods to consider averaging
periods = [nperiods,nperiods,nperiods,3,nperiods-1]

with open('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/EITC/table_eitc_mech.tex','w') as f:
	f.write(r'\begin{tabular}{llccccc}'+'\n')	
	f.write(r'\hline'+'\n')
	f.write(r'Variable   && (1)   && (2)   && (3) \bigstrut[b]\\'+'\n')
	f.write(r'\cline{1-1}\cline{3-7}')
	for j in range(len(output_list)):
		f.write(outcome_list[j]+ '&&'+ '{:3.2f}'.format(np.mean(output_list[j][0][0:periods[j]]))  
			+'&& '+ '{:3.2f}'.format(np.mean(output_list[j][1][0:periods[j]])) 
			+'&& '+ '{:3.2f}'.format(np.mean(output_list[j][2][0:periods[j]])))
		f.write(r' \bigstrut[t]\\'+'\n')

	f.write(r'\hline'+'\n')
	f.write(r'EITC (1995-2003) &       & $\checkmark$ &       &       &       & $\checkmark$ \\'+'\n')
	f.write(r'Child care subsidy &       &       &       & $\checkmark$ &       & $\checkmark$ \bigstrut[b]\\'+'\n')
	f.write(r'\hline'+'\n')
	f.write(r'\end{tabular}%'+'\n')

