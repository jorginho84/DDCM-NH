emp = choices['hours_matrix']>=15

#simulated
ate_emp = np.mean(np.mean(emp[passign[:,0]==1,:,:],axis=0) - np.mean(emp[passign[:,0]==0,:,:],axis=0),axis=1 )

#data
dofile = "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/fit/ate_emp.do"
cmd = ["stata-mp", "do", dofile]
subprocess.call(cmd)
ate_emp_obs=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ate_emp.csv').values
se_ate_emp_obs=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/se_ate_emp.csv').values


ate_emp_obs_long=np.empty((ate_emp.shape))
ate_emp_obs_long[:] =np.NAN
se_ate_emp_obs_long=np.empty((ate_emp.shape))
se_ate_emp_obs_long[:] =np.NAN 

i = 0
for x in [0,1,4,7]:
	ate_emp_obs_long[x] = ate_emp_obs[i,0]
	se_ate_emp_obs_long[x] = se_ate_emp_obs[i,0]
	i = i + 1

#figure
s1mask = np.isfinite(ate_emp_obs_long)
nper = ate_emp_obs_long.shape[0]
fig, ax=plt.subplots()
x = np.array(range(0,nper))
plot1=ax.plot(x,ate_emp,'bo-',label='Simulated',alpha=0.9)
plot2=ax.plot(x[s1mask],ate_emp_obs_long[s1mask],'ko',label='Data',alpha=0.9)
plot3=ax.errorbar(x[s1mask],ate_emp_obs_long[s1mask],yerr=se_ate_emp_obs_long[s1mask],fmt='ko',ecolor='k',alpha=0.9)
plt.setp(plot1,linewidth=3)
plt.setp(plot2,linewidth=3)
plt.setp(plot3,linewidth=1)
ax.legend()
ax.set_xticks([-1,0, 1, 2, 3, 4,5,6,7,8,9])
ax.set_ylabel(r'Impact on employment')
ax.set_xlabel(r'Years after random assignment ($t$)')
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
plt.show()
fig.savefig('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ate_employment.pdf', format='pdf')
plt.close()

