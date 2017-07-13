/*

This do-file computes the impact of New Hope on income, labor supply,
and child care

*/

global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results"


local SE="hc2"

clear
clear matrix
clear mata
set more off
set maxvar 15000



*****************************************************************
*****************************************************************
/*INCOME EFFECTS*/
*****************************************************************
*****************************************************************


use "$results/Income/data_income.dta", clear


drop total_income_y0 gross_y0 gross_nominal_y0 grossv2_y0 employment_y0 /*
*/ fs_y0 afdc_y0 sup_y0 eitc_state_y0 eitc_fed_y0
forvalues x=1/3{
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

*Many missing obs
drop total_income_y10


*Dropping 50 adults with no information on their children
count
qui: do "$codes/income/drop_50.do"
count

*Control variables (and recovering p_assign)
qui: do "$codes/income/Xs.do"
local control_var age_ra i.marital i.ethnic d_HS2 higrade i.pastern2

tempfile data_income
save `data_income', replace

keep total_income_y* sampleid p_assign emp_baseline age_ra marital ethnic d_HS2 higrade pastern2
reshape long total_income_y, i(sampleid) j(year)

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
use `data_income', clear

*positive earnings
forvalues x=0/2{
	gen emp_y`x' = gross_y`x'>0
}


keep emp_y* sampleid p_assign emp_baseline age_ra marital ethnic d_HS2 higrade pastern2
reshape long emp_y, i(sampleid) j(year)

qui xi: reg emp_y i.p_assign, vce(`SE')
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



