"""
exec(open('/home/jrodriguez/NH_HC/codes/model_v2/fit/draft.py').read())
"""
#Figure
fig, ax=plt.subplots()
x = np.array([1,3])
sim = [beta_t2[1],beta_t5[1]] #simulated
obs = [betas_t2_obs[1][0,0],betas_t5_obs[1][0,0]] #observed
ses = [ses_betas_t2_obs[1][0,0],ses_betas_t5_obs[1][0,0]] #save SEs here
ses_sim = [np.std(ates_2,axis=0),np.std(ates_5,axis=0)]
plot0 = ax.plot([0,1,2,3,4],[0,0,0,0,0],color = 'k',linestyle='--',linewidth=1)
plot1 = ax.bar(x,sim,color='b' ,alpha=.65,label='Simulated')
plot2 = ax.bar(x+0.5,obs,label='Data',alpha=0.9)
plot3 = ax.errorbar(x,sim,yerr=ses_sim,fmt='ko',ecolor='k',capsize=5,capthick=1,alpha=0.9)
plot4 = ax.errorbar(x+0.5,obs,yerr=ses,fmt='ko',ecolor='k',capsize=5,capthick=1,alpha=0.9)
plot3[-1][0].set_linestyle('--')
plot4[-1][0].set_linestyle('--')
ax.legend(fontsize=15)
ax.set_xticks([1.25, 3.25])
ax.set_xticklabels(['2','5'])
ax.set_xlim(0,4)
ax.set_ylabel(r'Impact on SSRS measure ($\sigma$s)', fontsize=15)
ax.set_xlabel(r'Years after random assignment ($t$)', fontsize=15)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
plt.yticks(fontsize=12)
plt.xticks(fontsize=12)
plt.show()
fig.savefig('/home/jrodriguez/NH_HC/results/model_v2/fit/ate_theta_validation.pdf', format='pdf')
plt.close()