#Age of child
age_chi = np.zeros((agech0.shape[0],nperiods))

for x in range(0,nperiods):
	age_chi[:,x] = agech0[:,0] + x


boo_y = age_chi[:,2]<=6
boo_o = age_chi[:,2]>6

ltheta = np.log(choices['theta_matrix'])

for j in range (M):
	for t in range(8):
		ltheta[:,t,j] = (ltheta[:,t,j])/np.std(ltheta[:,t,j],axis=0)

ate_ltheta_y = np.mean(np.mean(ltheta[(passign[:,0]==1) & (boo_y),:,:],axis=0) - np.mean(ltheta[(passign[:,0]==0) & (boo_y),:,:],axis=0),axis=1)
ate_ltheta_o = np.mean(np.mean(ltheta[(passign[:,0]==1) & (boo_o),:,:],axis=0) - np.mean(ltheta[(passign[:,0]==0) & (boo_o),:,:],axis=0),axis=1)
ate_ltheta = np.mean(np.mean(ltheta[(passign[:,0]==1) ,:,:],axis=0) - np.mean(ltheta[(passign[:,0]==0),:,:],axis=0),axis=1)

#Figure
nper = ate_ltheta.shape[0]
fig, ax=plt.subplots()
x = np.array(range(1,nper))
y_2 = ate_ltheta_y[1:]
plot2=ax.plot(x,y_2,'k-',label='Young',alpha=0.9)
plt.setp(plot2,linewidth=3)
#ax.annotate(r'$\Delta Pr($top 30%$)$=' + '{:04.2f}'.format(beta_t2[1]), xy=(2, y_2[1]), xytext=(2, y_2[1]+0.01),arrowprops=dict(facecolor='black', shrink=0.05),size = 15)
#ax.annotate(r'$\Delta Pr($top 30%$)$=' + '{:04.3f}'.format(beta_t5[1]), xy=(5, y_2[4]), xytext=(5, y_2[5]+0.02),arrowprops=dict(facecolor='black', shrink=0.05),size = 15)
ax.set_ylabel(r'Impact on academic achievement ($\sigma$s)', fontsize=15)
ax.set_xlabel(r'Years after random assignment ($t$)', fontsize=15)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
plt.yticks(fontsize=15)
plt.xticks(fontsize=15)
plt.show()
fig.savefig('/home/jrodriguez/NH_HC/results/model_v2/fit/ate_theta_young.pdf', format='pdf')
plt.close()

