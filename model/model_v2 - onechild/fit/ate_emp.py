part = choices['hours_matrix']==hours_p
full = choices['hours_matrix']==hours_f
hours = choices['hours_matrix'].copy()

#simulated
ate_part = np.mean(np.mean(part[(passign[:,0]==1) & (boo_sample==1),:,:],axis=0) - np.mean(part[(passign[:,0]==0) & (boo_sample==1),:,:],axis=0),axis=1 )
ate_full = np.mean(np.mean(full[(passign[:,0]==1) & (boo_sample==1),:,:],axis=0) - np.mean(full[(passign[:,0]==0) & (boo_sample==1),:,:],axis=0),axis=1 )
ate_hours = np.mean(np.mean(hours[(passign[:,0]==1) & (boo_sample==1),:,:],axis=0) - np.mean(hours[(passign[:,0]==0) & (boo_sample==1),:,:],axis=0),axis=1 )

se_ate_part = np.std(np.mean(part[(passign[:,0]==1) & (boo_sample==1),:,:],axis=0) - np.mean(part[(passign[:,0]==0) & (boo_sample==1),:,:],axis=0),axis=1 )
se_ate_full = np.mean(np.mean(full[(passign[:,0]==1) & (boo_sample==1),:,:],axis=0) - np.mean(full[(passign[:,0]==0) & (boo_sample==1),:,:],axis=0),axis=1 )
se_ate_hours = np.std(np.mean(hours[(passign[:,0]==1) & (boo_sample==1),:,:],axis=0) - np.mean(hours[(passign[:,0]==0) & (boo_sample==1),:,:],axis=0),axis=1 )

#data
dofile = "/home/jrodriguez/NH_HC/codes/model_v2/fit/ate_emp.do"
cmd = ["stata-se", "do", dofile]
subprocess.call(cmd)
ate_part_obs=pd.read_csv('/home/jrodriguez/NH_HC/results/model_v2/fit/ate_part.csv').values
se_ate_part_obs=pd.read_csv('/home/jrodriguez/NH_HC/results/model_v2/fit/se_ate_part.csv').values
ate_full_obs=pd.read_csv('/home/jrodriguez/NH_HC/results/model_v2/fit/ate_full.csv').values
se_ate_full_obs=pd.read_csv('/home/jrodriguez/NH_HC/results/model_v2/fit/se_ate_full.csv').values
ate_hours_obs=pd.read_csv('/home/jrodriguez/NH_HC/results/model_v2/fit/ate_hours.csv').values
se_ate_hours_obs=pd.read_csv('/home/jrodriguez/NH_HC/results/model_v2/fit/se_ate_hours.csv').values


ate_sim_list = [ate_part,ate_full,ate_hours]
se_ate_list = [se_ate_part,se_ate_full,se_ate_hours]
ate_list = [ate_part_obs,ate_full_obs,ate_hours_obs]
se_list = [se_ate_part_obs,se_ate_full_obs,se_ate_hours_obs]
name_list = ["part-time employment", "full-time employment", "weekly hours worked"]
graph_list = ["part", "full", "hours"]


for j in range(3):
	ate_emp_obs_long=np.empty((ate_sim_list[j].shape))
	ate_emp_obs_long[:] =np.NAN
	se_ate_emp_obs_long=np.empty((ate_sim_list[j].shape))
	se_ate_emp_obs_long[:] =np.NAN 

	i = 0
	for x in [0,1,4,7]:
		ate_emp_obs_long[x] = ate_list[j][i,0]
		se_ate_emp_obs_long[x] = se_list[j][i,0]
		i = i + 1

	#figure
	s1mask = np.isfinite(ate_emp_obs_long)
	nper = ate_emp_obs_long.shape[0]
	fig, ax=plt.subplots()
	x = np.array(range(0,nper))
	plot1=ax.plot(x[0:3],ate_sim_list[j][0:3],'bs-',label='Simulated',alpha=0.6)
	plot4=ax.errorbar(x[0:3],ate_sim_list[j][0:3],yerr=se_ate_list[j][0:3],ecolor='b',alpha=0.6)
	plot2=ax.plot(x[s1mask][0:2]+0.05,ate_emp_obs_long[s1mask][0:2],'ko-',label='Data',alpha=0.9)
	plot3=ax.errorbar(x[s1mask][0:2]+0.05,ate_emp_obs_long[s1mask][0:2],yerr=se_ate_emp_obs_long[s1mask][0:2],fmt='ko',ecolor='k',alpha=0.9)
	plt.setp(plot1,linewidth=5)
	plt.setp(plot2,linewidth=5)
	plt.setp(plot3,linewidth=3)
	plt.setp(plot4,linewidth=3)
	ax.set_xticks([0, 1, 2])
	ax.set_xlim(-0.2,2.2)
	if j==2:
		ax.set_ylim(0,15)

	ax.set_ylabel(r'Impact on ' + name_list[j], fontsize=20)
	ax.set_xlabel(r'Years after random assignment ($t$)', fontsize=20)
	ax.spines['right'].set_visible(False)
	ax.spines['top'].set_visible(False)
	ax.yaxis.set_ticks_position('left')
	ax.xaxis.set_ticks_position('bottom')
	plt.yticks(fontsize=15)
	plt.xticks(fontsize=15)
	ax.legend(loc=1,fontsize=20)
	plt.show()
	fig.savefig('/home/jrodriguez/NH_HC/results/model_v2/fit/ate_' + graph_list[j] +'.pdf', format='pdf')
	plt.close()

