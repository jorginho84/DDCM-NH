#Age of child
age_child_0 = np.concatenate((agech0_a[d_childa[:,0]== 1],
	agech0_b[d_childb[:,0]== 1]),axis=0)
age_chi = np.zeros((age_child_0.shape[0],nperiods))

for x in range(0,nperiods):
	age_chi[:,x] = age_child_0 + x


boo_y = age_chi[:,2]<=6
boo_o = age_chi[:,2]>6

ltheta_a = np.log(choices['theta_matrix_a'])
ltheta_b = np.log(choices['theta_matrix_b'])

ltheta = np.concatenate((ltheta_a[d_childa[:,0]== 1,:,:],
	ltheta_b[d_childb[:,0]== 1,:,:]),axis=0)

passign_aux=np.concatenate((passign[d_childa[:,0]==1,0],
	passign[d_childb[:,0]== 1,0]),axis=0)

for j in range (M):
	for t in range(8):
		ltheta[:,t,j] = (ltheta[:,t,j])/np.std(ltheta[:,t,j],axis=0)

ate_ltheta_y = np.mean(np.mean(ltheta[(passign_aux==1) & (boo_y),:,:],axis=0) - np.mean(ltheta[(passign_aux==0) & (boo_y),:,:],axis=0),axis=1)
ate_ltheta_o = np.mean(np.mean(ltheta[(passign_aux==1) & (boo_o),:,:],axis=0) - np.mean(ltheta[(passign_aux==0) & (boo_o),:,:],axis=0),axis=1)
ate_ltheta = np.mean(np.mean(ltheta[(passign_aux==1) ,:,:],axis=0) - np.mean(ltheta[(passign_aux==0),:,:],axis=0),axis=1)

#Impact on SSRS t2 and t5
d30_t2_a = choices['ssrs_t2_matrix_a']>=4
d30_t2_b = choices['ssrs_t2_matrix_b']>=4

d30_t5_a = choices['ssrs_t2_matrix_a']>=4
d30_t5_b = choices['ssrs_t2_matrix_b']>=4

d30_t2 = np.concatenate((d30_t2_a[d_childa[:,0]== 1,:],
	d30_t2_b[d_childb[:,0]== 1,:]),axis=0)

d30_t5 = np.concatenate((d30_t5_a[d_childa[:,0]== 1,:],
	d30_t5_b[d_childb[:,0]== 1,:]),axis=0)

ate_d30_t2 = np.mean(np.mean(d30_t2[passign_aux==1,:],axis=0) - np.mean(d30_t2[passign_aux==0,:],axis=0))
ate_d30_t5 = np.mean(np.mean(d30_t5[passign_aux==1,:],axis=0) - np.mean(d30_t5[passign_aux==0,:],axis=0))

#Figure
nper = ate_ltheta.shape[0]
fig, ax=plt.subplots()
x = np.array(range(1,nper))
y_2 = ate_ltheta_y[1:]
plot2=ax.plot(x,y_2,'k-',label='Young',alpha=0.9)
plt.setp(plot2,linewidth=3)
#ax.annotate(r'$\Delta Pr($top 30%$)$=' + '{:04.2f}'.format(beta_t2[1]), xy=(2, y_2[1]), xytext=(2, y_2[1]+0.01),arrowprops=dict(facecolor='black', shrink=0.05),size = 15)
#ax.annotate(r'$\Delta Pr($top 30%$)$=' + '{:04.3f}'.format(beta_t5[1]), xy=(5, y_2[4]), xytext=(5, y_2[5]+0.02),arrowprops=dict(facecolor='black', shrink=0.05),size = 15)
ax.set_ylabel(r'Impact on academic achievement ($\sigma$s)', fontsize=20)
ax.set_xlabel(r'Years after random assignment ($t$)', fontsize=20)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
plt.yticks(fontsize=15)
plt.xticks(fontsize=15)
plt.show()
fig.savefig('/home/jrodriguez/NH_HC/results/Model/fit/ate_theta_young.pdf', format='pdf')
plt.close()

