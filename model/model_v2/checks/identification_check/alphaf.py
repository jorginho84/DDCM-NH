
#build a grid around parameter value
lenght = 0.5
size_grid = 6
max_p = 0
min_p = -0.15
p_list = np.linspace(min_p,max_p,size_grid)
obs_moment = moments_vector[2,0].copy()

#draft: try updating a parameter
target_moment = np.zeros((size_grid,))
for i in range(size_grid): 
	param0.alphaf = p_list[i]
	print ''
	print ''
	print 'Getting a dictionary of emax'
	start_emax = time.time()
	print ''
	print ''

	emax_instance=output_ins.emax(param0,model)

	time_emax=time.time() - start_emax
	print ''
	print ''
	print 'Done with emax in:'
	print("--- %s seconds ---" % (time_emax))
	print ''
	print ''

	print ''
	print ''
	print 'Simulating data'
	start_simdata = time.time()
	print ''
	print ''

	choices=output_ins.samples(param0,emax_instance,model)
	dic_betas=output_ins.aux_model(choices)
	target_moment[i] = np.mean(dic_betas['beta_hours2'],axis=0)

	time_simdata=time.time() - start_simdata

	print ''
	print ''
	print 'Done with simulation in:'
	print("--- %s seconds ---" % (time_simdata))
	print ''
	print ''

	print 'Done with one parameter in '
	print("--- %s seconds ---" % (time_simdata + time_emax))
	


#Back to original
execfile('/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/checks/identification_check/load_param.py')

#the graph
fig, ax=plt.subplots()
plot1=ax.plot(p_list,target_moment,'b-o',label='Simulated',alpha=0.9)
plot2=ax.plot(p_list,np.full((size_grid,),obs_moment),'b-.',label='Observed',alpha=0.9)
plt.setp(plot1,linewidth=3)
plt.setp(plot2,linewidth=3)
ax.legend()
ax.set_ylabel(r'Proportion of full-time employment')
ax.set_xlabel(r'Preference for full-time labor ($\alpha^f$)')
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
plt.show()
fig.savefig('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/checks/alphaf_check.pdf', format='pdf')
plt.close()

