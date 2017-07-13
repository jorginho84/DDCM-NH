betas_nelder=np.load('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/betas_modelv9_v1_e3.npy')


#Utility function
eta=betas_nelder[0]
alphap=betas_nelder[1]
alphaf=betas_nelder[2]
alpha_cc=betas_nelder[3]
alpha_home_hf=betas_nelder[4]


#wage process
wagep_betas=np.array([betas_nelder[5],betas_nelder[6],betas_nelder[7],
	betas_nelder[8],betas_nelder[9],betas_nelder[10],betas_nelder[11]]).reshape((7,1))


#Production function [young,old]
gamma1= betas_nelder[12]
gamma2= betas_nelder[13]
gamma3= betas_nelder[14]
tfp=betas_nelder[15]
sigmatheta=0

#Measurement system: three measures for t=2, one for t=5
kappas=[[betas_nelder[16],betas_nelder[17],betas_nelder[18],betas_nelder[19]],
[betas_nelder[20],betas_nelder[21],betas_nelder[22],betas_nelder[23]]]
#First measure is normalized. starting arbitrary values
#All factor loadings are normalized
lambdas=[1,1]



#Weibull distribution of cc prices
scalew=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/scale.csv').values
shapew=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/shape.csv').values
q=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/aux_model/q_prob.csv').values


#Probability of afdc takeup
pafdc=.60

#Probability of snap takeup
psnap=.70

#Data
#X_aux=pd.read_csv('C:\\Users\\Jorge\\Dropbox\\Chicago\\Research\\Human capital and the household\\results\\Model\\Xs.csv')
X_aux=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/sample_model_v2.csv')
x_df=X_aux

#Sample size 
N=X_aux.shape[0]

#Data for wage process
#see wage_process.do to see the order of the variables.
x_w=x_df[ ['age_ra', 'd_HS2', 'constant' ] ].values


#Data for marriage process
#Parameters: marriage. Last one is the constant
x_m=x_df[ ['age_ra', 'constant']   ].values
marriagep_betas=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/marriage_process/betas_m_v2.csv').values

#Data for fertility process (only at X0)
#Parameters: kids. last one is the constant
x_k=x_df[ ['age_ra', 'age_ra2', 'constant']   ].values
kidsp_betas=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/kids_process/betas_kids_v2.csv').values


#Minimum set of x's (for interpolation)
x_wmk=x_df[  ['age_ra', 'age_ra2', 'd_HS2', 'age_t0','age_t02','constant'] ].values

#Data for treatment status
passign=x_df[ ['d_RA']   ].values

#The EITC parameters
eitc_list = pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/eitc_list.p', 'rb' ) )

#The AFDC parameters
afdc_list = pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/afdc_list.p', 'rb' ) )

#The SNAP parameters
snap_list = pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/snap_list.p', 'rb' ) )

#CPI index
cpi =  pickle.load( open( '/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/cpi.p', 'rb' ) )

#Here: the estimates from the auxiliary model
###
###

#Assuming random start
#theta0=np.exp(np.random.randn(N))

#number of kids at baseline
nkids0=x_df[ ['nkids_baseline']   ].values

#marital status at baseline
married0=x_df[ ['d_marital_2']   ].values

#age of child at baseline
agech0=x_df[['age_t0']].values

#Defines the instance with parameters
param0=util.Parameters(alphap, alphaf, eta, alpha_cc,alpha_home_hf,gamma1,gamma2,
	gamma3, tfp, sigmatheta,wagep_betas, marriagep_betas, kidsp_betas, 
	eitc_list,afdc_list,snap_list,cpi,q,scalew,shapew,lambdas,kappas,pafdc,psnap)

