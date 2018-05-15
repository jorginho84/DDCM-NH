#simulated: only until t=4 (t=5 almost no young)
nperiods = 5
cc_t = choices['choice_matrix']>=3
cc_t = cc_t[:,0:nperiods,:]
age_child = np.zeros((N,nperiods))
for x in range(nperiods):
	age_child[:,x]=agech0[:,0] + x

#sample: young by t=2 (to be consistent with data)
boo_young = age_t2<=6
boo_t = passign[:,0]==1
boo_c = passign[:,0]==0

ate_cc = np.zeros((5))
se_ate_cc = np.zeros((5))
for t in range(5):
	ate_cc[t] = np.mean(np.mean(cc_t[(boo_young[:,t]) & (boo_t),t,:],axis = 0) - np.mean(cc_t[(boo_young[:,t]) & (boo_c),t,:],axis = 0),axis=0)
	se_ate_cc[t] = np.std(np.mean(cc_t[(boo_young[:,t]) & (boo_t),t,:],axis = 0) - np.mean(cc_t[(boo_young[:,t]) & (boo_c),t,:],axis = 0),axis=0)



#data
dofile = "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/fit/ate_cc.do"
cmd = ["stata-mp", "do", dofile]
subprocess.call(cmd)
ate_cc_obs=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ate_cc.csv').values
se_ate_cc_obs=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/se_ate_cc.csv').values

ate_cc_obs_long=np.zeros((ate_cc.shape))
se_ate_cc_obs_long=np.zeros((ate_cc.shape))
i = 0
for x in [1,4]:
	ate_cc_obs_long[x] = ate_cc_obs[i,0].copy()
	se_ate_cc_obs_long[x] = se_ate_cc_obs[i,0].copy()
	i = i + 1

#figure
s1mask = ate_cc_obs_long!=0
fig, ax=plt.subplots()
x = np.array(range(0,nperiods))
plot1=ax.plot(x[0:3],ate_cc[0:3]*100,'bs-',label='Simulated',alpha=0.6)
plot4=ax.errorbar(x[0:3],ate_cc[0:3]*100,yerr=se_ate_cc[0:3]*100,ecolor='b',alpha=0.6)
plot2=ax.plot(x[s1mask][0:1],ate_cc_obs_long[s1mask][0:1]*100,'ko-',label='Data',alpha=0.9)
plot3=ax.errorbar(x[s1mask][0:1],ate_cc_obs_long[s1mask][0:1]*100,yerr=se_ate_cc_obs_long[s1mask][0:1]*100,fmt='ko',ecolor='k',alpha=0.9)
plt.setp(plot1,linewidth=5)
plt.setp(plot2,markeredgewidth=5)
plt.setp(plot3,linewidth=3)
plt.setp(plot4,linewidth=3)
ax.legend(fontsize=20)
ax.set_xticks([0, 1, 2])
ax.set_xlim(-0.2,2.2)
ax.set_ylim(0,35)
ax.set_ylabel(r'Impact on child care (%)', fontsize=20)
ax.set_xlabel(r'Years after random assignment ($t$)', fontsize=20)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
plt.yticks(fontsize=15)
plt.xticks(fontsize=15)
plt.show()
fig.savefig('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ate_cc.pdf', format='pdf')
plt.close()


nper = 1
bar_width = 0.35
fig, ax=plt.subplots()
x = np.array(range(0,nper))
plot1=ax.bar(x,ate_cc[1],bar_width,label='Simulated',color='k',alpha=0.8)
plot2=ax.bar(x + bar_width,ate_cc_obs[0]*100,bar_width,yerr=se_ate_cc_obs[0,0],label='Data',edgecolor='k',
	color='k',alpha=0.4)
ax.legend(loc=8,fontsize=20)
ax.set_ylabel('Impact on child care (%)', fontsize=20)
ax.set_xlabel(r'$t=1$', fontsize=20)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
ax.set_xticklabels([])
ax.set_xticks([])
plt.yticks(fontsize=15)
plt.show()
fig.savefig('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ate_bars_cc.pdf', format='pdf')
plt.close()