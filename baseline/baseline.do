/*
This do-file compares baseline characteristics of treatment and control groups.

Produces 5 tables:
-baseline summary statistics for the whole sample (baseline.xls)
-baseline summary statistics for the CFS sample (baseline_cfs_0.xls)
-baseline summary statistics for the CFS year 2 sample (baseline_cfs_2.xls)
-baseline summary statistics for the CFS year 5 sample (baseline_cfs_5.xls)
-baseline summary statistics for the CFS year 8 sample (baseline_cfs_8.xls)


to compute baseline characteristics of estimation sample, run sample_model.do first

*/


global databases "/home/jrodriguez/NH-secure"
global codes "/home/jrodriguez/NH_HC/codes"
global results "/home/jrodriguez/NH_HC/results/Baseline"

clear
clear matrix
clear mata
set maxvar 15000
set more off

global SE "hc2"

*******************************************************
/*All adults database*/
*******************************************************

use "$databases/Adults_original.dta", clear
qui: do "$codes/data_adults.do"



*Constructing the matrix baseline
do "$codes/baseline/baseline_aux.do"


*the table
putexcel set "$results/baseline", sheet("data") modify
putexcel B2=matrix(baseline)

local number=2
foreach w in "Age" "Female (%)" "African-American, non-Hispanic (%)" "Hispanic (%)" "White, non-Hispanic (%)" /*
*/  "Others (%)" "Never married (%)" "Married living w/ spouse (%)" /*
*/ "Married living apart (%)" "Separated, divorced or widowed (%)" "Highschool diploma or GED (%)" "Highest grade completed" /*
*/  "$0 (%)" "$1-999 (%)" "$1,000-4,999 (%)"  "$5,000-9,999 (%)"  "$10,000-14,999 (%)"  "$15,000 or more (%)"  {
	putexcel A`number'=("`w'")
	local number=`number'+2
}
putexcel B1=("Treatment") 
putexcel C1=("Control") 
putexcel D1=("T-C") 
putexcel E1=("p-value") 
putexcel F1=("N") 


*******************************************************
/*CFS sample*/
*******************************************************

use "$databases/CFS_original.dta", clear
qui: do "$codes/data_cfs.do"

*Dropping 50 adults with no children
qui: do "$codes/baseline/drop_50.do"


*Restricting sample: 2-, 5-, and 8-year surveys


forvalues x=-1(3)8{

	preserve

	*Restricting the sample
	
	if `x'==2{
		keep if c1!=" "
	}
	
	else if `x'==5{
		keep if piinvyy!=" "
	}
	
	else if `x'==8{
		keep if epiinvyy!=" "
	}
	
	*Constructing the matrix baseline
	do "$codes/baseline/baseline_aux.do"
	
	*Name of spreadsheet
	if `x'==-1{
		local y=0
	}
	else{
		local y=`x'
	}


	*the table
	putexcel set "$results/baseline_cfs_`y'", sheet("data") modify
	putexcel B2=matrix(baseline) 

	local number=2
	foreach w in "Age" "Female (%)" "African-American, non-Hispanic (%)" "Hispanic (%)" "White, non-Hispanic (%)" /*
	*/  "Others (%)" "Never married (%)" "Married living w/ spouse (%)" /*
	*/ "Married living apart (%)" "Separated, divorced or widowed (%)" "Highschool diploma or GED (%)" "Highest grade completed" /*
	*/  "$0 (%)" "$1-999 (%)" "$1,000-4,999 (%)"  "$5,000-9,999 (%)"  "$10,000-14,999 (%)"  "$15,000 or more (%)"  {
		putexcel A`number'=("`w'") 
		local number=`number'+2
	}
	putexcel B1=("Treatment") 
	putexcel C1=("Control") 
	putexcel D1=("T-C") 
	putexcel E1=("p-value") 
	putexcel F1=("N") 
	
	restore

}


*******************************************************
/*CFS sample: estimation sample*/
*******************************************************
use "/home/jrodriguez/NH_HC/results/model_v2/sample_model.dta", clear


*Constructing the matrix baseline
do "$codes/baseline/baseline_aux_2.do"

*the table
putexcel set "$results/baseline_cfs_estimation", sheet("data") modify
putexcel B2=matrix(baseline)

local number=2
foreach w in "Age" "Female (%)" "African-American, non-Hispanic (%)" /*
*/ "Hispanic (%)" "White, non-Hispanic (%)" /*
*/  "Others (%)" "Never married (%)" "Married living w/ spouse (%)" /*
*/ "Married living apart (%)" "Separated, divorced or widowed (%)" "Highschool diploma or GED (%)" "Highest grade completed" /*
*/  "$0 (%)" "$1-999 (%)" "$1,000-4,999 (%)"  "$5,000-9,999 (%)"  "$10,000-14,999 (%)"  "$15,000 or more (%)"  {
	putexcel A`number'=("`w'")
	local number=`number'+2
}
putexcel B1=("Treatment") 
putexcel C1=("Control") 
putexcel D1=("T-C") 
putexcel E1=("p-value") 
putexcel F1=("N")


*******************************************************
/*CFS sample: estimation sample +  parents young children*/
*******************************************************
use "/home/jrodriguez/NH_HC/results/model_v2/sample_model.dta", clear
gen age_t2 = age_t0 + 2
keep if age_t2<=6

*Constructing the matrix baseline
do "$codes/baseline/baseline_aux_2.do"

*the table
putexcel set "$results/baseline_cfs_estimation_young", sheet("data") modify
putexcel B2=matrix(baseline)

local number=2
foreach w in "Age" "Female (%)" "African-American, non-Hispanic (%)" /*
*/ "Hispanic (%)" "White, non-Hispanic (%)" /*
*/  "Others (%)" "Never married (%)" "Married living w/ spouse (%)" /*
*/ "Married living apart (%)" "Separated, divorced or widowed (%)" "Highschool diploma or GED (%)" "Highest grade completed" /*
*/  "$0 (%)" "$1-999 (%)" "$1,000-4,999 (%)"  "$5,000-9,999 (%)"  "$10,000-14,999 (%)"  "$15,000 or more (%)"  {
	putexcel A`number'=("`w'")
	local number=`number'+2
}
putexcel B1=("Treatment") 
putexcel C1=("Control") 
putexcel D1=("T-C") 
putexcel E1=("p-value") 
putexcel F1=("N")




*******************************************************
/*CFS-Teachers' reports sample */
*******************************************************

use "/home/jrodriguez/NH_HC/results/model_v2/sample_model.dta", clear


*Dummies for year x respondant
gen d_year2= skills_t2 !=.
gen d_year5= skills_t5 !=.
gen d_year8= skills_t8 !=.




*Restricting sample: 2-, 5-, and 8-year surveys
forvalues x=2(3)8{

	preserve

	*Restricting the sample
	
	if `x'==2{
		keep if d_year2==1
	}
	
	else if `x'==5{
		keep if d_year5==1
	}
	
	else if `x'==8{
		keep if d_year8==1
	}
	
	*Constructing the matrix baseline
	do "$codes/baseline/baseline_aux_2.do"
	
	

	*the table
	putexcel set "$results/baseline_teacher_`x'", sheet("data") modify
	putexcel B2=matrix(baseline) 

	local number=2
	foreach w in "Age" "Female (%)" "African-American, non-Hispanic (%)" "Hispanic (%)" "White, non-Hispanic (%)" /*
	*/  "Others (%)" "Never married (%)" "Married living w/ spouse (%)" /*
	*/ "Married living apart (%)" "Separated, divorced or widowed (%)" "Highschool diploma or GED (%)" "Highest grade completed" /*
	*/  "$0 (%)" "$1-999 (%)" "$1,000-4,999 (%)"  "$5,000-9,999 (%)"  "$10,000-14,999 (%)"  "$15,000 or more (%)"  {
		putexcel A`number'=("`w'") 
		local number=`number'+2
	}
	putexcel B1=("Treatment") 
	putexcel C1=("Control") 
	putexcel D1=("T-C") 
	putexcel E1=("p-value") 
	putexcel F1=("N") 
	
	restore

}


set more on
