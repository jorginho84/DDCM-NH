income = choices['consumption_matrix']
nperiods = 8

#simulated
income_aux = income.copy()
income_aux[income_aux==0]=1
ate_inc = np.mean( np.mean(np.log(income_aux[(passign[:,0]==1) & (boo_sample==1),:,:]),axis=0) - np.mean(np.log(income_aux[(passign[:,0]==0) & (boo_sample==1),:,:]),axis=0),axis=1)
se_ate_inc = np.std( np.mean(np.log(income_aux[(passign[:,0]==1) & (boo_sample==1),:,:]),axis=0) - np.mean(np.log(income_aux[(passign[:,0]==0) & (boo_sample==1),:,:]),axis=0),axis=1)

#data
dofile = "/home/jrodriguez/NH_HC/codes/model_v2/fit/ate_inc.do"
cmd = ["stata-se", "do", dofile]
subprocess.call(cmd)
ate_inc_obs=pd.read_csv('/home/jrodriguez/NH_HC/results/model_v2/fit/ate_inc_2.csv').values
se_ate_inc_obs=pd.read_csv('/home/jrodriguez/NH_HC/results/model_v2/fit/se_ate_inc_2.csv').values


ate_inc_obs_long=np.zeros((ate_inc.shape))
se_ate_inc_obs_long=np.zeros((ate_inc.shape))
i = 0
for x in [1]:
	ate_inc_obs_long[x] = ate_inc_obs[i,0].copy()
	se_ate_inc_obs_long[x] = se_ate_inc_obs[i,0].copy()
	i = i + 1



#figure
s1mask = ate_inc_obs_long!=0
fig, ax=plt.subplots()
x = np.array(range(0,nperiods))
plot1=ax.plot(x[0:3],ate_inc[0:3],'bs-',label='Simulated',alpha=0.6)
#plot4=ax.errorbar(x[0:3],ate_inc[0:3],yerr=se_ate_inc[0:3],ecolor='b',alpha=0.6)
plot2=ax.plot(x[s1mask][0:1]+0.05,ate_inc_obs_long[s1mask][0:1],'ko-',label='Data',alpha=0.9)
plot3=ax.errorbar(x[s1mask][0:1]+0.05,ate_inc_obs_long[s1mask][0:1],
	yerr=se_ate_inc_obs_long[s1mask][0:1],fmt='ko',ecolor='k',capsize=5,capthick=1,alpha=0.9)
plt.setp(plot1,linewidth=5)
plt.setp(plot2,linewidth=5)
plt.setp(plot3,linewidth=2)
plot3[-1][0].set_linestyle('--')
ax.set_xticks([0, 1, 2])
ax.set_xlim(-0.2,2.2)
ax.set_ylim(-0.2,1.5)
ax.set_ylabel(r'Impact on log consumption', fontsize=15)
ax.set_xlabel(r'Years after random assignment ($t$)', fontsize=15)
ax.legend(loc=1,fontsize=15)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
plt.yticks(fontsize=15)
plt.xticks(fontsize=15)
plt.show()
fig.savefig('/home/jrodriguez/NH_HC/results/model_v2/fit/ate_income.pdf', format='pdf')
plt.close()


