/*
This do-file estimates the impact of New Hope on CC utilization

*/


global databases "/home/jrodriguez/NH-secure"
global codes "/home/jrodriguez/NH_HC/codes"
global results "/home/jrodriguez/NH_HC/results/hh_summary"

/*
robust SE for small samples. Set to hc3 for more conservatives. 

See Angrist and Pischke for more information
"robust" SE can be misleading when the sample size is small and there is no much heteroskedasticity.
*/
local SE="robust"



clear
clear matrix
clear mata
set more off
set maxvar 15000


*******************************************************
/*Estimation sample: children of women*/
*******************************************************

use "$databases/Youth_original2.dta", clear

*labels
qui: do "$codes/data_youth.do"
keep  sampleid child p_assign zboy agechild p_assign p_radaym sdkidbd



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


keep age_t0 sampleid child p_assign sdkidbd
reshape wide age_t0 sdkidbd, i(sampleid) j(child)

tempfile child_aux
save `child_aux', replace


*Merge data with adults and drop those who do not merge
use "$databases/CFS_original.dta", clear
qui: do "$codes/data_cfs.do"

qui: count
local n_cfs = r(N)

merge 1:1 sampleid using `child_aux'
keep if _merge == 3
drop _merge

qui: count
local n_cfs2 = r(N)

keep if gender == 2

reshape long age_t0 sdkidbd, i(sampleid) j(child)

keep sampleid child
tempfile data_est
save `data_est'

*******************************************************
/*Year-2 results */
*******************************************************
use "$databases/Youth_original2.dta", clear
keep sampleid child p_assign zboy child zboy curremp p_radaym sdkidbd/* identifiers
*/ c68* c69* c70* c73* /*CC use and payments from year 2*/

destring c68* c69* c70* c73* zboy, replace force

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



/*Local labels: use these in regressions*/
local CC_use c68* c69*

*destring `CC_use' agechild tcsbs tcsis tcsis tcstot tacad tq11b zboy,  replace force

*Categories of child care: last two years, regular CC
/*
Example: If parent reports having child A in CC & the child is Child A
*/

*CHild care: Head Start, Preschool, Nursery, or CC, extended day program, another CC other than someone's home
gen CC_HS_months=c70a_1 if c69a_2==child
replace CC_HS_months=c70a_2 if c69a_4==child

gen CC_PS_months=c70b_1 if c69b_2==child
replace CC_PS_months=c70b_2 if c69b_4==child

gen CC_ED_months=c70c_1 if c69c_2==child
replace CC_ED_months=c70c_2 if c69c_4==child

gen CC_OT_months=c70d_1 if c69d_2==child
replace CC_OT_months=c70d_2 if c69d_2==child

gen CC_PR_months=c70e_1 if c69e_2==child
replace CC_PR_months=c70e_2 if c69e_4==child

gen CC_HH_months=c70f_1 if c69f_2==child
replace CC_HH_months=c70f_1 if c69f_4==child

*number of months in formal
egen months_formal=rowtotal(CC_HS_months CC_PS_months CC_ED_months CC_OT_months)
egen months_informal=rowtotal(CC_PR_months CC_HH_months)
replace months_formal=. if c68a==. /*didn't answer survey*/
replace months_informal=. if c68a==.

*Main child care arragenment
egen max_months_t1=rowmax(CC_HS_months CC_PS_months CC_ED_months CC_OT_months CC_PR_months CC_HH_months)
gen d_CC2_t1=1 if max_months_t1==CC_HS_months | max_months_t1==CC_PS_months | max_months_t1==CC_ED_months | max_months_t1==CC_OT_months
replace d_CC2_t1=0 if  max_months_t1==CC_PR_months | max_months_t1==CC_HH_months | c68g==0
replace d_CC2_t1=. if max_months_t1==.

*Random assignment
gen RA=1 if p_assign=="E"
replace RA=2 if p_assign=="C"
label define ra_lbl 1 "Treatment" 2 "Control"
label values RA ra_lbl


*Gender
gen cat_gender = 1 if zboy == 0
replace cat_gender = 2 if zboy == 1

label define gender_lbl 1 "Girl" 2 "Boy"
label values cat_gender gender_lbl

merge 1:1 sampleid child using `data_est'

*This is the sample of children of women
keep if _merge == 3 | _merge == 2


/*CC use across age*/

forvalues x=1/3{ /*young, old, everybody*/
	preserve
	if `x'<=2 {
		keep if cat_gender==`x'
	}
	qui: sum d_CC2_t1 if p_assign=="C" & age_t0 <=4
	local mean_c_cat`x' = string(round(r(mean)*100,0.1),"%9.1f") 
	qui: sum d_CC2_t1 if p_assign=="E" & age_t0 <=4
	local mean_t_cat`x' = string(round(r(mean)*100,0.1),"%9.1f")
	
	qui xi: reg d_CC2_t1 i.p_assign if age_t0 <=4, vce(`SE')
	local effect_cat`x' = _b[_Ip_assign_2]
	local se_cat`x'  = _se[_Ip_assign_2]
	local lb_`x'=_b[_Ip_assign_2] - invttail(e(df_r),0.025)*_se[_Ip_assign_2]
	local ub_`x'=_b[_Ip_assign_2] + invttail(e(df_r),0.025)*_se[_Ip_assign_2]


	restore
}

************The graph*********************
clear
set obs 3 /*3 categories + 1 empyt*/
gen category = .
gen effects =.
gen lb =.
gen ub =.

local obs=1
forvalues category=1/3{
	replace category = `category' if _n ==`obs'
	replace effects = `effect_cat`category''*100 if _n == `obs'
	replace lb = `lb_`category''*100 if _n == `obs'
	replace ub = `ub_`category''*100 if _n == `obs'
	local obs=`obs' + 1
}


label define cat_lbl 1 "Girls" 2 "Boys" 3 "Overall"
label values category cat_lbl

twoway (scatter effects category, msize(large) mcolor(blue)) /*
*/ (rcap ub lb category, lwidth(medthick) lpattern(dash) lcolor(blue) ), /*
*/ ytitle("Impact on child care (in %)")  xtitle("") legend(off)/*
*/ xlabel( 1 "Girls" 2 "Boys" 3 "Overall", noticks) /*
*/ yscale(range(-10(20)60)) ylabel(0(20)60) xscale(range(0.5(1)3.5))/*
*/ graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white))  /*
*/ scheme(s2mono) ylabel(, nogrid) yline(0, lpattern(dash) lcolor(black)) scale(1.2)

graph export "$results/cc.pdf", as(pdf) replace


*This is baseline for everybody
display `mean_c_cat3'
