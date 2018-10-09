
"""
exec(open("C:\\Users\\jrodriguezo\\Dropbox\\Chicago\\Research\\Human capital and the household\\codes\\DDCM-NH\\model\\model_v2\\experiments\\NH\\draft.py").read())
"""

#Mechanisms figures
for j in range(len(models_list)):
	x = np.array(range(1,nperiods))
	y1 = np.mean(contribution_list[j]['Theta'],axis=1)
	y2 = np.mean(contribution_list[j]['Time'],axis=1)
	y3 = np.mean(contribution_list[j]['CC'],axis=1)
	y4 = np.mean(contribution_list[j]['Money'],axis=1)
	total = y1 + y2 + y3 + y4
	horiz_line_data = np.array([0 for i in range(len(x))])
	fig, ax=plt.subplots()
	ax.plot(x,y2, color='k',zorder=1,linewidth=4.5,label='Time')
	ax.plot(x,horiz_line_data, 'k--',linewidth=2)
	ax.fill_between(x,y2,(y2+y1), color='k' ,alpha=.65,zorder=2,label='Lagged human capital')
	ax.fill_between(x,(y2+y1),(y2+y1+y3), color='k' ,alpha=.35,zorder=3,label='Child care')
	ax.fill_between(x,(y2+y1+y3),(total), color='k' ,alpha=.12,zorder=4,label='Money')
	ax.set_ylabel(r'Effect on child human capital ($\sigma$s)', fontsize=14)
	ax.set_xlabel(r'Years after random assignment ($t$)', fontsize=14)
	#ax.annotate('Explained by time', xy=(2, y2[2]), xytext=(2.5, y2[2]-0.02),
	#	arrowprops=dict(facecolor='black', shrink=0.05,connectionstyle="arc3"))
	#ax.annotate('Explained by consumption', xy=(3, total[2]-0.01), xytext=(2, total[2]+0.02),
	#	arrowprops=dict(facecolor='black', shrink=0.05,connectionstyle="arc3"))
	
	#ax.annotate('Explained by child care', xy=(2.2, y1[1]+0.04), xytext=(3, y1[1]+0.02),
	#	arrowprops=dict(facecolor='black', shrink=0.05,connectionstyle="arc3"))
	#ax.text(4,0.05,'Explained by lagged human capital')
	ax.spines['right'].set_visible(False)
	ax.spines['top'].set_visible(False)
	ax.yaxis.set_ticks_position('left')
	ax.xaxis.set_ticks_position('bottom')
	ax.margins(0, 0)
	#ax.set_ylim(y_limit_lower[0] - 0.02,y_limit_upper[3] + 0.02)
	ax.legend(loc=5,fontsize=19)
	plt.yticks(fontsize=11)
	plt.xticks(fontsize=11)
	#ax.legend(['Time', 'Lagged human capital','Child care','Consumption'],loc=5)
	plt.show()
	fig.savefig('C:\\Users\\jrodriguezo\\Dropbox\\Chicago\\Research\\Human capital and the household\\lizzie_backup\\results\\Model\\experiments\\NH\\mech_' + models_names[j]+'.pdf', format='pdf')
	plt.close()
