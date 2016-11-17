/*
This do-file analyzes the take-up of the AFDC program
*/



global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results"


clear
clear matrix
clear mata
scalar drop _all
set more off
program drop _all
set maxvar 15000

*Reps in bootstrap
local reps = 1000

use "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model/sample_model_theta_v2.dta", clear

*Recovering AFDC eligibility parameters  (cutoff and benefits standards)
qui: do "$codes/income/afdc_param.do"

*Family size
gen nfam = 1 + nkids_baseline + married_y0

*AFDC eligibility at t=0
gen d_elig_afdc=0
forvalues nf=1/12{
	replace d_elig_afdc=1 if gross_nominal_y0<= cutoff_f`nf' & nfam==`nf'
}



*Recovering SNAP parameters
qui: do "$codes/income/snap_param.do"

*Snap eligibility at t=0
gen d_elig_snap=0
gen net_income = gross_nominal_y0 + afdc_y0 - std_deduction
forvalues nf=1/12{
	
	
	if `nf'<=8{
		replace d_elig_snap=1 if (net_income<= net_test_f`nf') & nfam==`nf'
		replace d_elig_snap=1 if gross_nominal_y0 <= gross_test_f`nf' & nfam==`nf'
	}
	else{
		replace d_elig_snap=1 if (net_income<= net_test_f8 + net_test_f9*`nf') & nfam==`nf'
		replace d_elig_snap=1 if (gross_nominal_y0<= gross_test_f8 + gross_test_f9*`nf') & nfam==`nf'
	}
	

}

***********************************************************
***********************************************************
***********************************************************
*AFDC takeup
sum d_elig_afdc
gen d_afdc=afdc_y0>0
sum d_afdc if d_elig_afdc==1
local mean_takeup=r(mean)

*SNAP takeup
sum d_elig_snap
gen d_fs=fs_y0>0
sum d_fs if d_elig_snap==1

*General eligibility and welfare takeup
*gen d_elig=d_elig_snap==1 | d_elig_afdc==1
*gen d_welfare=d_afdc==1 | d_fs==1

*sub-reporting and possible error in income gross income generator
sum d_afdc if d_elig_afdc==0
sum d_fs if d_elig_afdc==0

program boot_q, rclass
	version 13
	args income d_afdc quintile 
	tempname q_var mean_out
	xtile `q_var'=`income', nq(5)
	sum `d_afdc' if `q_var'==`quintile'
	scalar `mean_out'=r(mean)
	return scalar mean_q = `mean_out'
end

****************************************************************************************************	
****************************************************************************************************
****************************************************************************************************
/*Computing afdc take up across household size */

forvalues x=2/6{
	preserve
	keep if d_elig_afdc==1 & nfam==`x'
		
	forvalues q=1/5{
		qui: bootstrap mean_out=r(mean_q), reps(`reps'): boot_q gross_nominal_y0 d_afdc `q'
		mat b_aux=e(b)
		local mean_nfam`x'_q`q'=b_aux[1,1]
		mat s_aux=e(ci_normal)
		local lb_nfam`x'_`q'=s_aux[1,1]
		local ub_nfam`x'_`q'=s_aux[2,1]
	
	}
	
	
	
	
	
	
	restore

}




forvalues x=2/6{
	preserve
	clear
	set obs 5 /*5 quintiles*/
	gen quintile=.
	gen takeup=.
	gen lb=.
	gen ub=.
	local obs=1
	forvalues q=1/5{
		replace takeup=`mean_nfam`x'_q`q'' if _n==`obs'
		replace lb=`lb_nfam`x'_`q'' if _n==`obs'
		replace ub=`ub_nfam`x'_`q'' if _n==`obs'
		replace quintile = `q' if _n==`obs'
		local obs=`obs'+1
	
	}
	
	
	
	
	*New identifier
	gen quintile2=quintile*2
	
	twoway (bar takeup quintile2) (rcap ub lb quintile2), /* These are the mean effect and the 90% confidence interval
	*/ ytitle("AFDC take-up")  xtitle("Quintiles of gross income") legend(off) /*
	*/ xlabel( 2 "1" 4 "2" 6 "3" 8 "4" 10 "5", noticks) /*
	*/ graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white))  /*
	*/ scheme(s2mono) ylabel(, nogrid)
	
	graph export "$results/Income/afdc_takeup_nfam`x'.pdf", as(pdf) replace
	restore

}


****************************************************************************************************	
****************************************************************************************************
****************************************************************************************************
/*Computing afdc take up for all household sizes*/

preserve
keep if d_elig_afdc==1
forvalues q=1/5{
	qui: bootstrap mean_out=r(mean_q), reps(`reps'): boot_q gross_nominal_y0 d_afdc `q'
	mat b_aux=e(b)
	local mean_q`q'=b_aux[1,1]
	mat s_aux=e(ci_normal)
	local lb_`q'=s_aux[1,1]
	local ub_`q'=s_aux[2,1]
	
	}
clear
set obs 5 /*5 quintiles*/
gen quintile=.
gen takeup=.
gen lb=.
gen ub=.
local obs=1
forvalues q=1/5{
	replace takeup=`mean_q`q'' if _n==`obs'
	replace lb=`lb_`q'' if _n==`obs'
	replace ub=`ub_`q'' if _n==`obs'
	replace quintile = `q' if _n==`obs'
	local obs=`obs'+1
	
	}
	
	
	
	
*New identifier
gen quintile2=quintile*2
	
twoway (bar takeup quintile2) (rcap ub lb quintile2), /* These are the mean effect and the 90% confidence interval
*/ ytitle("AFDC take-up")  xtitle("Quintiles of gross income") legend(off) /*
*/ xlabel( 2 "1" 4 "2" 6 "3" 8 "4" 10 "5", noticks) /*
*/ graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white))  /*
*/ scheme(s2mono) ylabel(, nogrid)
	
graph export "$results/Income/afdc_takeup_overall.pdf", as(pdf) replace
restore

****************************************************************************************************	
****************************************************************************************************
****************************************************************************************************
/*Computing SNAP take up across household size */


preserve
keep if d_elig_snap==1
forvalues q=1/5{
	qui: bootstrap mean_out=r(mean_q), reps(`reps'): boot_q gross_nominal_y0 d_fs `q'
	mat b_aux=e(b)
	local mean_q`q'=b_aux[1,1]
	mat s_aux=e(ci_normal)
	local lb_`q'=s_aux[1,1]
	local ub_`q'=s_aux[2,1]
	
	}
clear
set obs 5 /*5 quintiles*/
gen quintile=.
gen takeup=.
gen lb=.
gen ub=.
local obs=1
forvalues q=1/5{
	replace takeup=`mean_q`q'' if _n==`obs'
	replace lb=`lb_`q'' if _n==`obs'
	replace ub=`ub_`q'' if _n==`obs'
	replace quintile = `q' if _n==`obs'
	local obs=`obs'+1
	
	}
	
	
	
	
*New identifier
gen quintile2=quintile*2
	
twoway (bar takeup quintile2) (rcap ub lb quintile2), /* These are the mean effect and the 90% confidence interval
*/ ytitle("SNAP take-up")  xtitle("Quintiles of gross income") legend(off) /*
*/ xlabel( 2 "1" 4 "2" 6 "3" 8 "4" 10 "5", noticks) /*
*/ graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white))  /*
*/ scheme(s2mono) ylabel(, nogrid)
	
graph export "$results/Income/snap_takeup_overall.pdf", as(pdf) replace
restore
