#Simulated data
ssrs_t2 = choices['ssrs_t2_matrix']
ssrs_t5 = choices['ssrs_t5_matrix']

#overall, young, old
beta_t2 = []
beta_t5 = []

betas_t2_obs = []
betas_t5_obs = []
ses_betas_t2_obs = []
ses_betas_t5_obs = []

#Measures in t=2
age_t2 = agech0 + 2

boo_age = age_t2<=6

#Dummy sample young/old

#simulated
data_frame = pd.DataFrame({'sample'+str(i):ssrs_t2[:,i] for i in range(ssrs_t2.shape[1])})
data_frame['RA'] = passign[:,0]
data_frame['young'] = boo_age[:,0] + 0
data_frame.to_stata('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ssrs_sample.dta')
#this do-file computes the array of oprobit estimates
dofile = "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/fit/ssrs_sim.do"
cmd = ["stata-mp", "qui: do", dofile]
subprocess.call(cmd)
betas=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/betas1_vector.csv').values
betas_young=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/betas_young1_vector.csv').values
betas_old=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/betas_old1_vector.csv').values
beta_t2.append(np.mean(betas))
beta_t2.append(np.mean(betas_young))
beta_t2.append(np.mean(betas_old))

#Measures in t=5
data_frame = pd.DataFrame({'sample'+str(i):ssrs_t5[:,i] for i in range(ssrs_t2.shape[1])})
data_frame['RA'] = passign[:,0]
data_frame['young'] = boo_age[:,0] + 0
data_frame.to_stata('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ssrs_sample.dta')
#this do-file computes the array of oprobit estimates
dofile = "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/fit/ssrs_sim.do"
cmd = ["stata-mp", "qui: do", dofile]
subprocess.call(cmd)
betas=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/betas1_vector.csv').values
betas_young=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/betas_young1_vector.csv').values
betas_old=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/betas_old1_vector.csv').values
beta_t5.append(np.mean(betas))
beta_t5.append(np.mean(betas_young))
beta_t5.append(np.mean(betas_old))


#data: use only stata to bootstrap o_probit and get SE
dofile = "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/fit/ssrs_obs.do"
cmd = ["stata-mp", "qui: do", dofile]
subprocess.call(cmd)
betas_t2_obs.append(pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/beta_t2_obs.csv').values)
betas_t2_obs.append(pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/beta_t2_y_obs.csv').values)
betas_t2_obs.append(pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/beta_t2_o_obs.csv').values)

ses_betas_t2_obs.append(pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ses_beta_t2_obs.csv').values)
ses_betas_t2_obs.append(pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ses_beta_t2_y_obs.csv').values)
ses_betas_t2_obs.append(pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ses_beta_t2_o_obs.csv').values)


betas_t5_obs.append(pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/beta_t5_obs.csv').values)
betas_t5_obs.append(pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/beta_t5_y_obs.csv').values)
betas_t5_obs.append(pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/beta_t5_o_obs.csv').values)

ses_betas_t5_obs.append(pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ses_beta_t5_obs.csv').values)
ses_betas_t5_obs.append(pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ses_beta_t5_y_obs.csv').values)
ses_betas_t5_obs.append(pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ses_beta_t5_o_obs.csv').values)

##The table (.tex)
var_list = ['SSRS (overall)','SSRS (young)','SSRS (old)']

with open('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ssrs_validation.tex','w') as f:
	f.write(r'\begin{tabular}{lcccc}'+'\n')
	f.write(r'\hline'+'\n')
	f.write(r'&& Simulated && Data \bigstrut\\'+'\n')
	f.write(r'\cline{1-1}\cline{3-5}'+'\n')
	f.write(r'A. $t=2$ &&&&  \bigstrut[t]\\'+'\n')
	for i in range(3):
		f.write(var_list[i] +  '&&'+  '{:04.3f}'.format(beta_t2[i]) + '&&'+'{:04.3f}'.format(betas_t2_obs[i][0,0]) + '\\'+'\n')
		f.write(r' &&   &&'+ '{:04.3f}'.format(ses_betas_t2_obs[i][0,0]) + '\\'+'\n')
	f.write(r'B. $t=5$ &&&&  \bigstrut[t]\\'+'\n')
	for i in range(3):
		f.write(var_list[i] +  '&&'+  '{:04.3f}'.format(beta_t5[i]) + '&&'+'{:04.3f}'.format(betas_t5_obs[i][0,0]) + '\\'+'\n')
		f.write(r' &&   &&'+ '{:04.3f}'.format(ses_betas_t5_obs[i][0,0]) + '\\'+'\n')

	f.write(r'\hline'+'\n')
	f.write(r'\end{tabular}'+'\n')





#old excel table
wb=openpyxl.load_workbook('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/fit.xlsx')
ws = wb["ssrs_data"]

sim_moment = ws.cell('C'+str(5))
obs_moment = ws.cell('D'+str(5))
se_moment = ws.cell('D'+str(6))
sim_moment.value = np.float(beta_t2[0])
obs_moment.value = np.float(betas_t2_obs[0])
se_moment.value = np.float(ses_betas_t2_obs[0])

sim_moment = ws.cell('C'+str(7))
obs_moment = ws.cell('D'+str(7))
se_moment = ws.cell('D'+str(8))
sim_moment.value = np.float(beta_t5[0])
obs_moment.value = np.float(betas_t5_obs[0])
se_moment.value = np.float(ses_betas_t5_obs[0])

wb.save('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/fit.xlsx')