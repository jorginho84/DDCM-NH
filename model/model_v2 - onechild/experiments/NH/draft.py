"""
exec(open("/home/jrodriguez/NH_HC/codes/model_v2/experiments/NH/draft.py").read())

"""
#for period t=2
#Mechanisms Figures #2: accumulated controbutions
names_list_v2 = ['Wage sub', 'Child care sub','Wage sub + Child care sub']
markers_list = ['k-','k--','k-o' ]
facecolor_list = ['k','k','k' ]
y_list = []
y_list.append(np.mean(ates_list[0]['Theta'],axis=1))
y_list.append(np.mean(ates_list[3]['Theta'],axis=1))
y_list.append(np.mean(ates_list[1]['Theta'],axis=1))

x = np.array(range(1,nperiods))
fig, ax=plt.subplots()
for k in range(len(y_list)):
	ax.plot(x,y_list[k],markers_list[k],markerfacecolor= facecolor_list[k],
		markeredgewidth=1.0,label=names_list_v2[k],linewidth=3,markersize=11,alpha=0.9)
ax.set_ylabel(r'Impact on child human capital ($\sigma$s)', fontsize=12)
ax.set_xlabel(r'Years after random assignment ($t$)', fontsize=12)
ax.set_ylim(0,0.3)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
plt.yticks(fontsize=11)
plt.xticks(fontsize=11)
ax.legend(loc=0,fontsize = 11)
plt.show()
fig.savefig('/home/jrodriguez/NH_HC/results/model_v2/experiments/NH/ate_theta_policies_1.pdf', format='pdf')
plt.close()


#Figure: ATE on theta of wage sub vs cc sub/ work requirements
names_list_v2 = ['Wage sub + Work req', 'Child care sub + Work req','Full treatment']
markers_list = ['k-','k--','k-o' ]
facecolor_list = ['k','k','k' ]
y_list = []
y_list.append(np.mean(ates_list[2]['Theta'],axis=1))
y_list.append(np.mean(ates_list[4]['Theta'],axis=1))
y_list.append(np.mean(ates_list[5]['Theta'],axis=1))

x = np.array(range(1,nperiods))
fig, ax=plt.subplots()
for k in range(len(y_list)):
	ax.plot(x,y_list[k],markers_list[k],markerfacecolor= facecolor_list[k],
		markeredgewidth=1.0,label=names_list_v2[k],linewidth=3,markersize=11,alpha=0.9)
ax.set_ylabel(r'Impact on child human capital ($\sigma$s)', fontsize=12)
ax.set_xlabel(r'Years after random assignment ($t$)', fontsize=12)
ax.set_ylim(0,0.3)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
plt.yticks(fontsize=11)
plt.xticks(fontsize=11)
ax.legend(loc=0,fontsize = 11)
plt.show()
fig.savefig('/home/jrodriguez/NH_HC/results/model_v2/experiments/NH/ate_theta_policies_2.pdf', format='pdf')
plt.close()
