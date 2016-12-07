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


use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/ssrs_sample.dta", clear

mat betas = J(1000,1,.)

forvalues x=0/999{
	preserve
	keep RA sample`x'
	qui: oprobit sample`x' RA
	mat betas_aux = e(b)
	mat betas[`x'+1,1] = betas_aux[1,1]
	restore	

}


clear
set obs 1000
svmat betas
outsheet using "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/beta_vector.csv", comma replace


exit, STATA clear
