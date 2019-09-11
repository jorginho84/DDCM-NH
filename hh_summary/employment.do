/*
This do-file computes treatment effects on employment

*/


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

/*Employment data*/
qui: do "$codes/hh_summary/data_emp.do"

merge 1:1 sampleid using `child_aux'
keep if _merge == 3
drop _merge



*age of youngest
egen age_y = rowmin(age_t0*)

gen d_ra= 1 if p_assign == "E"
replace d_ra = 0 if p_assign == "C" 

keep if gender == 2

*baseline
preserve
keep emp* sampleid d_ra* age_y
reshape long emp, i(sampleid) j(quarter)

qui: sum emp if d_ra == 0 & quarter>=9 & quarter<41 & age_y<=4
local mean_baseline = r(mean)

qui: reg emp d_ra if quarter>=9 & quarter<41 & age_y<=4
local mean_effect = _b[d_ra]


restore


forvalues x=0/45{
	qui: reg emp`x' d_ra if age_y<=4, vce("robust")
	local beta_y`x' = _b[d_ra]
	local lb_y`x'=_b[d_ra] - invttail(e(df_r),0.025)*_se[d_ra]
	local ub_y`x'=_b[d_ra] + invttail(e(df_r),0.025)*_se[d_ra]

	qui: reg emp`x' d_ra if age_y>4, vce("robust")
	local beta_o`x' = _b[d_ra]
	local lb_o`x'=_b[d_ra] - invttail(e(df_r),0.025)*_se[d_ra]
	local ub_o`x'=_b[d_ra] + invttail(e(df_r),0.025)*_se[d_ra]
}




clear

set obs 46
gen effects_y = .
gen effects_o = .
gen lb_y = .
gen ub_y = .
gen lb_o = .
gen ub_o = .
gen year = .



forvalues x=1/46{
	local y = `x' - 1
	replace effects_y = `beta_y`y''*100 if _n == `x'
	replace lb_y = `lb_y`y''*100 if _n == `x'
	replace ub_y = `ub_y`y''*100 if _n == `x'

	replace effects_o = `beta_o`y''*100 if _n == `x'
	replace lb_o = `lb_o`y''*100 if _n == `x'
	replace ub_o = `ub_o`y''*100 if _n == `x'

	replace year = `x' - 1 - 8 if _n == `x'
}




twoway (connected effects_y year if year<32 & year >=0, msize(small) mcolor(blue) lcolor(blue))  /*
*/(line ub_y year if year<32 & year >=0, lpattern(dash) lwidth(thin) lcolor(black) ) /*
*/(line lb_y year if year<32 & year >=0, lpattern(dash) lwidth(thin) lcolor(black) ), /*
*/ ytitle("Impact on employment (in %)")  xtitle("Quarters from baseline") legend(off)/*
*/ graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white))  /*
*/ scheme(s2mono) ylabel(, nogrid) ylabel(-30(10)30) xline(12, lcolor(red)) yline(0, lpattern(dash) lcolor(black)) scale(1.2)
graph export "$results/hh_summary/employment_y.pdf", as(pdf) replace


twoway (connected effects_o year if year<32 & year >=0, msize(small) mcolor(blue) lcolor(blue))  /*
*/(line ub_o year if year<32 & year >=0, lpattern(dash) lwidth(thin) lcolor(black) ) /*
*/(line lb_o year if year<32 & year >=0,lpattern(dash) lwidth(thin) lcolor(black) ), /*
*/ ytitle("Impact on employment (in %)")  xtitle("Quarters from baseline") legend(off)/*
*/ graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white))  /*
*/ scheme(s2mono) ylabel(, nogrid) ylabel(-30(10)30) xline(12, lcolor(red)) yline(0, lpattern(dash) lcolor(black)) scale(1.2)

graph export "$results/hh_summary/employment_o.pdf", as(pdf) replace

*This is mean of baseline
display `mean_baseline'

*This is mean effect while New Hope ran
display `mean_effect'

