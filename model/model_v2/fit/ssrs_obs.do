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

gen age_t2 = age_t0 + 2


foreach x in 2 5{
	bootstrap, reps(`reps'): oprobit skills_t`x' d_RA
	mat betas_aux_`x'=e(b)
	mat se_aux_`x'=e(se)
	mat betas_t`x'=betas_aux_`x'[1,1]
	mat ses_t`x'=se_aux_`x'[1,1]

	bootstrap, reps(`reps'): oprobit skills_t`x' d_RA if age_t2<=6
	mat betas_aux_`x'_y=e(b)
	mat se_aux_`x'_y=e(se)
	mat betas_t`x'_y=betas_aux_`x'_y[1,1]
	mat ses_t`x'_y=se_aux_`x'_y[1,1]

	bootstrap, reps(`reps'): oprobit skills_t`x' d_RA if age_t2>6
	mat betas_aux_`x'_o=e(b)
	mat se_aux_`x'_o=e(se)
	mat betas_t`x'_o=betas_aux_`x'_o[1,1]
	mat ses_t`x'_o=se_aux_`x'_o[1,1]

}



foreach x in 2 5{
	
	preserve
	clear
	set obs 1
	svmat betas_t`x'
	outsheet using "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/beta_t`x'_obs.csv", comma replace
	restore

	preserve
	clear
	set obs 1
	svmat betas_t`x'_y
	outsheet using "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/beta_t`x'_y_obs.csv", comma replace
	restore


	preserve
	clear
	set obs 1
	svmat betas_t`x'_o
	outsheet using "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/beta_t`x'_o_obs.csv", comma replace
	restore

	preserve
	clear
	set obs 1
	svmat ses_t`x'
	outsheet using "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ses_beta_t`x'_obs.csv", comma replace
	restore

	preserve
	clear
	set obs 1
	svmat ses_t`x'_y
	outsheet using "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ses_beta_t`x'_y_obs.csv", comma replace
	restore

	preserve
	clear
	set obs 1
	svmat ses_t`x'_o
	outsheet using "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ses_beta_t`x'_o_obs.csv", comma replace
	restore


}



exit, STATA clear





