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
mat betas_young = J(1000,1,.)
mat betas_old = J(1000,1,.)

forvalues x=0/999{
	preserve
	keep RA sample`x' young
	qui: oprobit sample`x' RA
	qui: predict xbetas, xb
	gen xbetas_tilde = xbetas - _b[RA]*RA
	gen pr_1 = 1-normal(_b[/cut3]- (xbetas_tilde + _b[RA]))
	gen pr_0 = 1-normal(_b[/cut3]- (xbetas_tilde))
	gen dpr = pr_1 - pr_0
	qui: sum dpr
	mat betas_aux=r(mean) 
	mat betas[`x'+1,1] = betas_aux[1,1]
	drop xbetas xbetas_tilde pr_1 pr_0 dpr
	
	qui: oprobit sample`x' RA if young==1
	qui: predict xbetas, xb
	gen xbetas_tilde = xbetas - _b[RA]*RA
	gen pr_1 = 1-normal(_b[/cut3]- (xbetas_tilde + _b[RA]))
	gen pr_0 = 1-normal(_b[/cut3]- (xbetas_tilde))
	gen dpr = pr_1 - pr_0
	qui: sum dpr
	mat betas_aux_y = r(mean)
	mat betas_young[`x'+1,1] = betas_aux_y[1,1]
	drop xbetas xbetas_tilde pr_1 pr_0 dpr
	
	qui: oprobit sample`x' RA if young==0
	qui: predict xbetas, xb
	gen xbetas_tilde = xbetas - _b[RA]*RA
	gen pr_1 = 1-normal(_b[/cut3]- (xbetas_tilde + _b[RA]))
	gen pr_0 = 1-normal(_b[/cut3]- (xbetas_tilde))
	gen dpr = pr_1 - pr_0
	qui: sum dpr
	mat betas_aux_o = r(mean)
	mat betas_old[`x'+1,1] = betas_aux_o[1,1]
	drop xbetas xbetas_tilde pr_1 pr_0 dpr
	restore	

}


clear
set obs 1000
svmat betas
svmat betas_young
svmat betas_old

foreach beta of varlist betas1 betas_young1 betas_old1{
	preserve
	keep `beta'
	outsheet using "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/fit/`beta'_vector.csv", comma replace
	restore
}



exit, STATA clear



