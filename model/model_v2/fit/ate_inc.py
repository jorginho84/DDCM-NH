income = choices['consumption_matrix']

#simulated
income_aux = income.copy()
income_aux[income_aux==0]=1
ate_inc = np.mean( np.mean(np.log(income_aux[passign[:,0]==1,:,:]),axis=0) - np.mean(np.log(income_aux[passign[:,0]==0,:,:]),axis=0),axis=1)

#data
dofile = "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/fit/ate_inc.do"
cmd = ["stata-mp", "do", dofile]
subprocess.call(cmd)
ate_inc_obs=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ate_inc_2.csv').values
se_ate_inc_obs=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/se_ate_inc_2.csv').values


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