/*
This do-file prepares data for factor analysis

It produces three data sets (years 2, 5, and 8)

*/

global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Skills"

clear
program drop _all
clear matrix
clear mata
set maxvar 15000
set more off
set matsize 2000


use "$databases/Youth_original2.dta", clear

qui: do "$codes/data_youth.do"
keep  sampleid child p_assign zboy agechild p_assign  /*
*/ tq17* /* Y2: SSRS (block1)
*/ t2q17a t2q17b t2q17c t2q17d t2q17e t2q17f t2q17g t2q17h t2q17i t2q17j /* Y5: SSRS (block2)
*/ etsq13a etsq13b etsq13c etsq13d etsq13e etsq13f etsq13g etsq13h etsq13i etsq13j /* Y8: teachers reports: SSRS academic subscale (block 2)*/

/*Local labels: use these in regressions*/
local Y2 tq17a tq17b tq17c tq17d tq17e tq17f tq17g tq17h tq17i tq17j
local Y5 t2q17a t2q17b t2q17c t2q17d t2q17e t2q17f t2q17g t2q17h t2q17i t2q17j
local Y8 etsq13a etsq13b etsq13c etsq13d etsq13e etsq13f etsq13g etsq13h etsq13i etsq13j

*Rounding up variables to the nearest integer
foreach variable of varlist `Y2' `Y5' `Y8'{
	gen `variable'_s=round(`variable')
	drop `variable'
	rename `variable'_s `variable'
}

*#Recovering control variables
qui: do "$codes/skills/Xs.do"

gen d_young = agechild<=6
replace d_young = 0 if agechild>6 

foreach year in 2 5 8{
	preserve
	keep p_assign `Y`year'' emp_baseline d_young
	gen d_RA = 1 if p_assign=="E"
	replace d_RA=0 if p_assign=="C"
	drop p_assign

	*sample: only with valid obs
	foreach variable of varlist `Y`year''{
		drop if `variable'==.
	}


	outsheet using "$results/data_measures_y`year'.csv", comma replace
	restore

}
