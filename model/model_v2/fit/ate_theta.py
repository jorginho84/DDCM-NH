#Age of child
age_ch = np.zeros((N,9))
for t in range(9):
	age_ch[:,t] = agech0[:,0] + t

boo_y = age_ch[:,2]<=6
boo_o = age_ch[:,2]>6

ltheta = np.log(choices['theta_matrix'])

for j in range (M):
	for t in range(9):
		ltheta[:,t,j] = (ltheta[:,t,j])/np.std(ltheta[:,t,j],axis=0)


ate_ltheta_y = np.mean(np.mean(ltheta[(passign[:,0]==1) & (boo_y),:,:],axis=0) - np.mean(ltheta[(passign[:,0]==0) & (boo_y),:,:],axis=0),axis=1)
ate_ltheta_o = np.mean(np.mean(ltheta[(passign[:,0]==1) & (boo_o),:,:],axis=0) - np.mean(ltheta[(passign[:,0]==0) & (boo_o),:,:],axis=0),axis=1)
ate_ltheta = np.mean(np.mean(ltheta[(passign[:,0]==1) ,:,:],axis=0) - np.mean(ltheta[(passign[:,0]==0),:,:],axis=0),axis=1)

#Figure
nper = ate_ltheta.shape[0]
fig, ax=plt.subplots()
x = np.array(range(1,nper))
y_1 = ate_ltheta[1:]
y_2 = ate_ltheta_y[1:]
y_3 = ate_ltheta_o[1:]
plot1=ax.plot(x,y_1,'k-',label='Overall',alpha=0.9)
plot2=ax.plot(x,y_2,'k--',label='Young',alpha=0.9)
plot3=ax.plot(x,y_3,'k:',label='Old',alpha=0.9)
plt.setp(plot1,linewidth=3)
plt.setp(plot2,linewidth=3)
plt.setp(plot3,linewidth=3)
ax.set_ylabel(r'Impact on academic achievement ($\sigma$s)', fontsize=14)
ax.set_xlabel(r'Years after random assignment ($t$)', fontsize=14)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
ax.legend(['Overall','Young','Old'])
plt.show()
fig.savefig('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ate_theta.pdf', format='pdf')
plt.close()
