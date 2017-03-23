/*
This do-file computes the prob of ranking SSRS>=4 using bootstrap
*/

clear
program drop _all
clear matrix
clear mata
set more off
set maxvar 15000
set matsize 2000


use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/sample_model_theta_v2.dta", clear
set seed 2828
local reps = 800

bootstrap, reps(`reps'): oprobit skills_t2 d_RA
mat betas_aux=e(b)
mat se_aux=e(se)
mat betas_t2=betas_aux[1,1]
mat ses_t2=se_aux[1,1]

bootstrap, reps(`reps'): oprobit skills_t5 d_RA
mat betas_aux=e(b)
mat se_aux=e(se)
mat beta_t5=betas_aux[1,1]
mat se_t5=se_aux[1,1]

preserve
clear
set obs 1
svmat betas_t2
outsheet using "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/beta_t2_obs.csv", comma replace
restore

preserve
clear
set obs 1
svmat ses_t2
outsheet using "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ses_beta_t2_obs.csv", comma replace
restore

preserve
clear
set obs 1
svmat beta_t5
outsheet using "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/beta_t5_obs.csv", comma replace
restore


preserve
clear
set obs 1
svmat se_t5
outsheet using "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ses_beta_t5_obs.csv", comma replace
restore


exit, STATA clear





