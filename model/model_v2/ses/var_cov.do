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


use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/sample_model_v2.dta", clear
qui: save "$results/data_aux.dta", replace
qui: do "$codes/utility_aux.do"
qui: do "$codes/wage_p.do"
qui: do "$codes/theta_aux.do"
mat betas_orig=beta_utility\beta_wage\betas_theta
svmat betas_orig
preserve
keep betas_orig1
drop if betas_orig1==.
outsheet using "$results/aux_model/moments_vector.csv", comma  replace
restore

set seed 2828
local draws = 500
local n_moments = 22

forvalues x = 1/`draws'{
	use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/sample_model_v2.dta", clear
	bsample
	qui: save "$results/data_aux.dta", replace
	qui: do "$codes/utility_aux.do"
	qui: do "$codes/wage_p.do"
	qui: do "$codes/theta_aux.do"
	mat betas=beta_utility\beta_wage\betas_theta
	svmat betas
	keep betas1
	rename betas1 betas
	drop if betas==.
	egen par = seq()
	gen draw = `x'
	qui: reshape wide betas, i(draw) j(par)
	tempfile data_`x'
	qui: save `data_`x'', replace
	
}


*This generates a dataset of aux estimates for each draw
use `data_1'
forvalues x=2/`draws'{
	append using `data_`x''

}

*This is the sim moments matrix
sum betas1
matrix beta_matrix =r(mean)
forvalues x=2/`n_moments'{
	sum betas`x'
	matrix beta_matrix = beta_matrix\r(mean)
	

}

*This is the cov matrix
qui: corr betas*, cov
mat var_cov = r(C)
preserve
drop draw betas*
svmat var_cov
outsheet using "$results/aux_model/var_cov.csv", comma  replace
restore
