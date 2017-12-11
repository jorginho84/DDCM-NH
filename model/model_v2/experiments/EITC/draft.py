"""
execfile('draft.py')
"""
y = []
exp = ['eitc1_cc0', 'eitc0_cc1', 'eitc1_cc1']

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
	ax.set_ylim(-0.01,.35)
	ax.legend(['Time', r'$\theta_t$','Child care','Consumption'],loc=7)
	plt.show()
	fig.savefig('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/EITC/mech_' + exp[j] + '.pdf', format='pdf')
	plt.close()

	#this is for the next graph
	y.append(np.concatenate((np.array([0]),total),axis=0))


