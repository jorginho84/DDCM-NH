#Simulated data
ssrs_t2 = choices['ssrs_t2_matrix']
ssrs_t5 = choices['ssrs_t5_matrix']

beta_t2 = []
beta_t5 = []
#Measures in t=2
for m in range(3): #across the three measures
	#simulated
	data_frame = pd.DataFrame({'sample'+str(i):ssrs_t2[:,m,i] for i in range(ssrs_t2.shape[2])})
	data_frame['RA'] = passign[:,0]
	data_frame.to_stata('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ssrs_sample.dta')

	#this do-file computes the array of oprobit estimates
	dofile = "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/fit/ssrs_sim.do"
	cmd = ["stata-mp", "do", dofile]
	subprocess.call(cmd)
	betas=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/beta_vector.csv').values
	beta_t2.append(np.mean(betas))

#Measures in t=5
data_frame = pd.DataFrame({'sample'+str(i):ssrs_t5[:,i] for i in range(ssrs_t2.shape[2])})
data_frame['RA'] = passign[:,0]
data_frame.to_stata('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ssrs_sample.dta')
#this do-file computes the array of oprobit estimates
dofile = "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/fit/ssrs_sim.do"
cmd = ["stata-mp", "do", dofile]
subprocess.call(cmd)
betas=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/beta_vector.csv').values
beta_t5.append(np.mean(betas))


#data: use only stata to bootstrap o_probit and get SE
dofile = "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/fit/ssrs_obs.do"
cmd = ["stata-mp", "do", dofile]
subprocess.call(cmd)
betas_t2_obs=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/beta_t2_obs.csv').values
ses_betas_t2_obs=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ses_beta_t2_obs.csv').values
betas_t5_obs=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/beta_t5_obs.csv').values
ses_betas_t5_obs=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ses_beta_t5_obs.csv').values



wb=openpyxl.load_workbook('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/fit.xlsx')
ws = wb["ssrs_data"]

pos = 0
for m in range(3):
	sim_moment = ws.cell('C'+str(pos + 5))
	obs_moment = ws.cell('D'+str(pos + 5))
	se_moment = ws.cell('D'+str(pos + 6))
	sim_moment.value = np.float(beta_t2[m])
	obs_moment.value = np.float(betas_t2_obs[m,0])
	se_moment.value = np.float(ses_betas_t2_obs[m,0])
	pos = pos + 2

sim_moment = ws.cell('F'+str(11))
obs_moment = ws.cell('G'+str(11))
se_moment = ws.cell('G'+str(12))
sim_moment.value = np.float(beta_t5[0])
obs_moment.value = np.float(betas_t5_obs[0])
se_moment.value = np.float(ses_betas_t5_obs[0])

wb.save('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/fit.xlsx')