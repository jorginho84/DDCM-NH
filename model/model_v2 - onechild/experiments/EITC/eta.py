##############################################################################
#######The instance for computing samples with EITC#########################
###############################################################################
eitc_list = [eitc_list_1,eitc_list_2,eitc_list_3,eitc_list_4,eitc_list_5]

#Defines the instance with parameters
param0=util.Parameters(alphap,alphaf,eta,gamma1,gamma2,gamma3,
	tfp,sigma2theta, rho_theta_epsilon,wagep_betas, marriagep_betas, kidsp_betas, 
	eitc_original,afdc_list,snap_list,cpi,lambdas,kappas,pafdc,psnap,mup)


#The model (utility instance)
hours = np.zeros(N)
childcare  = np.zeros(N)

model  = util.Utility(param0,N,x_w,x_m,x_k,passign,
	nkids0,married0,hours,childcare,agech0,hours_p,hours_f,wr,cs,ws)

output_ins=estimate.Estimate(nperiods,param0,x_w,x_m,x_k,x_wmk,passign,agech0,nkids0,
	married0,D,dict_grid,M,N,moments_vector,w_matrix,hours_p,hours_f,
	wr,cs,ws)

#build a grid around parameter value
lenght = 0.1
size_grid = 6
max_p = 0.22
min_p = 0.1
p_list = np.linspace(min_p,max_p,size_grid)
obs_moment = moments_vector[0,0].copy()


target_moment_original = np.zeros((size_grid,))
for i in range(size_grid): 
	param0.eta = p_list[i]
	emax_instance=output_ins.emax(param0,model)
	choices=output_ins.samples(param0,emax_instance,model)
	dic_betas=output_ins.aux_model(choices)
	target_moment_original[i] = np.mean(dic_betas['beta_childcare'],axis=0)


##############################################################################
####The instance for computing samples with no EITC##
##############################################################################
target_moment_noeitc = np.zeros((size_grid,))


param0=util.Parameters(alphap,alphaf,eta,gamma1,gamma2,gamma3,
	tfp,sigma2theta, rho_theta_epsilon,wagep_betas, marriagep_betas, kidsp_betas, 
	eitc_list[3],afdc_list,snap_list,cpi,lambdas,kappas,pafdc,psnap,mup)

output_ins=estimate.Estimate(nperiods,param0,x_w,x_m,x_k,x_wmk,passign,agech0,nkids0,
	married0,D,dict_grid,M,N,moments_vector,var_cov,hours_p,hours_f,
	wr,cs,ws)

model_eitc = Budget(param0,N,x_w,x_m,x_k,passign,nkids0,married0,
	hours,childcare,agech0,hours_p,hours_f,wr,cs,ws)

for i in range(size_grid): 
	param0.eta = p_list[i]
	emax_instance=output_ins.emax(param0,model_eitc)
	choices=output_ins.samples(param0,emax_instance,model_eitc)
	dic_betas=output_ins.aux_model(choices)
	target_moment_noeitc[i] = np.mean(dic_betas['beta_childcare'],axis=0)


##############################################################################
####The graph##
##############################################################################
#Back to original
execfile('/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/checks/identification_check/load_param.py')


#the graph
fig, ax=plt.subplots()
plot1=ax.plot(p_list,target_moment_original,'b-o',label='Simulated w/ EITC',alpha=0.9)
plot2=ax.plot(p_list,target_moment_noeitc,'r-^',label='Simulated w/o EITC',alpha=0.9)
plot3=ax.plot(p_list,np.full((size_grid,),obs_moment),'b-.',label='Observed',alpha=0.9)
plt.setp(plot1,linewidth=3)
plt.setp(plot2,linewidth=3)
plt.setp(plot3,linewidth=3)
ax.legend()
ax.set_ylabel(r'Child care',fontsize=font_size)
ax.set_xlabel(r'Preference for $\theta$ ($\eta$)',fontsize=font_size)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
ax.legend(loc=0)
plt.show()
fig.savefig('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/EITC/eta_check_eitc.pdf', format='pdf')
plt.close()