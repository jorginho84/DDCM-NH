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


use "/home/jrodriguez/NH_HC/results/model_v2/fit/ssrs_sample.dta", clear

mat betas = J(1000,1,.)
mat betas_young = J(1000,1,.)
mat betas_old = J(1000,1,.)

forvalues x=0/999{
	
	qui: reg ssrs`x' RA
	mat betas[`x'+1,1] = _b[RA]
	
	qui: reg ssrs`x' RA if young==1
	mat betas_young[`x'+1,1] = _b[RA]

	qui: reg ssrs`x' RA if young==0
	mat betas_old[`x'+1,1] = _b[RA]

}


clear
set obs 1000
svmat betas
svmat betas_young
svmat betas_old

foreach beta of varlist betas1 betas_young1 betas_old1{
	preserve
	keep `beta'
	outsheet using "/home/jrodriguez/NH_HC/results/model_v2/fit/`beta'_vector.csv", comma replace
	restore
}



exit, STATA clear



