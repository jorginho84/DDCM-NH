ltheta = np.log(choices['theta_matrix'])
ate_ltheta = np.mean(np.mean(ltheta[passign[:,0]==1,:,:],axis=0) - np.mean(ltheta[passign[:,0]==0,:,:],axis=0),axis=1)
sd_ate = np.std(np.mean(ltheta[passign[:,0]==1,:,:],axis=0) - np.mean(ltheta[passign[:,0]==0,:,:],axis=0),axis=1)
ub = ate_ltheta + 1.96*sd_ate
lb = ate_ltheta - 1.96*sd_ate
zero = np.array([0,0,0,0,0,0,0,0])

#Figure
nper = ate_ltheta.shape[0]
fig, ax=plt.subplots()
x = np.array(range(1,nper))
y = ate_ltheta[1:]
plot1=ax.plot(x,y,'b-',label='Simulated',alpha=0.9)
plt.setp(plot1,linewidth=3)
ax.set_ylabel(r'Impact on academic achievement ($\ln \theta$)')
ax.set_xlabel(r'Years after random assignment ($t$)')
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
plt.show()
fig.savefig('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ate_theta.pdf', format='pdf')
plt.close()
