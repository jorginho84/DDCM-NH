income = choices['income_matrix']

#simulated
ate_inc = np.mean( np.mean(income[passign[:,0]==1,:,:],axis=0) - np.mean(income[passign[:,0]==0,:,:],axis=0),axis=1)

#data
dofile = "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/fit/ate_inc.do"
cmd = ["stata-mp", "do", dofile]
subprocess.call(cmd)
ate_inc_obs=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ate_inc.csv').values
se_ate_inc_obs=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/se_ate_inc.csv').values

#figure
nper = ate_inc_obs.shape[0]
fig, ax=plt.subplots()
x = np.array(range(0,nper))
plot1=ax.plot(x,ate_inc,'bo-',label='Simulated',alpha=0.9)
plot2=ax.plot(x,ate_inc_obs,'ko',label='Data',alpha=0.9)
plot3=ax.errorbar(x,ate_inc_obs,yerr=se_ate_inc_obs,fmt='ko',ecolor='k',alpha=0.9)
plt.setp(plot1,linewidth=3)
plt.setp(plot2,linewidth=3)
plt.setp(plot3,linewidth=1)
ax.legend()
ax.set_xticks([-1,0, 1, 2, 3, 4,5,6,7,8,9])
ax.set_ylabel(r'Impact on income (2003 dollars)')
ax.set_xlabel(r'Years after random assignment ($t$)')
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
plt.show()
fig.savefig('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ate_income.pdf', format='pdf')
plt.close()

