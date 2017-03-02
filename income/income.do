/*

This do-file computes the impact of NH on total income.
Income is measured using administrative sources.

Income sources:
-UI
-Earnings supplement
-CSJs
-EITC


To compute effects by employment status: change local 'emp"

*/

global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results"


local SE="hc2"

clear
clear matrix
clear mata
set more off
set maxvar 15000

/*
controls: choose if regression should include controls for parents: age, ethnicity, marital status, and education.
*/

local controls=1

*Choose: 1 if produce income graph for employed at baseline
*Choose: 0 if produce income graph for unemployed at baseline
*Choose: 3 if total
local emp=3

use "$results/Income/data_income.dta", clear

*Many missing obs
drop total_income_y10


*****************************************
*****************************************
*THE FIGURES
*****************************************
*****************************************

*Dropping 50 adults with no information on their children
count
qui: do "$codes/income/drop_50.do"
count

*Control variables (and recovering p_assign)
do "$codes/income/Xs.do"
if `controls'==1{

	
	local control_var age_ra i.marital i.ethnic d_HS2 higrade i.pastern2
}

*Sample
if `emp'==1{
	keep if emp_baseline==1
}
else if `emp'==0{
	keep if emp_baseline==0

}


forvalues y=0/9{

	qui xi: reg total_income_y`y' i.p_assign `control_var', vce(`SE')
	local mean_`y' = _b[_Ip_assign_2]
	local lb_`y'=_b[_Ip_assign_2] - invttail(e(df_r),0.025)*_se[_Ip_assign_2]
	local ub_`y'=_b[_Ip_assign_2] + invttail(e(df_r),0.025)*_se[_Ip_assign_2]
	qui: test _Ip_assign_2=0
	local pvalue_`y'=r(p)



}

*********************
/*The figure*/
*********************
preserve

clear
set obs 10
gen year=.
gen effect=.
gen lb=.
gen ub=.
gen pvalues=.

local obs=1
forvalues year=0/9{
	replace effect=`mean_`year'' if _n==`obs'
	replace lb=`lb_`year'' if _n==`obs'
	replace ub=`ub_`year'' if _n==`obs'
	replace pvalues=`pvalue_`year'' if _n==`obs'
	replace year=`year' - 1 if _n==`obs' /*original timing*/
	local obs=`obs'+1
	
	
}

gen mean_aux_1=effect if pvalues<0.05
gen mean_aux_2=effect if pvalues>=0.05

gen year2=year*2

twoway (scatter mean_aux_2 year2,msymbol(circle) mlcolor(blue) mfcolor(white))/*
*/ (rcap ub lb year2, lw(thin)) /*
*/ (scatter mean_aux_1 year2, msymbol(circle) mlcolor(blue) mfcolor(blue)), /* 
*/ ytitle("Change in annual income (2003 dollars)")  xtitle("Years after random assignment") legend(off) /*
*/ xlabel( -2 "-1" 0 "0" 2 "1" 4 "2" 6 "3" 8 "4" 10 "5" 12 "6" 14 "7" 16 "8", noticks) /*
*/ graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white))  /*
*/ scheme(s2mono) ylabel(, nogrid) yline(0, lpattern(solid) lcolor(black)) scale(1.2) /*
*/ xline(5, lcolor(red))

graph export "$results/Income/total_income_annual_controls`controls'_emp`emp'.pdf", as(pdf) replace



restore

/*These numbers go in the text*/
/*
forvalues x=1/3{
	qui xi: reg total_income_y`x' i.p_assign `control_var', vce(`SE')
	local beta_year`x'=_b[_Ip_assign_2]
	display `beta_year`x''
	qui: sum total_income_y`x' if p_assign=="C"
	local m_`y'_control=r(mean)
	display `m_`y'_control'
	
}
*/

egen total_income_raperiod=rowmean(total_income_y1 total_income_y2 total_income_y3)
xi: reg total_income_raperiod i.p_assign , vce(`SE')
sum total_income_raperiod if p_assign=="C"


xi: reg total_income_y2 i.p_assign , vce(`SE')
sum total_income_y2 if p_assign=="C"


**********************************
/*Diff-in-Diff analysis*/
**********************************
preserve
keep sampleid total_income_y* p_assign age_ra marital ethnic d_HS2 higrade pastern2

*the panel
reshape long total_income_y, i(sampleid) j(year)

*Back to the original timing
replace year=year-1

*Diff-in-diff loop
gen d_after=year>=0
gen d_ra=p_assign=="E"
gen d_ate=d_after*d_ra



forvalues y=0/8{
	qui: reg total_income_y d_ra d_after d_ate `control_var' if year==-1 | year==`y', vce(`SE')
	test d_ate=0
	
	if `y'==0{
		mat pvalue=r(p)
	}
	
	else{
		mat pvalue=pvalue\r(p)
	}
	local mean_`y'=_b[d_ate]
	local lb_`y'=_b[d_ate] - invttail(e(df_r),0.05)*_se[d_ate]
	local ub_`y'=_b[d_ate] + invttail(e(df_r),0.05)*_se[d_ate]
	
	}

*The graph
clear
set obs 10 /*6 years*/
gen year=.
gen effect=.
gen lb=.
gen ub=.
gen pvalues=.

local obs=1
forvalues year=0/8{
	replace effect=`mean_`year'' if _n==`obs'
	replace lb=`lb_`year'' if _n==`obs'
	replace ub=`ub_`year'' if _n==`obs'
	replace pvalues=pvalue[`obs',1] if _n==`obs'
	replace year=`year' if _n==`obs'
	local obs=`obs'+1
	
	
}

*To indicate p-value in graph
gen mean_aux_1=effect if pvalues<0.05
gen mean_aux_2=effect if pvalues>=0.05

*new identifier
gen year2=year*2

twoway (bar effect year2) (rcap ub lb year2) /* These are the mean effect and the 90% confidence interval
*/ (scatter mean_aux_1 year2,  msymbol(circle) mcolor(blue) mfcolor(blue)) (scatter mean_aux_2 year2,   msymbol(circle) mcolor(blue) mfcolor(none)), /*
*/ ytitle("Annual income (2003 dollars)")  xtitle("Years after random assignment") legend(off) /*
*/ xlabel( 0 "0" 2 "1" 4 "2" 6 "3" 8 "4" 10 "5" 12 "6" 14 "7" 16 "8", noticks) /*
*/ graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white))  /*
*/ scheme(s2mono) ylabel(, nogrid) yline(0, lpattern(solid) lcolor(black))

graph export "$results/Income/income_diffdiff.pdf", as(pdf) replace





restore
