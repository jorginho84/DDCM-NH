"""
execfile('draft.py')
"""
#Effects on ln theta figure
fig, ax=plt.subplots()
for k in range(len(tfp_list)):
	ax.plot(x,ate_theta_list[k][1:],markers_list[k],label=names_list_v2[k],linewidth=3,markersize=9,alpha=0.9)
ax.set_ylabel(r'Impact on child human capital ($\sigma$s)', fontsize=15)
ax.set_xlabel(r'Years after random assignment ($t$)', fontsize=15)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
plt.yticks(fontsize=15)
plt.xticks(fontsize=15)
ax.legend(fontsize = 15)
plt.show()
fig.savefig('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/experiments/cc_quality/ate_theta_CC_quality.pdf', format='pdf')
plt.close()



