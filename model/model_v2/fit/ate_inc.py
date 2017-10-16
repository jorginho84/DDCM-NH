income = choices['consumption_matrix']

#simulated
income_aux = income.copy()
income_aux[income_aux==0]=1
ate_inc = np.mean( np.mean(np.log(income_aux[passign[:,0]==1,:,:]),axis=0) - np.mean(np.log(income_aux[passign[:,0]==0,:,:]),axis=0),axis=1)

#data
dofile = "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/fit/ate_inc.do"
cmd = ["stata-mp", "do", dofile]
subprocess.call(cmd)
ate_inc_obs=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ate_inc.csv').values
se_ate_inc_obs=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/se_ate_inc.csv').values

ate_inc_obs_long=np.zeros((ate_inc.shape))
se_ate_inc_obs_long=np.zeros((ate_inc.shape))
i = 0
for x in [1,4,7]:
	ate_inc_obs_long[x] = ate_inc_obs[i,0].copy()
	se_ate_inc_obs_long[x] = se_ate_inc_obs[i,0].copy()
	i = i + 1


#figure
nper = ate_inc.shape[0]
s1mask = ate_inc_obs_long!=0
fig, ax=plt.subplots()
x = np.array(range(0,nper))
plot1=ax.plot(x,ate_inc,'bo-',label='Simulated',alpha=0.9)
plot2=ax.plot(x[s1mask],ate_inc_obs_long[s1mask],'ko',label='Data',alpha=0.9)
plot3=ax.errorbar(x[s1mask],ate_inc_obs_long[s1mask],yerr=se_ate_inc_obs_long[s1mask],fmt='ko',ecolor='k',alpha=0.9)
plt.setp(plot1,linewidth=3)
plt.setp(plot2,linewidth=3)
plt.setp(plot3,linewidth=1)
ax.legend()
ax.set_xticks([-1,0, 1, 2, 3, 4,5,6,7,8,9])
ax.set_ylabel(r'Impact on consumption pc (2003 dollars)', fontsize=14)
ax.set_xlabel(r'Years after random assignment ($t$)', fontsize=14)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
plt.show()
fig.savefig('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ate_income.pdf', format='pdf')
plt.close()

nper = 1
bar_width = 0.35
fig, ax=plt.subplots()
x = np.array(range(0,nper))
plot1=ax.bar(x,ate_inc[1],bar_width,label='Simulated',color='k',alpha=0.8)
plot2=ax.bar(x + bar_width,ate_inc_obs[0],bar_width,yerr=se_ate_inc_obs[0,0],label='Data',edgecolor='k',
	color='k',alpha=0.4)
ax.legend(loc=8,fontsize=20)
ax.set_ylabel('Log consumption', fontsize=20)
ax.set_xlabel(r'$t=1$', fontsize=20)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
ax.set_xticklabels([])
ax.set_xticks([])
ax.set_yticks([0,0.1,0.2,0.3,0.4])
plt.yticks(fontsize=15)
plt.show()
fig.savefig('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ate_bars_income.pdf', format='pdf')
plt.close()