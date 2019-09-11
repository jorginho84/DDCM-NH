/*

This do-file computes the impact of New Hope on income, labor supply,
and child care

*/

global databases "/home/jrodriguez/NH-secure"
global codes "/home/jrodriguez/NH_HC/codes"
global results "/home/jrodriguez/NH_HC/results"


local SE="hc2"

clear
clear matrix
clear mata
set more off
set maxvar 15000


*******************************************************
*******************************************************
/*Recovering child's age*/

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


keep age_t0 sampleid child
reshape wide age_t0, i(sampleid) j(child)

tempfile child_aux
save `child_aux', replace


*****************************************************************
*****************************************************************
/*INCOME EFFECTS*/
*****************************************************************
*****************************************************************


use "$results/income/data_income.dta", clear


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

}




*Dropping 50 adults with no information on their children
count
qui: do "$codes/income/drop_50.do"
count

*Control variables (and recovering p_assign)
qui: do "$codes/income/Xs.do"
local control_var age_ra i.marital i.ethnic d_HS2 higrade i.pastern2

tempfile data_income
save `data_income', replace

gen d_ra= 1 if p_assign == "E"
replace d_ra = 0 if p_assign == "C" 


*stop!!
*Treatment

*randcmd ((d_ra) reg total_income_y3 d_ra), treatvars(d_ra) sample
*randcmd ((d_ra) reg gross_y0 d_ra), treatvars(d_ra) sample

merge 1:1 sampleid using `child_aux'
drop _merge

*age of youngest
egen age_y = rowmin(age_t0*)



keep total_income_y* gross_y* sampleid d_ra p_assign emp_baseline age_ra marital ethnic d_HS2 higrade pastern2 age_y
reshape long total_income_y gross_y, i(sampleid) j(year)

randcmd ((d_ra) reg total_income_y d_ra if year<=2 & age_y<=4), treatvars(d_ra) sample
randcmd ((d_ra) reg gross_y d_ra if year<=2 & age_y<=4), treatvars(d_ra) sample

randcmd ((d_ra) reg total_income_y d_ra if year>2 & age_y<=4), treatvars(d_ra) sample
randcmd ((d_ra) reg gross_y d_ra if year==0 & age_y<=4), treatvars(d_ra) sample


randcmd ((d_ra) reg total_income_y d_ra if year>2 & year<=5), treatvars(d_ra) sample

randcmd ((d_ra) reg total_income_y d_ra if year>2), treatvars(d_ra) sample

stop!
qui xi: reg total_income_y i.p_assign, vce(`SE')
local base_income = string(round(_b[_cons]),"%9.0gc")
local beta_income = string(round(_b[_Ip_assign_2]),"%9.0f")
local se_income = string(round(_se[_Ip_assign_2]),"%9.0f")
qui: test _Ip_assign_2=0
local pval_income = r(p)




*****************************************************************
*****************************************************************
/*Labor supply effects*/
*****************************************************************
*****************************************************************
*Effects on quarterly employment

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
		local m=`m'+1
	}
	
} 


*Quarters

forvalues y=1994/1997{

	local m1=1
	forvalues q=1/4{
		local m2=`m1'+1
		local m3=`m2'+1
		egen csj`y'q`q'=rowtotal(csj`y'm`m1' csj`y'm`m2' csj`y'm`m3')
		local m1=`m3'+1
	}

}

****************************************
*UI Earnings: quarters in calendar time
****************************************



*Renaming 
rename ern4q93 ern1993q4

local nn=1
forvalues y=94/99{
	forvalues q=1/4{

		rename ern`q'q`y' ern19`y'q`q'
		
	}
}

local yy=0
forvalues y=2000/2003{
	forvalues q=1/4{

		rename ern`q'q0`yy' ern200`yy'q`q' 
				
	}

local yy=`yy'+1
}

*I DON"T HAVE EARNINGS FOR 98Q1: leave them as missing.
destring ern1998q1, replace force

*****************************************
*NH supplement: quarters in calendar time
*****************************************
destring sup*q*, replace force

*Renaming 
local nn=1
forvalues y=94/99{
	forvalues q=1/4{
		
		replace sup`y'q`q'=0 if sup`y'q`q'==.
		rename sup`y'q`q' sup19`y'q`q'
		
	}
}


forvalues q=1/4{
	replace sup00q`q'=0 if sup00q`q'==.
	rename sup00q`q' sup2000q`q' 
				
}

****Employment (quarter) ****

forvalues y=1994/2003{
	forvalues q=1/4{
	
		if `y'<=1997{
			gen emp`y'q`q'=(ern`y'q`q'!=. & ern`y'q`q'>0) | (csj`y'q`q'!=. & csj`y'q`q'>0) 
		}
		else{
			gen emp`y'q`q'=(ern`y'q`q'!=. & ern`y'q`q'>0)
		}
	
	}

}


*Quarter of RA
replace p_radatr=p_radatr+19000000
tostring p_radatr, force replace
gen ra_quarter=qofd(date(p_radatr,"YMD"))
format ra_quarter %tq


*Reshaping to build a panel
keep emp* sampleid ra_quarter p_assign
reshape long emp, i(sampleid) j(quarter_aux) string
gen quarter=quarterly(quarter_aux, "YQ")
format quarter %tq


*Quarters since RA
gen quarters_ra=quarter-ra_quarter

*Effects for t=0,1,2 years (12 quarters after RA)
xi: reg emp i.p_assign if quarters_ra>=0 & quarters_ra<=11, vce(`SE')
local base_emp = string(round(_b[_cons]*100,0.1),"%9.1f")
local beta_emp = string(round(_b[_Ip_assign_2]*100,0.1),"%9.1f")
local se_emp = string(round(_se[_Ip_assign_2]*100,0.1),"%9.1f")
qui: test _Ip_assign_2=0
local pval_emp = r(p)

*****************************************************************
*****************************************************************
/*Child care effects*/
*****************************************************************
*****************************************************************

use "$databases/Youth_original2.dta", clear
keep sampleid child p_assign zboy child agechild tcsbs tcsis tcsis tcstot tacad tq11b zboy curremp/* identifiers
*/ c68* c69* c70* c73* /*CC use and payments from year 2
*/ piq114aa  piq114ba piq114ca piq114da piq114ea piq114fa piq114ga /* CC year 5
*/tacad tcsbs tcsis tcsts tcstot  /*SSRS and CBS*/

*Recover control variables
do "$codes/CC/Xs.do"

local control_var age_ra agechild i.marital i.ethnic d_HS higrade i.pastern2



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

*Number of months in child care at t=4
egen max_months_t4=rowmax(piq114aa  piq114ba piq114ca piq114da piq114ea piq114fa piq114ga)
gen d_CC2_t4=1 if max_months_t4==piq114da
replace d_CC2_t4=0 if  max_months_t4==piq114aa | max_months_t4==piq114ba | max_months_t4==piq114ca | max_months_t4==piq114ea | max_months_t4==piq114fa | max_months_t4==piq114ga
replace d_CC2_t4=. if max_months_t4==.

*Age category
gen cat_age=1 if agechild<=6
replace cat_age=2 if agechild>6

label define ages_lbl 1 "Young" 2 "Old"
label values cat_age ages_lbl


xi: reg d_CC2_t1 i.p_assign if cat_age==1, vce(`SE')
local base_cc = string(round(_b[_cons]*100,0.1),"%9.1f")
local beta_cc = string(round(_b[_Ip_assign_2]*100,0.1),"%9.1f")
local se_cc = string(round(_se[_Ip_assign_2]*100,0.1),"%9.1f")
qui: test _Ip_assign_2=0
local pval_cc = r(p)


*****************************************************************
*****************************************************************
/*THE TABLE*/
*****************************************************************
*****************************************************************

*Defining pvalues
foreach variable in "income" "emp" "cc"{
	if `pval_`variable''<=0.01{
		local pval_`variable'_2 "***"
	}
	else if `pval_`variable''>0.01 & `pval_`variable''<=0.05{
		local pval_`variable'_2 "**"
	}
	else if `pval_`variable''>0.05 & `pval_`variable''<=0.1{
		local pval_`variable'_2 "*"
	}
	else{
		local pval_`variable'_2 ""
	}
}

file open hh_table using "$results/HH_summary/hh_table.tex", write replace
file write hh_table "\begin{tabular}{lccccc}"_n
file write hh_table "\hline"_n
file write hh_table "\multicolumn{1}{c}{\multirow{2}[2]{*}{Household variable}} "
file write hh_table "&& \multicolumn{2}{c}{Estimated} && \multirow{2}[2]{*}{MDRC report}"
file write hh_table " \bigstrut[t]\\"_n
file write hh_table "&& Baseline & Effect &&  \bigstrut[b]\\"_n
file write hh_table "\cline{1-1}\cline{3-4}\cline{6-6}\\"_n
file write hh_table "\multicolumn{1}{l}{Income (US dollars)} && `base_income'  & `beta_income'`pval_income_2' && 1,016*** \bigstrut[t]\\"_n
file write hh_table "      &       &       & (`se_income') &       &  \\"_n
file write hh_table "      &       &       &       &       &  \\"_n
file write hh_table "\multicolumn{1}{l}{Labor supply (\%)} && `base_emp'  & `beta_emp'`pval_emp_2' && 5.5*** \bigstrut[t]\\"_n
file write hh_table "      &       &       & (`se_emp') &       &  \\"_n
file write hh_table "      &       &       &       &       &  \\"_n
file write hh_table "\multicolumn{1}{l}{Formal child care (\%)} && `base_cc'  & `beta_cc'`pval_cc_2' && 10.0*** \bigstrut[t]\\"_n
file write hh_table "      &       &       & (`se_cc') &       &  \\"_n
file write hh_table "\hline"_n
file write hh_table "\end{tabular}"_n
file close hh_table



