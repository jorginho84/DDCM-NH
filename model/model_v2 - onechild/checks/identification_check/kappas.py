
def kappas_iden(k,t,min_p,max_p,size_grid,fon):
	"""
	period t {2,5}
	"""

#build a grid around parameter value
	p_list = np.linspace(min_p,max_p,size_grid)
	if t==2:
		obs_moment = moments_vector[16,0].copy()
	
	else:
		obs_moment = moments_vector[17 + k,0].copy()
	
	target_moment = np.zeros((size_grid,))
	for i in range(size_grid):
		if t==2:
			param0.kappas[0] = p_list[i].copy()
		
		else:
			if k == 0:
				param0.kappas[1] = p_list[i].copy()
			else:
				param0.sigma_z[1] = p_list[i].copy()
		
		emax_instance=output_ins.emax(param0,model)
		choices=output_ins.samples(param0,emax_instance,model)
		dic_betas=output_ins.aux_model(choices)
		if t == 2:
			target_moment[i] = np.mean(dic_betas['beta_kappas_t' + str(t)])
		else:
			target_moment[i] = np.mean(dic_betas['beta_kappas_t' + str(t)][k,:])


	#Back to original
	exec(open("/home/jrodriguez/NH_HC/codes/model_v2/checks/identification_check/load_param.py").read())


	#the graph
	fig, ax=plt.subplots()
	plot1=ax.plot(p_list,target_moment,'b-o',label='Simulated',alpha=0.9)
	plot2=ax.plot(p_list,np.full((size_grid,),obs_moment),'b-.',label='Observed',alpha=0.9)
	plt.setp(plot1,linewidth=3)
	plt.setp(plot2,linewidth=3)
	ax.legend(loc=4)
	if t == 2:
		ax.set_ylabel(r'$E(SSRS_2)$', fontsize=fon)
		ax.set_xlabel(r'Constant in measurement equation', fontsize=fon)

	else:
		if k == 0:
			ax.set_ylabel(r'$E(SSRS_5)$', fontsize=fon)
			ax.set_xlabel(r'Constant in measurement equation', fontsize=fon)
		else:
			ax.set_ylabel(r'$Var(SSRS_5)$', fontsize=fon)
			ax.set_xlabel(r'Variance in measurement equation', fontsize=fon)

	ax.spines['right'].set_visible(False)
	ax.spines['top'].set_visible(False)
	ax.yaxis.set_ticks_position('left')
	ax.xaxis.set_ticks_position('bottom')
	ax.legend(loc=0)
	plt.show()
	if t == 2:
		fig.savefig('/home/jrodriguez/NH_HC/results/model_v2/checks/kappa_t' + str(t) + '.pdf', format='pdf')
	else:
		if k == 0:
			fig.savefig('/home/jrodriguez/NH_HC/results/model_v2/checks/kappa_t' + str(t) + '.pdf', format='pdf')
		else: 
			fig.savefig('/home/jrodriguez/NH_HC/results/model_v2/checks/Variance' + str(t) + '.pdf', format='pdf')
	plt.close()


size_grid = 4

kappas_iden(0,2,kappas[0] - 0.1,kappas[0] + 0.1,size_grid,font_size)
kappas_iden(0,5,kappas[1] - 0.1,kappas[1] + 0.1,size_grid,font_size)
kappas_iden(1,5,sigma_z[1] - 0.1,sigma_z[1] + 0.1,size_grid,font_size)




