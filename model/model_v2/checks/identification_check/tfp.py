
#build a grid around parameter value
lenght = 0.02
size_grid = 5
max_p = tfp + lenght
min_p = tfp - lenght
p_list = np.linspace(min_p,max_p,size_grid)
obs_moment = moments_vector[20,0].copy()

#draft: try updating a parameter
target_moment = np.zeros((size_grid,))
qw = np.zeros((size_grid,))
for i in range(size_grid): 
	param0.tfp = p_list[i].copy()
	emax_instance=output_ins.emax(param0)
	choices=output_ins.samples(param0,emax_instance)
	dic_betas=output_ins.aux_model(choices)
	target_moment[i] = np.mean(dic_betas['beta_inputs_young_cc1'][2,:],axis=0)
	beta0=np.array([param0.eta,param0.alphap,param0.alphaf,
		param0.betaw[0],param0.betaw[1],param0.betaw[2],
		param0.betaw[3],np.log(param0.betaw[4]),
		syminv(param0.gamma1[0]),syminv(param0.gamma2[0]),
		syminv(param0.gamma1[1]),syminv(param0.gamma2[1]),param0.tfp,
		param0.kappas[0][0],param0.kappas[0][1], #kappa: t=2 
		param0.kappas[0][2],param0.kappas[0][3],#kappa: t=2 
		param0.kappas[1][0],param0.kappas[1][1],#kappa: t=5 
		param0.kappas[1][2],param0.kappas[1][3], #kappa: t=5
		])
	qw[i] = output_ins.ll(beta0)

#Back to original
execfile('/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/checks/identification_check/load_param.py')

#the graph
fig, ax=plt.subplots()
plot1=ax.plot(p_list,target_moment,'b-',label='Simulated',alpha=0.9)
plot2=ax.plot(p_list,np.full((size_grid,),obs_moment),'r-',label='Observed',alpha=0.9)
plot3=ax.plot(np.full((size_grid,),tfp),target_moment,'k--',label='Estimated parameter',alpha=0.9)
plt.setp(plot1,linewidth=3)
plt.setp(plot2,linewidth=3)
plt.setp(plot3,linewidth=3)
ax.legend()
ax.set_ylabel(r'$E(SSRS\mid cc=1)-E(SSRS\mid cc=0)$')
ax.set_xlabel(r'Productivity of child care (TFP)')
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
plt.show()
fig.savefig('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/checks/tfp.pdf', format='pdf')
plt.close()

fig, ax=plt.subplots()
plot1=ax.plot(p_list,qw,'b-',label='Objective function',alpha=0.9)
plt.setp(plot1,linewidth=3)
ax.legend(loc = 0)
ax.set_ylabel(r'Objective function')
ax.set_xlabel(r'Productivity of child care (TFP)')
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
plt.show()
fig.savefig('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/checks/qw_tfp.pdf', format='pdf')
plt.close()
