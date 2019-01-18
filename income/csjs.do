/*
This do-file computes the proportion of individuals with positive 
CSJ monthly earnings


*/



global databases "/home/jrodriguez/NH-secure"
global codes "/home/jrodriguez/understanding_NH/codes"
global results "/home/jrodriguez/understanding_NH/results"




clear
clear matrix
clear mata
scalar drop _all
set more off
set maxvar 15000



*Use the CFS study
use "$databases/CFS_original.dta", clear
qui: do "$codes/data_cfs.do"

keep sampleid p_assign p_radatr cstartm curremp c1 piinvyy epiinvyy /*
*/ern*q* sup*q* csjm9* /*UI earnings, NH supplement, CSJ's
*/ kid*daty  c53d_1 piq93e epi74e /*kids at baseline and births
*/ c53d_3 /*Year of birth*/


**********************************
*CSJ: quarters in calendar time
**********************************

*Renaming CSJ calendar-time variables
forvalues y=94/97{

	local m=1
	foreach month in "01" "02" "03" "04" "05" "06" "07" "08" "09" "10" "11" "12"{
		rename csjm`y'`month' csj19`y'm`m'
		
		gen d_csj19`y'm`m' = csj19`y'm`m' > 0

		sum d_csj19`y'm`m'

		local m=`m'+1
	}
	
} 

keep d_csj19* sampleid
reshape long d_csj, i(sampleid) j(year) string

sum d_csj
