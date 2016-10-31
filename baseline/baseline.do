/*
This do-file compares baseline characteristics of treatment and control groups.

Produces 5 tables:
-baseline summary statistics for the whole sample (baseline.xls)
-baseline summary statistics for the CFS sample (baseline_cfs_0.xls)
-baseline summary statistics for the CFS year 2 sample (baseline_cfs_2.xls)
-baseline summary statistics for the CFS year 5 sample (baseline_cfs_5.xls)
-baseline summary statistics for the CFS year 8 sample (baseline_cfs_8.xls)

*/


global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Baseline"

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
putexcel B2=matrix(baseline) using "$results/baseline", sheet("data") modify

local number=2
foreach w in "Age" "Female (%)" "African-American, non-Hispanic (%)" "Hispanic (%)" "White, non-Hispanic (%)" /*
*/  "Others (%)" "Never married (%)" "Married living w/ spouse (%)" /*
*/ "Married living apart (%)" "Separated, divorced or widowed (%)" "Highschool diploma or GED (%)" "Highest grade completed" /*
*/  "$0 (%)" "$1-999 (%)" "$1,000-4,999 (%)"  "$5,000-9,999 (%)"  "$10,000-14,999 (%)"  "$15,000 or more (%)"  {
	putexcel A`number'=("`w'") using "$results/baseline", sheet("data") modify
	local number=`number'+2
}
putexcel B1=("Treatment") using "$results/baseline", sheet("data") modify
putexcel C1=("Control") using "$results/baseline", sheet("data") modify
putexcel D1=("T-C") using "$results/baseline", sheet("data") modify
putexcel E1=("p-value") using "$results/baseline", sheet("data") modify
putexcel F1=("N") using "$results/baseline", sheet("data") modify


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
	putexcel B2=matrix(baseline) using "$results/baseline_cfs_`y'", sheet("data") modify

	local number=2
	foreach w in "Age" "Female (%)" "African-American, non-Hispanic (%)" "Hispanic (%)" "White, non-Hispanic (%)" /*
	*/  "Others (%)" "Never married (%)" "Married living w/ spouse (%)" /*
	*/ "Married living apart (%)" "Separated, divorced or widowed (%)" "Highschool diploma or GED (%)" "Highest grade completed" /*
	*/  "$0 (%)" "$1-999 (%)" "$1,000-4,999 (%)"  "$5,000-9,999 (%)"  "$10,000-14,999 (%)"  "$15,000 or more (%)"  {
		putexcel A`number'=("`w'") using "$results/baseline_cfs_`y'", sheet("data") modify
		local number=`number'+2
	}
	putexcel B1=("Treatment") using "$results/baseline_cfs_`y'", sheet("data") modify
	putexcel C1=("Control") using "$results/baseline_cfs_`y'", sheet("data") modify
	putexcel D1=("T-C") using "$results/baseline_cfs_`y'", sheet("data") modify
	putexcel E1=("p-value") using "$results/baseline_cfs_`y'", sheet("data") modify
	putexcel F1=("N") using "$results/baseline_cfs_`y'", sheet("data") modify
	
	restore

}



*******************************************************
/*CFS-Teachers' reports sample sample*/
*******************************************************

use "$databases/CFS_original.dta", clear
do "$codes/data_cfs.do"
sort sampleid
tempfile data_aux
save `data_aux', replace

use "$databases/Youth_original2.dta", clear
qui: do "$codes/data_youth.do"

keep sampleid tq1b t21fl00 et2f03
destring sampleid, force replace

*Dummies for year x respondant
gen d_year2=tq1b!=.
gen d_year5=t21fl00!=.
gen d_year8=et2f03!=.

*Leaving just one child (Child A)
duplicates drop sampleid, force

*Meging
sort sampleid
merge 1:1 sampleid using `data_aux'
keep if _merge==3
drop _merge




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
	do "$codes/baseline/baseline_aux.do"
	
	

	*the table
	putexcel B2=matrix(baseline) using "$results/baseline_teacher_`x'", sheet("data") modify

	local number=2
	foreach w in "Age" "Female (%)" "African-American, non-Hispanic (%)" "Hispanic (%)" "White, non-Hispanic (%)" /*
	*/  "Others (%)" "Never married (%)" "Married living w/ spouse (%)" /*
	*/ "Married living apart (%)" "Separated, divorced or widowed (%)" "Highschool diploma or GED (%)" "Highest grade completed" /*
	*/  "$0 (%)" "$1-999 (%)" "$1,000-4,999 (%)"  "$5,000-9,999 (%)"  "$10,000-14,999 (%)"  "$15,000 or more (%)"  {
		putexcel A`number'=("`w'") using "$results/baseline_teacher_`x'", sheet("data") modify
		local number=`number'+2
	}
	putexcel B1=("Treatment") using "$results/baseline_teacher_`x'", sheet("data") modify
	putexcel C1=("Control") using "$results/baseline_teacher_`x'", sheet("data") modify
	putexcel D1=("T-C") using "$results/baseline_teacher_`x'", sheet("data") modify
	putexcel E1=("p-value") using "$results/baseline_teacher_`x'", sheet("data") modify
	putexcel F1=("N") using "$results/baseline_teacher_`x'", sheet("data") modify
	
	restore

}


set more on
