/*
This do-file computes the effect of this program on child development and academic achievement (year 5)

outcomes two-year
-teachers' reports: teacher expectations: t2q11a t2q11b t2q11c 
-teachers' reports: mock reports cards: t2q16a t2q16b t2q16c t2q16d t2q16e t2q16f
-teachers reports: SSRS academic subscale: t2q17a-t2q17j
-teachers' reports: classroom behavior scale: bhvscaf2 trnscaf2 indscaf2

-individuals' aspirations and expectations: yiq45a-c and yaq46c-yaq46d (about the future)

-parents' report: expectations: piq147 piq148
-parents' report, school achievement piq146a piq146b piq146c piq146d 

-WOODCOCK-JOHNSON: wjss22-wjss25 (corresponding to letter-word, comprehension, calculation and applied problems).


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
Choose:
OLS=1: produces treatment effects tables using OLS estimates, "$results/Skills/skills_Y2_`sex'"
orprobit=1: produces treatment effects tables using an ordered probit: "$results/Skills/skills_Y2_probit_`sex'"

*/

local OLS=1
local orprobit=0

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
/*Estimates from the youth database: year-2 results*/
*******************************************************

use "$databases/Youth_original2.dta", clear

*labels
do "$codes/data_youth.do"

keep  sampleid child p_assign zboy agechild /* identifiers
*/ wjss22 wjss23 wjss24 wjss25 /* Woodscok-Johnson
*/ piq146a piq146b piq146c piq146d /*  parents' report, school achievement
*/ piq147 piq148 /* Parents report: expectations
*/ t2q11a t2q11b t2q11c /* Teachers report: expectations
*/ t2q16a t2q16b t2q16c t2q16d t2q16e t2q16f /* teachers' reports: mock cards
*/ t2q17a t2q17b t2q17c t2q17d t2q17e t2q17f t2q17g t2q17h t2q17i t2q17j /* teachers reports: SSRS academic subscale (a-j)
*/ bhvscaf2 trnscaf2 indscaf2 clascaf2 /* teachers' report: classroom behavior scale
*/ yiq45* /* individuals expectations (a-c)
*/

/*Local labels: use these in regressions*/
local identifiers sampleid child p_assign zboy 
local WJ wjss22 wjss23 wjss24 wjss25
local parents_achievement piq146a piq146b piq146c piq146d
local parents_expectation piq147 piq148
local teacher_expectation t2q11a t2q11b t2q11c
local teacher_mock t2q16a t2q16b t2q16c t2q16d t2q16e t2q16f
local teacher_ssrs t2q17*
local teacher_class bhvscaf2 trnscaf2 indscaf2 
local expectations yiq45*

/*

/*Local labels: use these in tables*/
WJ_lbl: "WJ: Letter-Word" "WJ: Comprehension" "WJ: Calculation" "WJ: Applied problems"
parents_achievement: "Parents: Reading" "Parents: Math" "Parents: Written work" "Parents: Overall"
teacher_mock: "Mock: Reading" "Mock: Oral language" "Mock: Written language" "Math" "Social studies" "Science"
teacher_ssrs: "SSRS: Overall" "SSRS: Reading" "SSRS: Math" "SSRS: Motivation" "SSRS: Parental encouragement" "SSRS: Intellectual functioning" "SSRS: Class behavior" "SSRS: Communication skills"
teacher_class: "CBS: Behavior skills" "CBS: Transitional skills" "CBS: Independent skills" "CBS: Overal"
expectations:

*/

*destring zboy `WJ' `parents_achievement' `parents_expectation' `teacher_expectation' `teacher_mock' `teacher_ssrs' /*
**/`teacher_class' `expectations' , force replace


if `controls'==1{

do "$codes/skills/Xs.do"


}

*Only children who were preschoolers when they were in New Hope
*keep if agechild<=7

gen RA=1 if p_assign=="E"
replace RA=2 if p_assign=="C"
label define ra_lbl 1 "Treatment" 2 "Control"
label values RA ra_lbl

*********************OLS estimates******************************



if `OLS'==1{

*Standardize values: CBS, parents report, WJ, and mock reports
foreach variable of varlist `teacher_ssrs' `teacher_mock' `teacher_class' `parents_achievement' {
	egen `variable'_s=std(`variable')
	drop `variable'
	rename `variable'_s `variable'
}

*WJ: mean as a population equals 100, and SD=15.
foreach variable of varlist wjss*{
	gen `variable'_st=(`variable'-100)/15
	drop `variable'
	rename `variable'_s `variable'
}



*Regressions and tables: overall, girls, and then boys.
local nn=0
foreach sex in "Overall" "Girls" "Boys"{

	preserve
	
	if `nn'==1{
		keep if zboy==0
	}
	else if `nn'==2{
		keep if zboy==1
	}

	local x=1
	foreach variable of varlist `WJ' `teacher_ssrs' `teacher_mock' `teacher_class' `parents_achievement'{
		
		ttest `variable', by(RA)
		mat A=(0,0\0,0) /*treatment effect and p-values and N's*/
			

		xi: reg `variable' i.p_assign age_ra agechild i.marital i.ethnic d_HS higrade i.pastern2, vce(`SE')
		mat A[1,1]=_b[_Ip_assign_2] /*replace with \beta from oprobit*/
		mat A[2,1]=_se[_Ip_assign_2]/*replace it with S.E.*/
		test _Ip_assign_2=0
		mat A[1,2]=r(p) /*add p-value*/
		mat A[2,2]=e(N) /*add N*/

		if `x'==1{
			mat baseline=A
		}
		else{
			mat baseline=baseline\A
		}
		local x=`x'+1
	}


	*the table
	putexcel F2=matrix(baseline) using "$results/Skills/skills_Y5_`sex'", sheet("data") modify
	local number=2
	foreach x in "WJ: Letter-Word" "WJ: Comprehension" "WJ: Calculation" "WJ: Applied problems" /* WJ
	*/ "SSRS: Overall" "SSRS: Reading" "SSRS: Math" "SSRS: Reading grade expectations" "SSRS: Math grade expectations" "SSRS: Motivation" "SSRS: Parental encouragement" /* SSRS
	*/ "SSRS: Intellectual functioning" "SSRS: Class behavior" "SSRS: Communication skills"/* SSRS
	*/"Mock: Reading" "Mock: Oral language" "Mock: Written language" "Mock: Math" "Mock: Social studies" "Mock: Science"/* Teachers' mock cards
	*/"CBS: Behavior skills" "CBS: Transitional skills" "CBS: Independent skills"  /* CBS
	*/"Parents: Reading" "Parents: Math" "Parents: Written work" "Parents: Overall"/* Parents perceptions
	*/{
		putexcel A`number'=("`x'") using "$results/Skills/skills_Y5_`sex'", sheet("data") modify
		local number=`number'+2
	}
	putexcel F1=("Impact 2") using "$results/Skills/skills_Y5_probit_`sex'", sheet("data") modify
	putexcel G1=("p-value") using "$results/Skills/skills_Y5_probit_`sex'", sheet("data") modify

	
	local nn=`nn'+1
	
	restore


}

}



**********************************************************************************************************
**********************************************************************************************************
/*
Probit estimates
*/
**********************************************************************************************************
**********************************************************************************************************





if `orprobit'==1{

*Standardize values: CBS, parents report, and mock reports
foreach variable of varlist piq146* t2q16* t2q17*  bhvscaf2 trnscaf2 indscaf2   {
	gen `variable'_s=round(`variable')
	drop `variable'
	rename `variable'_s `variable'
}

*WJ: mean as a population equals 100, and SD=15.
foreach variable of varlist wjss*{
	gen `variable'_st=(`variable'-100)/15
	drop `variable'
	rename `variable'_s `variable'
}

*Regressions and tables: overall, girls, and then boys.
local nn=0
foreach sex in "Overall" "Girls" "Boys"{

	preserve
	
	if `nn'==1{
		keep if zboy==0
	}
	else if `nn'==2{
		keep if zboy==1
	}

	
	*WJ is continuous
	local x=1
	foreach variable of varlist `WJ'{
		
		*ttest `variable', by(RA)
		mat A=(0,0\0,0) /*treatment effect and p-values and N's*/
			

		xi: reg `variable' i.p_assign age_ra agechild i.marital i.ethnic d_HS higrade i.pastern2, vce(`SE')
		mat A[1,1]=_b[_Ip_assign_2] /*replace with \beta from oprobit*/
		mat A[2,1]=_se[_Ip_assign_2]/*replace it with S.E.*/
		test _Ip_assign_2=0
		mat A[1,2]=r(p) /*add p-value*/
		mat A[2,2]=e(N) /*add N*/

		if `x'==1{
			mat baseline=A
		}
		else{
			mat baseline=baseline\A
		}
		local x=`x'+1
	}
	
	
	local x=1
	foreach variable of varlist `teacher_ssrs' `teacher_mock' `teacher_class' `parents_achievement'{
		
		ttest `variable', by(RA)
		mat A=(0,0\0,0) /*treatment effect and p-values and N's*/
			

		xi: oprobit `variable' i.p_assign age_ra agechild i.marital i.ethnic d_HS higrade i.pastern2, vce(robust)
		mat A[1,1]=_b[_Ip_assign_2] /*replace with \beta from oprobit*/
		mat A[2,1]=_se[_Ip_assign_2]/*replace it with S.E.*/
		test _Ip_assign_2=0
		mat A[1,2]=r(p) /*add p-value*/
		mat A[2,2]=e(N) /*add N*/

		mat baseline=baseline\A
	}


	*the table
	putexcel F2=matrix(baseline) using "$results/Skills/skills_Y5_probit_`sex'", sheet("data") modify
	local number=2
	foreach x in "WJ: Letter-Word" "WJ: Comprehension" "WJ: Calculation" "WJ: Applied problems" /* WJ
	*/ "SSRS: Overall" "SSRS: Reading" "SSRS: Math" "SSRS: Reading grade expectations" "SSRS: Math grade expectations" "SSRS: Motivation" "SSRS: Parental encouragement" /* SSRS
	*/ "SSRS: Intellectual functioning" "SSRS: Class behavior" "SSRS: Communication skills"/* SSRS
	*/"Mock: Reading" "Mock: Oral language" "Mock: Written language" "Mock: Math" "Mock: Social studies" "Mock: Science"/* Teachers' mock cards
	*/"CBS: Behavior skills" "CBS: Transitional skills" "CBS: Independent skills" /* CBS
	*/"Parents: Reading" "Parents: Math" "Parents: Written work" "Parents: Overall"/* Parents perceptions
	*/{
		putexcel A`number'=("`x'") using "$results/Skills/skills_Y5_probit_`sex'", sheet("data") modify
		local number=`number'+2
	}
	putexcel F1=("Impact 2") using "$results/Skills/skills_Y5_probit_`sex'", sheet("data") modify
	putexcel G1=("p-value") using "$results/Skills/skills_Y5_probit_`sex'", sheet("data") modify

	
	local nn=`nn'+1
	
	restore


}

}

set more on
