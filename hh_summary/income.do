/*
This do-file computes treatment effects on income

*/


global databases "/home/jrodriguez/NH-secure"
global codes "/home/jrodriguez/NH_HC/codes"
global results "/home/jrodriguez/NH_HC/results"

local SE="robust"


clear
clear matrix
clear mata
set more off
set maxvar 15000




/*Recovering child's age*/

use "$databases/Youth_original2.dta", clear

*labels
qui: do "$codes/data_youth.do"
keep  sampleid child p_assign zboy agechild p_assign p_radaym sdkidbd gender



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
replace age_t0=1 if age_t0==0
replace age_t0=10 if age_t0==11
drop if age_t0 < 1 | age_t0 > 11


keep age_t0 sampleid child p_assign gender
reshape wide age_t0, i(sampleid) j(child)

tempfile child_aux
save `child_aux', replace


*****************************************************************
*****************************************************************
/*INCOME EFFECTS*/
*****************************************************************
*****************************************************************




/*generate income database*/

qui: do "$codes/hh_summary/data_income.do"


drop total_income_y0 gross_y0 gross_nominal_y0 grossv2_y0 employment_y0 /*
*/ fs_y0 afdc_y0 sup_y0 eitc_state_y0 eitc_fed_y0
forvalues x=1/10{
	local z=`x'-1
	rename total_income_y`x' total_income_y`z'
	rename gross_y`x' gross_y`z'
	rename grossv2_y`x' grossv2_y`z'
	rename gross_nominal_y`x' gross_nominal_y`z'
	rename employment_y`x' employment_y`z'
	rename afdc_y`x' afdc_y`z'
	rename fs_y`x' fs_y`z'
	rename sup_y`x' sup_y`z'
	rename eitc_fed_y`x' eitc_fed_y`z'
	rename eitc_state_y`x' eitc_state_y`z'

	gen eitc_y`z' = eitc_fed_y`z' + eitc_state_y`z'
	gen welfare_y`z' = fs_y`z' + sup_y`z'

}




*Dropping adults with no information on their children
merge 1:1 sampleid using `child_aux'
keep if _merge == 3
drop _merge



*age of youngest
egen age_y = rowmin(age_t0*)

gen d_ra= 1 if p_assign == "E"
replace d_ra = 0 if p_assign == "C" 

keep if gender == 2

*baseline
restore
keep total_income_y* sampleid age_y d_ra
reshape long total_income_y, i(sampleid) j(year)
qui: sum total_income_y if age_y<=4 & year <=2 & d_ra == 0
local baseline = r(mean)
preserve

forvalues x=0/8{
	qui: reg total_income_y`x' d_ra if age_y<=4, vce("robust")
	local beta_y`x' = _b[d_ra]
	local lb_y`x'=_b[d_ra] - invttail(e(df_r),0.025)*_se[d_ra]
	local ub_y`x'=_b[d_ra] + invttail(e(df_r),0.025)*_se[d_ra]

	qui: reg total_income_y`x' d_ra if age_y>4, vce("robust")
	local beta_o`x' = _b[d_ra]
	local lb_o`x'=_b[d_ra] - invttail(e(df_r),0.025)*_se[d_ra]
	local ub_o`x'=_b[d_ra] + invttail(e(df_r),0.025)*_se[d_ra]

	qui: reg eitc_y`x' d_ra if age_y<=4, vce("robust")
	local beta_e`x' = _b[d_ra]
	local lb_e`x'=_b[d_ra] - invttail(e(df_r),0.025)*_se[d_ra]
	local ub_e`x'=_b[d_ra] + invttail(e(df_r),0.025)*_se[d_ra]

	qui: reg welfare_y`x' d_ra if age_y<=4, vce("robust")
	local beta_w`x' = _b[d_ra]
	local lb_w`x'=_b[d_ra] - invttail(e(df_r),0.025)*_se[d_ra]
	local ub_w`x'=_b[d_ra] + invttail(e(df_r),0.025)*_se[d_ra]

	qui: reg eitc_y`x' d_ra if age_y<=4, vce("robust")
	local beta_e`x' = _b[d_ra]
	local lb_e`x'=_b[d_ra] - invttail(e(df_r),0.025)*_se[d_ra]
	local ub_e`x'=_b[d_ra] + invttail(e(df_r),0.025)*_se[d_ra]

	qui: reg gross_y`x' d_ra if age_y<=4, vce("robust")
	local beta_g`x' = _b[d_ra]
	local lb_g`x'=_b[d_ra] - invttail(e(df_r),0.025)*_se[d_ra]
	local ub_g`x'=_b[d_ra] + invttail(e(df_r),0.025)*_se[d_ra]
}



*preserve
clear

set obs 27
gen effects_y = .
gen effects_o = .
gen lb_y = .
gen ub_y = .
gen lb_o = .
gen ub_o = .
gen year = .


forvalues x=1/9{
	local i = `x'*3 - 1
	local y = `x' - 1
	replace effects_y = `beta_y`y''/100 if _n == `i'
	replace lb_y = `lb_y`y''/100 if _n == `i'
	replace ub_y = `ub_y`y''/100 if _n == `i'
	local y=`y' + 1
}


forvalues x=1/9{
	local i = `x'*3
	local y = `x' - 1
	replace effects_o = `beta_o`y''/100 if _n == `i'
	replace lb_o = `lb_o`y''/100 if _n == `i'
	replace ub_o = `ub_o`y''/100 if _n == `i'
	local y=`y' + 1
}

forvalues x = 1/27{
	replace year = `x' if _n == `x'
}



twoway (scatter effects_y year, msize(large) mcolor(blue))  /*
*/(scatter effects_o year, msize(large) mcolor(red)) /*
*/ (rcap ub_y lb_y year, lwidth(medthick) lpattern(dash) lcolor(blue) ) /*
*/ (rcap ub_o lb_o year, lwidth(medthick) lpattern(dash) lcolor(red) ), /*
*/ ytitle("Impact on income (in 2003 dollars/100)")  xtitle("Years from baseline") legend(off)/*
*/ xlabel( 2.5 "0" 5.5 "1" 8.5 "2" 11.5 "3" 14.5 "4" 17.5 "5" 20.5 "6" 23.5 "7" 26.5 "8") /*
*/ graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white))  /*
*/ scheme(s2mono) ylabel(, nogrid) yline(0, lpattern(dash) lcolor(black)) scale(1.2)

graph export "$results/hh_summary/income.pdf", as(pdf) replace

*restore

sum effects_y if year < 10
stop!

*Components*/
preserve

clear
set obs 9
gen effects_e = .
gen effects_w = .
gen effects_g = .
gen lb_e = .
gen ub_e = .
gen lb_w = .
gen ub_w = .
gen lb_g = .
gen ub_g = .
gen year = .


local y=0
forvalues x = 1/8{
	replace year = `x' - 1 if _n == `x'
	replace effects_e = `beta_e`x'' if _n == `x'
	replace effects_w = `beta_w`x'' if _n == `x'
	replace effects_g = `beta_g`x'' if _n == `x'

	replace lb_e = `lb_e`x'' if _n == `x'
	replace ub_e = `ub_e`x'' if _n == `x'

	replace lb_w = `lb_w`x'' if _n == `x'
	replace ub_w = `ub_w`x'' if _n == `x'

	replace lb_g = `lb_g`x'' if _n == `x'
	replace ub_g = `ub_g`x'' if _n == `x'



}



twoway (scatter effects_e year, msize(large) mcolor(blue))  /*
*/(scatter effects_w year, msize(large) mcolor(red)) /*
*/(scatter effects_g year, msize(large) mcolor(black)) /*
*/ (rcap ub_e lb_e year, lwidth(medthick) lpattern(dash) lcolor(blue) ) /*
*/ (rcap ub_w lb_w year, lwidth(medthick) lpattern(dash) lcolor(red) ) /*
*/ (rcap ub_g lb_g year, lwidth(medthick) lpattern(dash) lcolor(black) ), /*
*/ ytitle("Impact on income (in $US/100)")  xtitle("Years from baseline")/*
*/ graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white))  /*
*/ scheme(s2mono) ylabel(, nogrid) yline(0, lpattern(dash) lcolor(black)) scale(1.2)

graph export "$results/hh_summary/components.pdf", as(pdf) replace

restore
