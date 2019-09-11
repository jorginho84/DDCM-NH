/*

This do-file generates a database to compute employment regressions
*/


local SE="robust"


clear
clear matrix
clear mata
set more off
set maxvar 15000

/*Employment data*/

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

*Adding employment from CSJs: CSJ==1


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






