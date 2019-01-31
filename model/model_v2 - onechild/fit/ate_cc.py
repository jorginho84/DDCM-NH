#simulated: only until t=4 (t=5 almost no young)
nperiods = 5
cc_t_a=choices['childcare_a_matrix'].copy()
cc_t_b=choices['childcare_b_matrix'].copy()


cc_t = np.concatenate((cc_t_a[d_childa[:,0]==1,:,:],
	cc_t_a[d_childb[:,0]==1,:,:]),axis=0)

cc_t = cc_t[:,0:nperiods,:]

age_child_0 = np.concatenate((agech0_a[d_childa[:,0]== 1],
	agech0_b[d_childb[:,0]== 1]),axis=0)
age_child = np.zeros((age_child_0.shape[0],nperiods))

for x in range(0,nperiods):
	age_child[:,x] = age_child_0 + x

passign_aux=np.concatenate((passign[d_childa[:,0]==1,0],
	passign[d_childb[:,0]== 1,0]),axis=0)

#sample: young by t=2 (to be consistent with data)
boo_t = passign_aux==1
boo_c = passign_aux==0

boo_sample_aux = np.concatenate((boo_sample[d_childa[:,0]==1],
	boo_sample[d_childb[:,0]==1]),axis=0)

ate_cc = np.zeros((5))
se_ate_cc = np.zeros((5))
for t in range(5):
	ate_cc[t] = np.mean(np.mean(cc_t[(boo_sample_aux) & (boo_t),t,:],axis = 0) - np.mean(cc_t[(boo_sample_aux) & (boo_c),t,:],axis = 0),axis=0)
	se_ate_cc[t] = np.std(np.mean(cc_t[(boo_sample_aux) & (boo_t),t,:],axis = 0) - np.mean(cc_t[(boo_sample_aux) & (boo_c),t,:],axis = 0),axis=0)



#data
dofile = "/home/jrodriguez/NH_HC/codes/model/fit/ate_cc.do"
cmd = ["stata-se", "do", dofile]
subprocess.call(cmd)
ate_cc_obs=pd.read_csv('/home/jrodriguez/NH_HC/results/Model/fit/ate_cc.csv').values
se_ate_cc_obs=pd.read_csv('/home/jrodriguez/NH_HC/results/Model/fit/se_ate_cc.csv').values

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
plot2=ax.plot(x[s1mask][0:1]+0.05,ate_cc_obs_long[s1mask][0:1]*100,'ko-',label='Data',alpha=0.9)
plot3=ax.errorbar(x[s1mask][0:1]+0.05,ate_cc_obs_long[s1mask][0:1]*100,yerr=se_ate_cc_obs_long[s1mask][0:1]*100,fmt='ko',ecolor='k',alpha=0.9)
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
fig.savefig('/home/jrodriguez/NH_HC/results/Model/fit/ate_cc.pdf', format='pdf')
plt.close()


