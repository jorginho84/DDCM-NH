
#build a grid around parameter value
lenght = 0.05
size_grid = 4
max_p = rho1 + 0.3
min_p = rho1 - 0.3
p_list = np.linspace(min_p,max_p,size_grid)
obs_moment = moments_vector[14,0].copy()

#draft: try updating a parameter
target_moment = np.zeros((size_grid,))
for i in range(size_grid): 
	param0.gamma3 = p_list[i].copy()
	emax_instance=output_ins.emax(param0,model)
	choices=output_ins.samples(param0,emax_instance,model)
	dic_betas=output_ins.aux_model(choices)
	target_moment[i] = np.mean(dic_betas['beta_inputs'][2,:],axis=0)



#Back to original
exec(open("/home/jrodriguez/NH_HC/codes/model_v2/checks/identification_check/load_param.py").read())

#the graph
fig, ax=plt.subplots()
plot1=ax.plot(p_list,target_moment,'b-o',label='Simulated',alpha=0.9)
plot2=ax.plot(p_list,np.full((size_grid,),obs_moment),'b-.',label='Observed',alpha=0.9)
plt.setp(plot1,linewidth=3)
plt.setp(plot2,linewidth=3)
ax.legend()
ax.set_ylabel(r'$Corr(\tau_t, SSRS_t)$',fontsize=font_size)
ax.set_xlabel(r'Scale ($\rho_1$)',fontsize=font_size)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
ax.legend(loc=0)
plt.show()
fig.savefig('/home/jrodriguez/NH_HC/results/model_v2/checks/rho1.pdf', format='pdf')
plt.close()

