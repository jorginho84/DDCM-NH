/*
This do-file analyzes the take-up of the AFDC program
*/



global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Model"


clear
clear matrix
clear mata
scalar drop _all
set more off
set maxvar 15000

use "$results/sample_model_theta_v2.dta", clear

*Recovering AFDC eligibility parameters  (cutoff and benefits standards)
qui: do "$codes/income/afdc_param.do"

*Family size
gen nfam = 1 + nkids_baseline + married_y0

*AFDC eligibility
gen d_elig_afdc=0
forvalues nf=1/12{
	replace d_elig_afdc=1 if gross_nominal_y0<= cutoff_f`nf' & nfam==`nf'
}



*Recovering SNAP parameters
qui: do "$codes/income/snap_param.do"

*Snap eligibility
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

*SNAP takeup
sum d_elig_snap
gen d_fs=fs_y0>0
sum d_fs if d_elig_snap==1




