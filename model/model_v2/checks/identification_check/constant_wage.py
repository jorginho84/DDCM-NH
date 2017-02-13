
#build a grid around parameter value
lenght = 0.05
size_grid = 5
max_p = wagep_betas[3,0] + lenght
min_p = wagep_betas[3,0] - lenght
p_list = np.linspace(min_p,max_p,size_grid)
obs_moment = moments_vector[6,0].copy()

#draft: try updating a parameter
target_moment = np.zeros((size_grid,))
for i in range(size_grid): 
	param0.betaw[3,0] = p_list[i]
	emax_instance=output_ins.emax(param0)
	choices=output_ins.samples(param0,emax_instance)
	dic_betas=output_ins.aux_model(choices)
	target_moment[i] = np.mean(dic_betas['beta_wagep'][3,:],axis=0)

#Back to original
execfile('/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/checks/identification_check/load_param.py')

#the graph
fig, ax=plt.subplots()
plot1=ax.plot(p_list,target_moment,'b-',label='Simulated',alpha=0.9)
plot2=ax.plot(p_list,np.full((size_grid,),obs_moment),'r-',label='Observed',alpha=0.9)
plot3=ax.plot(np.full((size_grid,),wagep_betas[3,0]),target_moment,'k--',label='Estimated parameter',alpha=0.9)
plt.setp(plot1,linewidth=3)
plt.setp(plot2,linewidth=3)
plt.setp(plot3,linewidth=3)
ax.legend()
ax.set_ylabel(r'Constant of observed wage regression')
ax.set_xlabel(r'Constant of wage offer process')
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
plt.show()
fig.savefig('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/checks/constant_wage.pdf', format='pdf')
plt.close()

