/*
This do-file computes the effect of New Hope on labor supply using UI administrative data and a diff-in-diff analysis

The main figure: Trends of employment probability by groups, quarters since RA, and employment status at baseline

This do-file may also compute:
-the difference in employment by quarters since RA
-difference and levels by quarters in calendar time

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
This works only for estimates based on quarters since RA
*/

local controls=1


clear
clear matrix
clear mata
set more off
set maxvar 15000

*************************************************************************************
*************************************************************************************
*************************************************************************************
/*In this part I compute impacts by quarters since RA*/

*************************************************************************************
*************************************************************************************
*************************************************************************************





use "$databases/CFS_original.dta", clear
do "$codes/data_cfs.do"

keep sampleid p_assign p_radatr curremp /*
*/emp1q* emp2q* emp3q* emp4q*  /*employment variables from UI
*/csjm94* csjm95* csjm96* csjm97* /*amount from CSJs*/

*Generate monthly employment from CSJs

forvalues y=94/97{
	local mm=1
	foreach month in "01" "02" "03" "04" "05" "06" "07" "08" "09" "10" "11" "12" {
	
	*dummy variable
	gen emp_csjm`y'`month'=1 if csjm`y'`month'>0 & csjm`y'`month'!=.
	replace emp_csjm`y'`month'=0 if csjm`y'`month'==0
	
	if `mm'<=9{
		rename emp_csjm`y'`month' emp_csjm`y'`mm' /*get rid of 0's*/
	}
	
	local mm=`mm'+1
	
	
	}
}

*Generate quarterly employment from CSJ
forvalues y=94/97{

	local month=1

	forvalues q=1/4{
		local month2=`month'+1
		local month3=`month2'+1
		
		gen qemp_csjm`y'`q'=1 if emp_csjm`y'`month'==1 | emp_csjm`y'`month2'==1 | emp_csjm`y'`month3'==1
		replace qemp_csjm`y'`q'=0 if emp_csjm`y'`month'==0 & emp_csjm`y'`month2'==0 & emp_csjm`y'`month3'==0
		
		local month=`month'+3
	
	
	}
}



*Quarter of RA
replace p_radatr=p_radatr+19000000
tostring p_radatr, force replace
gen ra_quarter=qofd(date(p_radatr,"YMD"))
format ra_quarter %tq
tab ra_quarter

*Generate employment in quarter number X since RA

replace emp4q93=emp4q93/100
rename emp4q93 emp1993q4

local nn=1
forvalues y=94/99{
	forvalues q=1/4{

		replace emp`q'q`y'=emp`q'q`y'/100
		rename emp`q'q`y' emp19`y'q`q'
		
	}
}

local yy=0
forvalues y=2000/2003{
	forvalues q=1/4{

		replace emp`q'q0`yy'=emp`q'q0`yy'/100
		rename emp`q'q0`yy' emp200`yy'q`q' 
			
	}

local yy=`yy'+1

}

*Adding employment from CSJs

forvalues y=94/97{
	
	forvalues q=1/4{
	
		replace emp19`y'q`q'=1 if qemp_csjm`y'`q'==1
	
	}

}


*Reshaping to build a panel
drop emp_* /*drop csj indicators*/
keep emp* sampleid ra_quarter
reshape long emp, i(sampleid) j(quarter_aux) string
gen quarter=quarterly(quarter_aux, "YQ")
format quarter %tq

*Quarters since RA
gen quarters_ra=quarter-ra_quarter
keep quarters_ra sampleid emp
tab quarters_ra/*this is to see how many obs*/


*Reshape again to build the graph using collapse
replace quarters_ra=quarters_ra+8/*trick to reshape*/
reshape wide emp, i(sampleid) j(quarters_ra) 

*recovering RA
sort sampleid
tempfile data_aux
save `data_aux', replace
use "$databases/CFS_original.dta", clear
do "$codes/data_cfs.do"



keep sampleid p_assign curremp
sort sampleid
merge 1:1 sampleid using `data_aux'
drop _merge


********************************************************************************
if `controls'==1{

	do "$codes/time/Xs.do"
	local control_var age_ra i.marital i.ethnic d_HS higrade i.pastern2

}


********************************************************************************

*Dropping 50 observations with no children
do "$codes/time/drop_50.do"


********************************************************************************
/*The panel*/
********************************************************************************
*Not considering these ones: do not have full sample
drop emp0 emp1 emp2 emp3 emp4

drop emp41 emp42 emp43 emp44 emp45


*employment variables
gen emp_year0=emp5==1 | emp6==1 | emp7==1
	
*years 1-6
local x1=8
forvalues y=1/6{
	local x2=`x1'+1
	local x3=`x1'+2
	local x4=`x1'+3
	gen emp_year`y'=emp`x1'==1 | emp`x2'==1 | emp`x3'==1
	local x1=`x1'+4
}


keep sampleid emp_year* p_assign curremp age_ra marital ethnic d_HS higrade pastern2

*the panel
reshape long emp_year, i(sampleid) j(year)



********************************************************************************
********************************************************************************
********************************************************************************
/*

FIGURES

*/
********************************************************************************
********************************************************************************
********************************************************************************



*Diff-in-diff loop
gen d_after=year>0
gen d_ra=p_assign=="E"
gen d_ate=d_after*d_ra

forvalues y=1/6{
	qui: reg emp_year d_ra d_after d_ate `control_var' if year==0 | year==`y', vce(`SE')
	test d_ate=0
	
	if `y'==1{
		mat pvalue=r(p)
	}
	
	else{
		mat pvalue=pvalue\r(p)
	}
	local mean_`y'=_b[d_ate]
	local lb_`y'=_b[d_ate] - invttail(e(df_r),0.05)*_se[d_ate]
	local ub_`y'=_b[d_ate] + invttail(e(df_r),0.05)*_se[d_ate]
	
	}


*******************************************************
/*The graph*/
*******************************************************

clear
set obs 6 /*6 years*/
gen year=.
gen effect=.
gen lb=.
gen ub=.
gen pvalues=.

local obs=1
forvalues year=1/6{
	replace effect=`mean_`year''*100 if _n==`obs'
	replace lb=`lb_`year''*100 if _n==`obs'
	replace ub=`ub_`year''*100 if _n==`obs'
	replace pvalues=pvalue[`obs',1] if _n==`obs'
	replace year=`obs' if _n==`obs'
	local obs=`obs'+1
	
	
}


*To indicate p-value in graph
gen mean_aux_1=effect if pvalues<0.05
gen mean_aux_2=effect if pvalues>=0.05

*new identifier
gen year2=year*2

twoway (bar effect year2) (rcap ub lb year2) /* These are the mean effect and the 90% confidence interval
*/ (scatter mean_aux_1 year2,  msymbol(circle) mcolor(blue) mfcolor(blue)) (scatter mean_aux_2 year2,   msymbol(circle) mcolor(blue) mfcolor(none)), /*
*/ ytitle("Employment (percentage points)")  xtitle("Years after random assignment") legend(off) /*
*/ xlabel( 2 "1" 4 "2" 6 "3" 8 "4" 10 "5" 12 "6", noticks) /*
*/ graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white))  /*
*/ scheme(s2mono) ylabel(, nogrid) yline(0, lpattern(solid) lcolor(black))

graph save "$results/Time/LS_dd.gph", replace
graph export "$results/Time/LS_dd.pdf", as(pdf) replace
