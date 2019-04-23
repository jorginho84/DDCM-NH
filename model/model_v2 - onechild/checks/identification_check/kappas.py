
def kappas_iden(k,t,min_p,max_p,size_grid,fon):
	"""
	kappa k {1:4} in period t {2,5}
	"""

#build a grid around parameter value
	p_list = np.linspace(min_p,max_p,size_grid)
	if t==2:
		obs_moment = moments_vector[11 + k,0].copy()
	
	else:
		obs_moment = moments_vector[15 + k,0].copy()
	
	target_moment = np.zeros((size_grid,))
	for i in range(size_grid):
		if t==2:
			param0.kappas[0][k-1] = p_list[i].copy()
		
		else:
			param0.kappas[1][k-1] = p_list[i].copy()
		
		emax_instance=output_ins.emax(param0,model)
		choices=output_ins.samples(param0,emax_instance,model)
		dic_betas=output_ins.aux_model(choices)
		target_moment[i] = np.mean(dic_betas['beta_kappas_t' + str(t)][k-1,:],axis=0)


	#Back to original
	exec(open("/home/jrodriguez/NH_HC/codes/model_v2/checks/identification_check/load_param.py").read())


	#the graph
	fig, ax=plt.subplots()
	plot1=ax.plot(p_list,target_moment,'b-o',label='Simulated',alpha=0.9)
	plot2=ax.plot(p_list,np.full((size_grid,),obs_moment),'b-.',label='Observed',alpha=0.9)
	plt.setp(plot1,linewidth=3)
	plt.setp(plot2,linewidth=3)
	ax.legend(loc=4)
	ax.set_ylabel(r'$Pr(SSRS = '+str(k+1) + r')$', fontsize=fon)
	ax.set_xlabel(r'SSRS cutoff $\kappa_' + str(k) + r'$ ($t=' + str(t) + r')$', fontsize=fon)
	ax.spines['right'].set_visible(False)
	ax.spines['top'].set_visible(False)
	ax.yaxis.set_ticks_position('left')
	ax.xaxis.set_ticks_position('bottom')
	ax.legend(loc=0)
	plt.show()
	fig.savefig('/home/jrodriguez/NH_HC/results/model_v2/checks/kappa' + str(k) + '_t' + str(t) + '.pdf', format='pdf')
	plt.close()


list_kappas_l = [[[kappas[0][0]+0.25,kappas[0][0]-0.25],
[kappas[0][1]+0.25,kappas[0][1]-0.25],[kappas[0][2]+0.25,kappas[0][2]-0.25],
[kappas[0][3]+0.25,kappas[0][3]-0.25]],
[[kappas[1][0]+0.25,kappas[1][0]-0.25],
[kappas[1][1]+0.25,kappas[1][1]-0.25],[kappas[1][2]+0.25,kappas[1][2]-0.25],
[kappas[1][3]+0.25,kappas[1][3]-0.25]]]

size_grid = 4

for t in [2,5]:
	for k in range(1,5):
		if t==2:
			loc=0
		else:
			loc=1

		kappas_iden(k,t,list_kappas_l[loc][k-1][0],list_kappas_l[loc][k-1][1],
			size_grid,font_size)

