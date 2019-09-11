/*
This do-file computes the prob of ranking SSRS>=4 using bootstrap
*/

clear
program drop _all
clear matrix
clear mata
set more off
set maxvar 15000
set matsize 2000


local reps = 1000

use "/home/jrodriguez/NH-secure/Youth_original2.dta", clear

*labels
qui: do "/home/jrodriguez/NH_HC/codes/data_youth.do"
keep  sampleid child p_assign zboy agechild p_assign p_radaym sdkidbd  /*
*/ tacad tq17* /* Y2: SSRS (block1)
*/ tcsbs tcsis tcsts tcstot  /* Y2: CBS (block2)
*/ t2q17a t2q17b t2q17c t2q17d t2q17e t2q17f t2q17g t2q17h t2q17i t2q17j /* Y5: SSRS (block2)
*/ etsq13a etsq13b etsq13c etsq13d etsq13e etsq13f etsq13g etsq13h etsq13i etsq13j /* Y8: teachers reports: SSRS academic subscale (block 2)
*/ piq146a piq146b piq146c piq146d /**/


*Age at baseline
destring sdkidbd, force replace
format sdkidbd %td
gen year_birth=yofd(sdkidbd)

*child age at baseline
gen year_ra = substr(string(p_radaym),1,2)
destring year_ra, force replace
replace year_ra = 1900 + year_ra

gen age_t0=  year_ra - year_birth

*due to rounding errors, ages 0 and 11 are 1 and 10
replace age_t0 = 1 if age_t0 == 0
replace age_t0 = 10 if age_t0 == 11
drop if age_t0 < 1 | age_t0 > 11

*gender
gen d_girl = 1 if zboy == "0"
replace d_girl= 0 if zboy == "1"



*Treatment
gen d_ra= 1 if p_assign == "E"
replace d_ra = 0 if p_assign == "C" 

/*Local labels: use these in regressions*/
local Y2_B1 tq17a tq17b tq17c tq17d tq17e tq17f tq17g tq17h tq17i tq17j
local Y5_B2 t2q17a t2q17b t2q17c t2q17d t2q17e t2q17f t2q17g t2q17h t2q17i t2q17j
local Y8_B2 etsq13a etsq13b etsq13c etsq13d etsq13e etsq13f etsq13g etsq13h etsq13i etsq13j
local Y2_B2 tcsbs tcsis tcsts

destring `Y2_B1' `Y5_B2' `Y8_B2' `Y2_B2' tacad tcstot , force replace



*Rounding up variables to the nearest integer
foreach variable of varlist `Y2_B1' `Y5_B2' `Y8_B2' {
	gen `variable'_s=round(`variable')
	drop `variable'
	rename `variable'_s `variable'
}


/*Computing SSRS scores*/
gen sample_2 = tq17a!=. & tq17b!=. & tq17c!=. & tq17d!=. & tq17e!=. & tq17f!=. & tq17g!=. & tq17h!=. & tq17i!=. & tq17j!=.
gen sample_5 = t2q17a!=. & t2q17b!=. & t2q17c!=. & t2q17d!=. & t2q17e!=. & t2q17f!=. & t2q17g!=. & t2q17h!=. & t2q17i!=. & t2q17j!=.
gen sample_8 = etsq13a!=. & etsq13b!=. & etsq13c!=. & etsq13d!=. & etsq13e!=. & etsq13f!=. & etsq13g!=. & etsq13h!=. & etsq13i!=. & etsq13j!=.


egen ssrs_2 = rowmean(`Y2_B1') 
egen ssrs_5 = rowmean(`Y5_B2') 
egen ssrs_8 = rowmean(`Y8_B2')

 *Rounding up variables to the nearest integer
foreach variable of varlist ssrs_2 ssrs_5 ssrs_8 {
	egen `variable'_s=std(`variable')
	drop `variable'
	rename `variable'_s `variable'
}

gen d_RA = 1 if p_assign == "E"
replace d_RA = 0 if p_assign == "C" 

foreach x in 2 5{
	bootstrap, reps(`reps'): reg ssrs_`x' d_RA
	mat betas_aux_`x'=e(b)
	mat se_aux_`x'=e(se)
	mat betas_t`x'=betas_aux_`x'[1,1]
	mat ses_t`x'=se_aux_`x'[1,1]

	bootstrap, reps(`reps'): reg ssrs_`x' d_RA if age_t0 <= 4
	mat betas_aux_`x'_y=e(b)
	mat se_aux_`x'_y=e(se)
	mat betas_t`x'_y=betas_aux_`x'_y[1,1]
	mat ses_t`x'_y=se_aux_`x'_y[1,1]

	bootstrap, reps(`reps'): reg ssrs_`x' d_RA if age_t0 > 4
	mat betas_aux_`x'_o=e(b)
	mat se_aux_`x'_o=e(se)
	mat betas_t`x'_o=betas_aux_`x'_o[1,1]
	mat ses_t`x'_o=se_aux_`x'_o[1,1]

}



foreach x in 2 5{
	
	preserve
	clear
	set obs 1
	svmat betas_t`x'
	outsheet using "/home/jrodriguez/NH_HC/results/model_v2/fit/beta_t`x'_obs.csv", comma replace
	restore

	preserve
	clear
	set obs 1
	svmat betas_t`x'_y
	outsheet using "/home/jrodriguez/NH_HC/results/model_v2/fit/beta_t`x'_y_obs.csv", comma replace
	restore


	preserve
	clear
	set obs 1
	svmat betas_t`x'_o
	outsheet using "/home/jrodriguez/NH_HC/results/model_v2/fit/beta_t`x'_o_obs.csv", comma replace
	restore

	preserve
	clear
	set obs 1
	svmat ses_t`x'
	outsheet using "/home/jrodriguez/NH_HC/results/model_v2/fit/ses_beta_t`x'_obs.csv", comma replace
	restore

	preserve
	clear
	set obs 1
	svmat ses_t`x'_y
	outsheet using "/home/jrodriguez/NH_HC/results/model_v2/fit/ses_beta_t`x'_y_obs.csv", comma replace
	restore

	preserve
	clear
	set obs 1
	svmat ses_t`x'_o
	outsheet using "/home/jrodriguez/NH_HC/results/model_v2/fit/ses_beta_t`x'_o_obs.csv", comma replace
	restore


}



exit, STATA clear





