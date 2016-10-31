/*

This do-file computes the effect of this program on child development and academic achievement (year 5)

outcomes two-year

-teachers' reports: teacher expectations:  
-teachers' reports: mock reports cards: 
-teachers reports: SSRS academic subscale: 
-teachers' reports: classroom behavior scale: 

-individuals' aspirations and expectations: 

-parents' report: expectations: epi125 epi126
-parents' report, school achievement epi124a epi124b epi124c epi124d

-WOODCOCK-JOHNSON: ewjwscr1 ewjwscr2 ewjwscr4 Letter-Word Identification, Passage Comprehension, Applied Problems


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
/*Estimates from the youth database: year-8 results*/
*******************************************************

use "$databases/Youth_original2.dta", clear

*labels
do "$codes/data_youth.do"

keep  sampleid child p_assign zboy agechild /* identifiers
*/ ewjss22 ewjss25 ewjsstot /* Woodscok-Johnson
*/ epi124a epi124b epi124c epi124d /*  parents' report, school achievement
*/etsq12a etsq12b etsq12c etsq12d etsq12e etsq12f /* teachers' reports: mock cards
*/ etsq13a etsq13b etsq13c etsq13d etsq13e etsq13f etsq13g etsq13h etsq13i etsq13j /* teachers reports: SSRS academic subscale (a-j)
*/ bhvscaf3 trnscaf3 indscaf3 /* teachers' report: classroom behavior scale*/

*Don't have item "comprehension" in the WJ. Assume the overall measure is a simple av.
gen ewjss23=ewjsstot*3-ewjss22-ewjss25

/*Local labels: use these in regressions*/
local identifiers sampleid child p_assign zboy 
local WJ ewjss22 ewjss23 ewjss25
local parents_achievement epi124a epi124b epi124c epi124d
local teacher_mock etsq12a etsq12b etsq12c etsq12d etsq12e etsq12f
local teacher_ssrs etsq13a etsq13b etsq13c etsq13d etsq13e etsq13f etsq13g etsq13h etsq13i etsq13j
local teacher_class bhvscaf3 trnscaf3 indscaf3 


/*

/*Local labels: use these in tables*/
WJ_lbl: "WJ: Letter-Word" "WJ: Comprehension" "WJ: Applied problems"
teacher_mock: "Mock: Reading" "Mock: Oral language" "Mock: Written language" "Math" "Social studies" "Science"
teacher_ssrs: "SSRS: Overall" "SSRS: Reading" "SSRS: Math" "SSRS: Motivation" "SSRS: Parental encouragement" "SSRS: Intellectual functioning" "SSRS: Class behavior" "SSRS: Communication skills"
parents_achievement: "Parents: Reading" "Parents: Math" "Parents: Written work" "Parents: Overall"
teacher_class: "CBS: Behavior skills" "CBS: Transitional skills" "CBS: Independent skills" "CBS: Overall"


*/


*destring zboy `WJ' `parents_achievement' `parents_expectation' `teacher_expectation' `teacher_mock' `teacher_ssrs' /*
**/`teacher_class' `expectations' , force replace

if `controls'==1{

do "$codes/skills/Xs.do"


}


*Only those eligible to pre-primary education
*keep if agechild<=7

/*
Choose:
OLS=1: produces treatment effects tables using OLS estimates, "$results/Skills/skills_Y2_`sex'"
orprobit=1: produces treatment effects tables using an ordered probit: "$results/Skills/skills_Y2_probit_`sex'"

*/

local OLS=1
local orprobit=0

*********************************OLS estimates*****************************


gen RA=1 if p_assign=="E"
replace RA=2 if p_assign=="C"
label define ra_lbl 1 "Treatment" 2 "Control"
label values RA ra_lbl

if `OLS'==1{

*Standardize values: CBS, parents report, WJ, and mock reports
foreach variable of varlist `teacher_ssrs' `teacher_mock' `teacher_class' `parents_achievement' {
	egen `variable'_s=std(`variable')
	drop `variable'
	rename `variable'_s `variable'
}


*WJ: mean as a population equals 100, and SD=15. (check if these are the raw scores with mean close to 100)
foreach variable of varlist ewjss2*{
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
		mat A=(r(mu_1),r(mu_2),r(mu_1)-r(mu_2)\r(sd_1), r(sd_2), 0)
		

		xi: reg `variable' i.RA , vce(`SE')
		mat variance=e(V)
		mat A[2,3]=variance[1,1]^0.5/*replace it with S.E.*/
		test _IRA_2=0
		mat b_aux=(r(p)\0)
		mat D=A,b_aux/*add p-value*/
		*mat c_aux=(e(N)\0)
		*mat D=D,c_aux/*add N*/

		if `x'==1{
			mat baseline=D
		}
		else{
			mat baseline=baseline\D
		}
		local x=`x'+1
	}






	*the table
	putexcel B2=matrix(baseline) using "$results/Skills/skills_Y8_`sex'", sheet("data") modify
	local number=2
	foreach x in "WJ: Letter-Word" "WJ: Comprehension" "WJ: Applied problems" /* WJ
	*/ "SSRS: Overall" "SSRS: Reading" "SSRS: Math" "SSRS: Reading grade expectations" "SSRS: Math grade expectations" "SSRS: Motivation" "SSRS: Parental encouragement" /* SSRS
	*/ "SSRS: Intellectual functioning" "SSRS: Class behavior" "SSRS: Communication skills"/* SSRS
	*/"Mock: Reading" "Mock: Oral language" "Mock: Written language" "Mock: Math" "Mock: Social studies" "Mock: Science"/* Teachers' mock cards
	*/"CBS: Behavior skills" "CBS: Transitional skills" "CBS: Independent skills" /* CBS
	*/"Parents: Reading" "Parents: Math" "Parents: Written work" "Parents: Overall"/* Parents perceptions
	*/{
		putexcel A`number'=("`x'") using "$results/Skills/skills_Y8_`sex'", sheet("data") modify
		local number=`number'+2
	}
	putexcel B1=("Treatment") using "$results/Skills/skills_Y8_`sex'", sheet("data") modify
	putexcel C1=("Control") using "$results/Skills/skills_Y8_`sex'", sheet("data") modify
	putexcel D1=("T-C") using "$results/Skills/skills_Y8_`sex'", sheet("data") modify
	putexcel E1=("p-value") using "$results/Skills/skills_Y8_`sex'", sheet("data") modify
	*putexcel F1=("N") using "$results/Skills/skills_Y8_`sex'", sheet("data") modify

	
	local nn=`nn'+1
	
	restore


}


}




**************************************************
**************************************************
/*Probit estimates*/
**************************************************
**************************************************


if `orprobit'==1{

*Rounding: CBS, parents report, and mock reports
foreach variable of varlist epi124* etsq12* etsq13* bhvscaf3 trnscaf3 indscaf3    {
	gen `variable'_s=round(`variable')
	drop `variable'
	rename `variable'_s `variable'
}


*WJ: mean as a population equals 100, and SD=15. (check if these are the raw scores with mean close to 100)
foreach variable of varlist ewjss2*{
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
	foreach variable of varlist `WJ' {
		
		ttest `variable', by(RA)
		mat A=(r(mu_1),r(mu_2),r(mu_1)-r(mu_2)\r(sd_1), r(sd_2), 0)
		

		xi: reg `variable' i.p_assign , vce(`SE')
		mat variance=e(V)
		mat A[2,3]=variance[1,1]^0.5/*replace it with S.E.*/
		test _IRA_2=0
		mat b_aux=(r(p)\0)
		mat D=A,b_aux/*add p-value*/
		*mat c_aux=(e(N)\0)
		*mat D=D,c_aux/*add N*/

		if `x'==1{
			mat baseline=D
		}
		else{
			mat baseline=baseline\D
		}
		local x=`x'+1
	}

	
	foreach variable of varlist `teacher_ssrs' `teacher_mock' `teacher_class' `parents_achievement'{
		
		ttest `variable', by(RA)
		mat A=(r(mu_1),r(mu_2),0\r(sd_1), r(sd_2), 0)
		

		xi: oprobit `variable' i.p_assign , vce(robust)
		mat A[1,3]=_b[_Ip_assign_2] /*replace with \beta from oprobit*/
		mat A[2,3]=_se[_Ip_assign_2]/*replace it with S.E.*/
		test _Ip_assign_2=0
		mat b_aux=(r(p)\0)
		mat D=A,b_aux/*add p-value*/
		*mat c_aux=(e(N)\0)
		*mat D=D,c_aux/*add N*/

		mat baseline=baseline\D
		
	}




	*the table
	putexcel B2=matrix(baseline) using "$results/Skills/skills_Y8_probit_`sex'", sheet("data") modify
	local number=2
	foreach x in "WJ: Letter-Word" "WJ: Comprehension" "WJ: Applied problems" /* WJ
	*/ "SSRS: Overall" "SSRS: Reading" "SSRS: Math" "SSRS: Reading grade expectations" "SSRS: Math grade expectations" "SSRS: Motivation" "SSRS: Parental encouragement" /* SSRS
	*/ "SSRS: Intellectual functioning" "SSRS: Class behavior" "SSRS: Communication skills"/* SSRS
	*/"Mock: Reading" "Mock: Oral language" "Mock: Written language" "Mock: Math" "Mock: Social studies" "Mock: Science"/* Teachers' mock cards
	*/"CBS: Behavior skills" "CBS: Transitional skills" "CBS: Independent skills" /* CBS
	*/"Parents: Reading" "Parents: Math" "Parents: Written work" "Parents: Overall"/* Parents perceptions
	*/{
		putexcel A`number'=("`x'") using "$results/Skills/skills_Y8_probit_`sex'", sheet("data") modify
		local number=`number'+2
	}
	putexcel B1=("Treatment") using "$results/Skills/skills_Y8_probit_`sex'", sheet("data") modify
	putexcel C1=("Control") using "$results/Skills/skills_Y8_probit_`sex'", sheet("data") modify
	putexcel D1=("T-C") using "$results/Skills/skills_Y8_probit_`sex'", sheet("data") modify
	putexcel E1=("p-value") using "$results/Skills/skills_Y8_probit_`sex'", sheet("data") modify
	*putexcel F1=("N") using "$results/Skills/skills_Y8_probit_`sex'", sheet("data") modify

	
	local nn=`nn'+1
	
	restore


}


}


set more on
