/*
This code computes the variance-covariance matrix of the auxiliary parameters
the output is a KxK matrix, where K is the number of aux moments.

Note: The weighting matrix for II estimation uses only the diagonal of this matrix.
To compute the structural parameters' standard errors, I use the whole var-cov matrix

I compute moments calling these do files:
utility_aux.do
wage_process.do
measurement system.do
production function.do

each do-file returns an array of aux estimates.

*/

clear
program drop _all
clear matrix
clear mata
set more off
set maxvar 15000

global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/aux_model" /*this is where I compute aux moments*/

set seed 2828
local draws = 1000


program betas, rclass
	version 13
	args num_mom
	preserve
	qui: do "$codes/utility_aux_2.do"
	restore
	preserve
	qui: do "$codes/wage_p_2.do"
	restore
	preserve
	qui: do "$codes/theta_aux_2.do"
	restore

	mat betas= beta_utility\beta_wage\betas_theta
	forvalues x=1/`num_mom'{
		return scalar mom`x' = betas[`x',1]
	}
end

use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/sample_model_v2.dta", clear

bootstrap /*
*/ mom1=r(mom1) /*
*/ mom2=r(mom2) /*
*/ mom3=r(mom3) /*
*/ mom4=r(mom4) /*
*/ mom5=r(mom5) /*
*/ mom6=r(mom6) /*
*/ mom7=r(mom7) /*
*/ mom8=r(mom8) /*
*/ mom9=r(mom9) /*
*/ mom10=r(mom10) /*
*/ mom11=r(mom11) /*
*/ mom12=r(mom12) /*
*/ mom13=r(mom13) /*
*/ mom14=r(mom14) /*
*/ mom15=r(mom15) /*
*/ mom16=r(mom16) /*
*/ mom17=r(mom17) /*
*/ mom18=r(mom18) /*
*/ mom19=r(mom19) /*
*/ mom20=r(mom20) /*
*/ mom21=r(mom21) /*
*/ mom22=r(mom22) /*
*/, cluster(sampleid) idcluster(newid) reps(`draws'): betas 22



mat betas_orig = e(b)
mat var_cov = e(V)

preserve
svmat var_cov
keep var_cov*
drop if var_cov1==.
outsheet using "$results/aux_model/var_cov_2.csv", comma  replace

restore

