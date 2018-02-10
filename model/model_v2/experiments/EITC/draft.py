"""
execfile('draft.py')
"""
#the graph
fig, ax=plt.subplots()
plot1=ax.plot(p_list,target_moment_original,'b-o',label='Simulated w/ EITC',alpha=0.9)
plot1=ax.plot(p_list,target_moment_noeitc,'r-^',label='Simulated w/o EITC',alpha=0.9)
plot2=ax.plot(p_list,np.full((size_grid,),obs_moment),'b-.',label='Observed',alpha=0.9)
plt.setp(plot1,linewidth=3)
plt.setp(plot2,linewidth=3)
ax.legend()
ax.set_ylabel(r'$Pr($full-time employment$)$',fontsize=font_size)
ax.set_xlabel(r'Preference for full-time labor ($\alpha^f$)',fontsize=font_size)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
ax.legend(loc=0)
plt.show()
fig.savefig('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/EITC/alphaf_check_eitc.pdf', format='pdf')
plt.close()




