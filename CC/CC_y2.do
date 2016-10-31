/*
This do-file estimates the impact of New Hope on CC utilization

*/


global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results"

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
*/ c68* c69* c73* c71* /*CC use and payments
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

gen CC=1 if c68g==0 /*NO ARRANGEMENTS*/
replace CC=2 if (c68a==1 & c69a_2==child) | (c68a==1 & c69a_4==child) /*HEAD START*/
replace CC=3 if (c68b==1 & c69b_2==child) | (c68b==1 & c69b_4==child) /*Preschool, nursey, or CC other than Head Start*/
replace CC=4 if (c68c==1 & c69c_2==child) | (c68c==1 & c69c_4==child) | (c68c==1 & c69c_6==child) | (c68c==1 & c69c_8==child) /*Extended day program*/
replace CC=5 if (c68d==1 & c69d_2==child) | (c68d==1 & c69d_4==child) | (c68d==1 & c69d_6==child) /*Another CC other than someone's home*/
replace CC=6 if (c68e==1 & c69e_2==child) | (c68e==1 & c69e_4==child) | (c68e==1 & c69e_6==child) | (c68e==1 & c69e_6==child)/*
*/| (c68e==1 & c69e_6==child) /*Any person other than household member"*/
replace CC=7 if (c68f==1 & c69f_2==child) | (c68f==1 & c69f_4==child) | (c68f==1 & c69f_6==child) | (c68f==1 & c69f_6==child)/*
*/| (c68f==1 & c69f_6==child)/*Another household member*/

label define CC_lbl 1 "NO ARRANGEMENTS" 2 "HEAD START" 3 "Preschool, nursey, or CC other than Head Start" 4 "Extended day program"/*
*/ 5 "Another CC other than someone's home" 6 "Any person other than household member" 7 "Another household member"
label values CC CC_lbl


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
gen cat_age=1 if agechild<=7
replace cat_age=2 if agechild>7

label define ages_lbl 1 "Young" 2 "Old"
label values cat_age ages_lbl

*keep if zboy==1
*CHild care: Head Start, Preschool, Nursery, or CC, extended day program, another CC other than someone's home
gen d_CC=1 if CC==2 | CC==3 | CC==4 | CC==5
replace d_CC=0 if CC==1 | CC==6 | CC==7 /*no arrangements, a hh member, someone other than hh member*/



*log using "$results/CC_use.text", text replace
/*Type of care by age*/
*tab CC age



/*CC use in young children*/

*girls
xi: reg d_CC i.p_assign `control_var' if cat_age==2 & zboy==0, vce(`SE')
do "$codes/CC/reg_aux.do"
putexcel B3=matrix(results) using "$results/CC/CC", sheet("data") modify

xi: reg d_CC i.p_assign `control_var' if cat_age==1 & zboy==0, vce(`SE')
do "$codes/CC/reg_aux.do"
putexcel B6=matrix(results) using "$results/CC/CC", sheet("data") modify

xi: reg d_CC i.p_assign `control_var' if zboy==0, vce(`SE')
do "$codes/CC/reg_aux.do"
putexcel B9=matrix(results) using "$results/CC/CC", sheet("data") modify


*boys
xi: reg d_CC i.p_assign `control_var' if cat_age==2 & zboy==1, vce(`SE')
do "$codes/CC/reg_aux.do"
putexcel D3=matrix(results) using "$results/CC/CC", sheet("data") modify

xi: reg d_CC i.p_assign `control_var' if cat_age==1 & zboy==1, vce(`SE')
do "$codes/reg_aux.do"
putexcel D6=matrix(results) using "$results/CC/CC", sheet("data") modify

xi: reg d_CC i.p_assign `control_var' if zboy==1, vce(`SE')
do "$codes/reg_aux.do"
putexcel D9=matrix(results) using "$results/CC/CC", sheet("data") modify






*overall
xi: reg d_CC i.p_assign `control_var' if cat_age==2, vce(`SE')
do "$codes/reg_aux.do"
putexcel F3=matrix(results) using "$results/CC/CC", sheet("data") modify

xi: reg d_CC i.p_assign `control_var' if cat_age==1, vce(`SE')
do "$codes/CC/reg_aux.do"
putexcel F6=matrix(results) using "$results/CC/CC", sheet("data") modify

xi: reg d_CC i.p_assign `control_var', vce(`SE')
do "$codes/CC/reg_aux.do"
putexcel F9=matrix(results) using "$results/CC/CC", sheet("data") modify


*Table
putexcel A3=("Old (8-13 years old)") using "$results/CC/CC", sheet("data") modify
putexcel A6=("Young (0-7 years old)") using "$results/CC/CC", sheet("data") modify
putexcel A9=("Overall") using "$results/CC/CC", sheet("data") modify
putexcel B1=("Girls") using "$results/CC/CC", sheet("data") modify
putexcel D1=("Boys") using "$results/CC/CC", sheet("data") modify
putexcel F1=("Overall") using "$results/CC/CC", sheet("data") modify

*Display summary statistics on child care utilization
table p_assign, c(mean d_CC)
