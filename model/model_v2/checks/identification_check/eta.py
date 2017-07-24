
#build a grid around parameter value
lenght = 0.1
size_grid = 8
max_p = eta + lenght
min_p = eta - lenght
p_list = np.linspace(min_p,max_p,size_grid)
obs_moment = moments_vector[0,0].copy()



target_moment = np.zeros((size_grid,))
for i in range(size_grid): 
	param0.eta= p_list[i]
	emax_instance = output_ins.emax(param0,model)
	choices = output_ins.samples(param0,emax_instance,model)
	dic_betas = output_ins.aux_model(choices)
	target_moment[i] = np.mean(dic_betas['beta_childcare'],axis=0) #The matrix is 1X1
	


#Back to original
execfile('/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/checks/identification_check/load_param.py')

#the graph
fig, ax=plt.subplots()
plot1=ax.plot(p_list,target_moment,'b-',label='Simulated',alpha=0.9)
plot2=ax.plot(p_list,np.full((size_grid,),obs_moment),'b-.',label='Observed',alpha=0.9)
plt.setp(plot1,linewidth=3)
plt.setp(plot2,linewidth=3)
ax.legend(loc = 0)
ax.set_ylabel(r'Child care')
ax.set_xlabel(r'Preference for $\ln\theta$ ($\eta$)')
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
plt.show()
fig.savefig('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/checks/eta.pdf', format='pdf')
plt.close()
