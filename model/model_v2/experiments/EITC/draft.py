"""
execfile('draft.py')
"""

outcome_list = ['Consumption (US\$)', 'Part-time', 'Full-time', 'Child care',
r'$\ln \theta$ ($\sigma$s)', 'Utility']

output_list = ['Consumption', 'Part-time', 'Full-time', 'CC', 'Theta', 'Welfare']

with open('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/EITC/table_eitc_exp.tex','w') as f:
	f.write(r'\begin{tabular}{lcccccccccc}'+'\n')
	f.write(r'\hline'+'\n')
	f.write(r'ATE   &       & (1)   & & (2)   & & (3)   & & (4)   && (5) \bigstrut[b]\\'+'\n')
	f.write(r'\cline{1-1}\cline{3-11}'+'\n')
	for j in range(len(outcome_list)):
		
		if j==0: #consumption w/ no decimals
			
			f.write(outcome_list[j])
			for k in range(len(experiments)): #the policy loop
				f.write(r'  && '+ '{:02.0f}'.format(dics[k][output_list[j]]))
			f.write(r' \bigstrut[t]\\'+'\n')
		else:
			f.write(outcome_list[j])
			for k in range(len(experiments)): #the policy loop
				f.write(r'  && '+ '{:04.3f}'.format(dics[k][output_list[j]]))
			f.write(r' \bigstrut[t]\\'+'\n')

	f.write(r'\hline'+'\n')
	f.write(r'\textit{Treatment group} &&&&&&&&&&  \bigstrut[t]\\'+'\n')
	f.write(r'EITC (1995-2003) &       & $\checkmark$ &       & $\checkmark$ &       & $\checkmark$ &       & $\checkmark$ &       & $\checkmark$ \\'+'\n')
	f.write(r'Child care subsidy &       &       &       &       &       & $\checkmark$ &       & $\checkmark$ &       & $\checkmark$ \bigstrut[b]\\'+'\n')
	f.write(r'\hline'+'\n')
	f.write(r'\textit{Control group} &       &       &       &       &       &       &       &       &       &  \bigstrut[t]\\'+'\n')
	f.write(r'EITC (1995-2003) &       &       &       &       &       & $\checkmark$ &       &       &       &  \\'+'\n')
	f.write(r'EITC (1994) &       &       &       & $\checkmark$ &       &       &       & $\checkmark$ &       &  \\'+'\n')
	f.write(r'No EITC &       & $\checkmark$ &       &       &       &       &       &       &       & $\checkmark$ \bigstrut[b]\\'+'\n')
	f.write(r'\hline'+'\n')
	f.write(r'\end{tabular}'+'\n')



