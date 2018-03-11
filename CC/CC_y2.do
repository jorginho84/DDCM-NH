/*
This do-file estimates the impact of New Hope on CC utilization

*/


global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/CC"

/*
robust SE for small samples. Set to hc3 for more conservatives. 

See Angrist and Pischke for more information
"robust" SE can be misleading when the sample size is small and there is no much heteroskedasticity.
*/
local SE="hc2"


/*
controls: choose if regression should include controls for parents: age, ethnicity, marital status, and education.
*/

local controls=1



clear
clear matrix
clear mata
set more off
set maxvar 15000


*******************************************************
/*Year-2 results */
*******************************************************
use "$databases/Youth_original2.dta", clear
keep sampleid child p_assign zboy child agechild tcsbs tcsis tcsis tcstot tacad tq11b zboy curremp/* identifiers
*/ c68* c69* c70* c73* /*CC use and payments from year 2
*/tacad tcsbs tcsis tcsts tcstot  /*SSRS and CBS*/

*Recover control variables
if `controls'==1{

do "$codes/CC/Xs.do"

local control_var age_ra agechild i.marital i.ethnic d_HS higrade i.pastern2

}


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

*Standardize values: CBS

foreach variable of varlist tcsbs tcsis tcsts tcstot{
	egen `variable'_s=std(`variable')
	drop `variable'
	rename `variable'_s `variable'
}


*Age category
gen cat_age=1 if agechild<=6
replace cat_age=2 if agechild>6

label define ages_lbl 1 "Young" 2 "Old"
label values cat_age ages_lbl



/*CC use across age*/

forvalues x=1/3{ /*young, old, everybody*/
	preserve
	if `x'<=2 {
		keep if cat_age==`x'
	}
	qui: sum d_CC2_t1 if p_assign=="C" 
	local mean_c_cat`x' = string(round(r(mean)*100,0.1),"%9.1f") 
	qui: sum d_CC2_t1 if p_assign=="E" 
	local mean_t_cat`x' = string(round(r(mean)*100,0.1),"%9.1f")
	
	qui xi: reg d_CC2_t1 i.p_assign , vce(`SE')
	local effect_model1_cat`x'  =string(round(_b[_Ip_assign_2]*100,0.1),"%9.1f")
	local se_model1_cat`x'  = string(round(_se[_Ip_assign_2]*100,0.1),"%9.1f")
	qui: test _Ip_assign_2=0
	scalar define pvalue_model1_cat`x' = r(p)

	

	qui xi: reg d_CC2_t1 i.p_assign `control_var', vce(`SE')
	local effect_model2_cat`x'  =string(round(_b[_Ip_assign_2]*100,0.1),"%9.1f")
	local se_model2_cat`x'  = string(round(_se[_Ip_assign_2]*100,0.1),"%9.1f")
	qui: test _Ip_assign_2=0
	scalar define pvalue_model2_cat`x' = r(p)

	forvalues mm=1/2{
		if pvalue_model`mm'_cat`x'<=0.01{
			local pval_model`mm'_cat`x' "***"
		}
		else if pvalue_model`mm'_cat`x'>0.01 & pvalue_model`mm'_cat`x'<=0.05{
			local pval_model`mm'_cat`x' "**"

		}
		else if pvalue_model`mm'_cat`x'>0.05 & pvalue_model`mm'_cat`x'<=0.1{
			local pval_model`mm'_cat`x' "*"

		}
		else{
			local pval_model`mm'_cat`x' ""
		}
	}
	restore
}


/*The Table*/
file open cc_table using "$results/cc_table.tex", write replace
file write cc_table "\begin{tabular}{llccccccc}"_n
file write cc_table "\hline"_n
file write cc_table "Sample && Control && Treatment && Model 1 && Model 2 \bigstrut\\"_n
file write cc_table "\cline{1-1}\cline{3-9}"_n

file write cc_table "Young (0-6 years old) && `mean_c_cat1' && `mean_t_cat1'  && `effect_model1_cat1'`pval_model1_cat1' && `effect_model2_cat1'`pval_model2_cat1' \\"_n
file write cc_table "&&&&       &       & (`se_model1_cat1') &       & (`se_model2_cat1') \\"_n
file write cc_table "&&&&&&& &  \\"_n

file write cc_table "Old ($>$6 years old) && `mean_c_cat2' && `mean_t_cat2'  && `effect_model1_cat2'`pval_model1_cat2' && `effect_model2_cat2'`pval_model2_cat2' \\"_n
file write cc_table "&&&&       &       & (`se_model1_cat2') &       & (`se_model2_cat2') \\"_n
file write cc_table "&&&&&&& &  \\"_n

file write cc_table "Overall && `mean_c_cat3' && `mean_t_cat3'  && `effect_model1_cat3'`pval_model1_cat3' && `effect_model2_cat3'`pval_model2_cat3' \\"_n
file write cc_table "&&&&       &       & (`se_model1_cat3') &       & (`se_model2_cat3') \\"_n
file write cc_table "\hline"_n
file write cc_table "\end{tabular}"_n
file close cc_table


/*The Table v2*/
file open cc_table using "$results/cc_table_v2.tex", write replace
file write cc_table "\begin{tabular}{llccccc}"_n
file write cc_table "\hline"_n
file write cc_table "Sample && Control && Treatment && Impact \bigstrut\\"_n
file write cc_table "\cline{1-1}\cline{3-7}"_n

file write cc_table "Young (0-6 years old) && `mean_c_cat1' && `mean_t_cat1'  && `effect_model1_cat1'`pval_model1_cat1'  \\"_n
file write cc_table "&&&&       &       & (`se_model1_cat1')  \\"_n
file write cc_table "&&&&&& \\"_n

file write cc_table "Old ($>$6 years old) && `mean_c_cat2' && `mean_t_cat2'  && `effect_model1_cat2'`pval_model1_cat2' \\"_n
file write cc_table "&&&&       &       & (`se_model1_cat2')  \\"_n
file write cc_table "&&&&&&  \\"_n

file write cc_table "Overall && `mean_c_cat3' && `mean_t_cat3'  && `effect_model1_cat3'`pval_model1_cat3' \\"_n
file write cc_table "&&&&       &       & (`se_model1_cat3')  \\"_n
file write cc_table "\hline"_n
file write cc_table "\end{tabular}"_n
file close cc_table


