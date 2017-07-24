global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/HH_summary"

clear
program drop _all
clear matrix
clear mata
set maxvar 15000
set more off
set matsize 2000


use "$databases/Youth_original2.dta", clear

*labels
qui: do "$codes/data_youth.do"
keep  sampleid child p_assign zboy agechild p_assign curremp /*
*/ tq17* /* Y2: SSRS (block1)
*/ tcsbs tcsis tcsts   /* Y2: CBS (block2)
*/ wjss22 wjss23 wjss24 wjss25 /* Y5: Woodscok-Johnson (block1)
*/ t2q17a t2q17b t2q17c t2q17d t2q17e t2q17f t2q17g t2q17h t2q17i t2q17j /* Y5: SSRS (block2)
*/ t2q16a t2q16b t2q16c t2q16d t2q16e t2q16f /* Y5: mock (block3)
*/ bhvscaf2 trnscaf2 indscaf2 /* Y5: CBS (block4)
*/ piq146a piq146b piq146c piq146d /* Y5: parents' report (block5)
*/ ewjss22 ewjss25 /* Y8: Woodscok-Johnson (block1)
*/ etsq13a etsq13b etsq13c etsq13d etsq13e etsq13f etsq13g etsq13h etsq13i etsq13j /* Y8: teachers reports: SSRS academic subscale (block 2)
*/etsq12a etsq12b etsq12c etsq12d etsq12e etsq12f /* Y8: teachers' reports: mock cards (block3)
*/ bhvscaf3 trnscaf3 indscaf3 /* Y8: teachers' report: classroom behavior scale (block 4)
*/ epi124a epi124b epi124c epi124d /*  Y8: parents' report, school achievement (block 5)*/

/*Local labels: use these in regressions*/
local Y2_B1 tq17a tq17b tq17c tq17d tq17e tq17f tq17g tq17h tq17i tq17j
local Y5_B2 t2q17a t2q17b t2q17c t2q17d t2q17e t2q17f t2q17g t2q17h t2q17i t2q17j
local Y8_B2 etsq13a etsq13b etsq13c etsq13d etsq13e etsq13f etsq13g etsq13h etsq13i etsq13j

*Rounding up variables to the nearest integer
foreach variable of varlist `Y2_B1' `Y2_B2' `Y5_B2' `Y5_B3' `Y5_B5' {
	gen `variable'_s=round(`variable')
	drop `variable'
	rename `variable'_s `variable'
}


*Standardize

foreach variable of varlist `Y2_B1'  `Y5_B2' `Y8_B2' {
	gen `variable'_s=`variable'>=3
	replace `variable'_s=0 if `variable'<3
	drop `variable'
	rename `variable'_s `variable'
}


/*
*Dummy variables
foreach variable of varlist `Y2_B1'  `Y5_B2' `Y8_B2' {
	gen `variable'_d = .
	replace `variable'_d = 1 if `variable'>=4
	replace `variable'_d = 0 if `variable'<4
	replace `variable'_d = .  if `variable'==.
	drop `variable'
	rename `variable'_d `variable'
}
*/


*Control variables
qui: do "$codes/skills/Xs.do"


*Young at t=2
gen d_young = .
replace d_young=1 if agechild<=6
replace d_young=0 if agechild>6

/*PCS year 2*/

pca `Y2_B1', components(1)
predict score yhat2
gen y2_raw = score
egen yhat2 = std(score)
drop score


pca `Y5_B2', components(1)
predict score yhat5
gen y5_raw = score
egen yhat5 = std(score)
drop score


pca `Y8_B2', components(1)
predict score yhat8
gen y8_raw = score
egen yhat8 = std(score)
drop score


/*PCA estimates*/
foreach year in 2 5 8 {
	xi: reg yhat`year' i.p_assign
	local beta_`year' = _b[_Ip_assign_2]
	local lb_`year'=_b[_Ip_assign_2] - invttail(e(df_r),0.05)*_se[_Ip_assign_2]
	local ub_`year'=_b[_Ip_assign_2] + invttail(e(df_r),0.05)*_se[_Ip_assign_2]

}
preserve
clear
set obs 3
gen betas=.
gen lb=.
gen ub=.
gen year=.

local i = 1
foreach year in 2 5 8{
	replace betas = `beta_`year'' if _n==`i'
	replace lb = `lb_`year'' if _n==`i'
	replace ub = `ub_`year'' if _n==`i'
	replace year = `i' if _n==`i'
	local i = `i' + 1 
}


twoway (connected betas year,msymbol(circle) mlcolor(blue) mfcolor(white)) /*
*/ (rcap ub lb year), /* These are the mean effect and the 90% confidence interval
*/ ytitle("Impact on PCA factor (in {&sigma})")  xtitle("Years after random assignment") legend(off) /*
*/ xlabel( 1 "2" 2 "5" 3 "8", noticks) /*
*/ graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white))  /*
*/ scheme(s2mono) ylabel(, nogrid) yline(0, lpattern(dash) lcolor(black))

graph export "$results/pca.pdf", as(pdf) replace


