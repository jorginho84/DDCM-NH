#Computing mfx
theta_th = np.zeros((N,nperiods)) #shocked
theta_0 = np.zeros((N,nperiods))
theta_0[:,0] = np.mean(theta_matrix[:,0,:],axis=1) #initial value
theta_th[:,0] = theta_0[:,0].copy()

#SD units
sd_matrix = np.zeros((nperiods,M))
for k in range(nperiods):
	for j in range(M):
		sd_matrix[k,j] = np.std(np.log(theta_matrix[:,k,j]),axis=0)
sds = np.mean(sd_matrix,axis=1)

#the shocks
shock_th = theta_0[:,0] + np.exp(np.zeros(N)+0.3)

#theta with no shocks
for k in range(nperiods - 1):
	#no shocks
	theta_0[:,k+1] = np.exp(gamma1*np.log(theta_0[:,k]) + gamma2*np.log(ec) +gamma3*np.log(lt))

#Responses
for k in range(nperiods - 1):
	if k==0:
		theta_th[:,k+1] = np.exp(gamma1*np.log(shock_th) + gamma2*np.log(ec) +gamma3*np.log(lt))
	else:
		theta_th[:,k+1] = np.exp(gamma1*np.log(theta_th[:,k]) + gamma2*np.log(ec) +gamma3*np.log(lt))
#ATE
ate_theta = np.mean(np.log(theta_th) - np.log(theta_0),axis=0)/sds

#mfx: a 1,000 income shock
t0 = gamma1*np.log(np.ones(N)) + gamma2*np.log(ec) +gamma3*np.log(lt)
t1 = gamma1*np.log(np.ones(N)) + gamma2*np.log(ec+1000/(nkids0[:,0] + married0[:,0])) +gamma3*np.log(lt)
mfx_c = np.mean(t1-t0)/sds[1]

#mfx: from full time to unemployment
t0 = gamma1*np.log(np.ones(N)) + gamma2*np.log(ec) +gamma3*np.log(lt)
t1 = gamma1*np.log(np.ones(N)) + gamma2*np.log(ec) +gamma3*np.log((lt+40))
mfx_t = np.mean(t1-t0)/sds[1]

print ''
print 'impact of 1,000 shock', mfx_c
print ''
print 'impact of unemployment shock', mfx_t


##The graph (shock on theta)
x = np.array(range(0,nperiods))
fig, ax=plt.subplots()
ax.plot(x,ate_theta, color='k',zorder=1,linewidth=3)
ax.set_ylabel(r'Impact on $\ln(\theta_{t+1})$ (in $\sigma$s)', fontsize=14)
ax.set_xlabel(r'Years after random assignment ($t$)', fontsize=14)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
plt.show()
fig.savefig('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/prod/theta_shock.pdf', format='pdf')
plt.close()


