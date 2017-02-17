#simulated: only until t=4 (t=5 almost no young)
nperiods = 5
cc_t = choices['choice_matrix']>=3
cc_t = cc_t[:,0:nperiods]
age_child = np.zeros((N,nperiods))
for x in range(nperiods):
	age_child[:,x]=agech0[:,0] + x


boo_young = age_child<=6
boo_t = passign[:,0]==1
boo_c = passign[:,0]==0

ate_cc = np.zeros((5))
for t in range(5):
	ate_cc[t] = np.mean(np.mean(cc_t[(boo_young[:,t]) & (boo_t),t,:],axis = 0) - np.mean(cc_t[(boo_young[:,t]) & (boo_c),t,:],axis = 0),axis=0)



#data
dofile = "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/fit/ate_cc.do"
cmd = ["stata-mp", "do", dofile]
subprocess.call(cmd)
ate_cc_obs=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ate_cc.csv').values
se_ate_cc_obs=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/se_ate_cc.csv').values

ate_cc_obs_long=np.empty((ate_cc.shape))
se_ate_cc_obs_long=np.empty((ate_cc.shape))
i = 0
for x in [1,4]:
	ate_cc_obs_long[x] = ate_cc_obs[i,0]
	se_ate_cc_obs_long[x] = se_ate_cc_obs[i,0]
	i = i + 1

#figure
s1mask = ate_cc_obs_long!=0
fig, ax=plt.subplots()
x = np.array(range(0,nperiods))
plot1=ax.plot(x,ate_cc,'bo-',label='Simulated',alpha=0.9)
plot2=ax.plot(x[s1mask],ate_cc_obs_long[s1mask],'ko',label='Data',alpha=0.9)
plot3=ax.errorbar(x[s1mask],ate_cc_obs_long[s1mask],yerr=se_ate_cc_obs_long[s1mask],fmt='ko',ecolor='k',alpha=0.9)
plt.setp(plot1,linewidth=3)
plt.setp(plot2,linewidth=3)
plt.setp(plot3,linewidth=1)
ax.legend()
ax.set_xticks([-1,0, 1, 2, 3, 4,5])
ax.set_ylabel(r'Impact on child care', fontsize=14)
ax.set_xlabel(r'Years after random assignment ($t$)', fontsize=14)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
plt.show()
fig.savefig('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ate_cc.pdf', format='pdf')
plt.close()
