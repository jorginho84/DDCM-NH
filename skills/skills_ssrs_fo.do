/*
This do-file produces a figure showing the impact of the program by survey and gender.
Uses the overall SSRS measure.

Let

SSRS_t=\alpha_t+\beta_t*RA+epsilon_it

Performs bootstrap to generate a series of {beta_t} for t=2,5,8 years after RA

*/



global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results"

/*
robust SE for small samples. Set to hc3 for more conservatives. 

See Angrist and Pischke for more information
"robust" SE can be misleading when the sample size is small and there is no much heteroskedasticity.
*/
local SE="hc2"

/*
controls: choose if regression should include controls for parents: age, ethnicity, marital status, and education.
*/

local controls=1


/*
Estimation:
OLS: choose 0 if regression should be an ordered probit. 1 otherwise
*/

local OLS=0

clear
clear matrix
scalar drop _all
clear mata
set seed 100
set maxvar 15000
program drop _all
set more off


*******************************************************
/*Computing estimates*/
*******************************************************

use "$databases/Youth_original2.dta", clear

*labels
do "$codes/data_youth.do"
keep  sampleid child p_assign zboy agechild /*
*/ tq17a t2q17a etsq13a /*year 2, 5, and 8, respectively*/

destring sampleid, force replace
***************************************************************************
/*The X's*/if `controls'==1{

do "$codes/skills/Xs.do"


}

*****************************************************************
*destring tcs* tacad zboy, force replace
*Only children who were preschoolers when they were in New Hope

*keep if agechild<=7

gen RA=1 if p_assign=="E"
replace RA=0 if p_assign=="C"
label define ra_lbl 1 "Treatment" 0 "Control"
label values RA ra_lbl



*Only this variable needs rounding
gen t2q17a_aux=round(t2q17a)
drop t2q17a
rename t2q17a_aux t2q17a

*Creating a panel data
rename tq17a ssrs1
rename t2q17a ssrs2 
rename etsq13a ssrs3
keep ssrs* sampleid child p_assign agechild marital d_HS higrade ethnic age_ra pastern2 
reshape long ssrs, i(sampleid child) j(year)

egen child_id=group(sampleid child)

gen ssrs_1=ssrs if year==1
gen ssrs_2=ssrs if year==2
gen ssrs_3=ssrs if year==3
*********************************************************************************
*********************************************************************************
*This program estimates three regressions and returns the beta associated with RA
program estimates_ssrs, rclass
	version 14
	*xtset newid year
	

	forvalues x=1/3{
		*xi: oprobit ssrs i.p_assign agechild i.marital d_HS i.ethnic age_ra   if year==`x'
		xi: reg age_ra agechild if year==`x'
		return scalar ate_`x'=_b[agechild]

	}
end

*********************************************************************************
*********************************************************************************

*estimates_ssrs

/*This is inefficient, but I cannot do it the other way */
/*
*The bootstrap: tq17a t2q17a etsq13a
bootstrap beta_y2=r(ate_1) beta_y5=r(ate_2) beta_y8=r(ate_3), seed(12) reps(10) cluster(child_id) idcluster(newid) noisily/* 
*/ saving("$results/Skills/betas.dta", replace):  estimates_ssrs
*/

local rep=1000

xi: bootstrap beta_y2=_b[_Ip_assign_2], seed(12) reps(`rep') cluster(child_id) idcluster(newid) /* 
*/ saving("$results/Skills/betas_y2.dta", replace):  oprobit ssrs i.p_assign agechild i.marital d_HS higrade i.ethnic age_ra i.pastern2   if year==1

xi: bootstrap beta_y5=_b[_Ip_assign_2], seed(12) reps(`rep') cluster(child_id) idcluster(newid) /* 
*/ saving("$results/Skills/betas_y5.dta", replace):  oprobit ssrs i.p_assign agechild i.marital d_HS higrade i.ethnic age_ra i.pastern2   if year==2

xi: bootstrap beta_y8=_b[_Ip_assign_2], seed(12) reps(`rep') cluster(child_id) idcluster(newid) /* 
*/ saving("$results/Skills/betas_y8.dta", replace):  oprobit ssrs i.p_assign agechild i.marital d_HS higrade i.ethnic age_ra i.pastern2   if year==3

*Merging data sets
use "$results/Skills/betas_y2.dta", clear
egen newid=seq()
tempfile data_y2
save `data_y2', replace

use "$results/Skills/betas_y5.dta", clear
egen newid=seq()

merge 1:1 newid using `data_y2'
drop _merge

tempfile data_y5
save `data_y5', replace

use "$results/Skills/betas_y8.dta", clear
egen newid=seq()

merge 1:1 newid using `data_y5'
drop _merge


log using "$results/Skills/fadeout.smcl", replace
***********Tests********************

gen diff_y5=beta_y5-beta_y2
ttest diff_y5=0

gen diff_y8=beta_y8-beta_y5
ttest diff_y8=0


log close
