/*
This do-file computes the effect of this program on child development and academic achievement (year 2)

outcomes two-year
-teachers' reports: social competence, compliance, autonomy, achievement, classroom behavior, discipline: I could only find
tcsbs tcsis tcsis tctot (see report year n2)
-aspirations and expectations: o97 o98 o99 o100
-parents' report: expectations: p112 p113

The regression:

y=alpha+\beta*RA+gamma*X

Where X's are controlled in "Xs.do". Change this code to modify control variables


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
set maxvar 15000
set more off

/*
Choose:
OLS=1: produces treatment effects tables using OLS estimates, "$results/Skills/skills_Y2_`sex'"
orprobit=1: produces treatment effects tables using an ordered probit: "$results/Skills/skills_Y2_probit_`sex'"

*/

local OLS=1
local orprobit=0


*******************************************************
/*Estimates from the youth database: year-2 results*/
*******************************************************

if `OLS'==1{

use "$databases/Youth_original2.dta", clear

*labels
qui: do "$codes/data_youth.do"
keep  sampleid child tcsbs tcsis tcsts tcstot tacad p_assign zboy agechild /*
*/ tq17* /*a-j: these are the 10 SSRS subcomponents*/

if `controls'==1{

do "$codes/skills/Xs.do"


}


*destring tcs* tacad zboy, force replace

*Only children who were preschoolers when they were in New Hope:
*keep if agechild<=7 /*two years after ra: 7 => they were up to 5 years old=> still eligible to pre-primary*/

gen RA=1 if p_assign=="E"
replace RA=2 if p_assign=="C"
label define ra_lbl 1 "Treatment" 2 "Control"
label values RA ra_lbl

*Standardize values: CBS

foreach variable of varlist tq17* tcsbs tcsis tcsts{
	egen `variable'_s=std(`variable')
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
	foreach variable of varlist tq17* tcsbs tcsis tcsts {
		
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
	putexcel F2=matrix(baseline) using "$results/Skills/skills_Y2_`sex'", sheet("data") modify
	local number=2
	foreach x in "SSRS: Overall" "SSRS: Reading" "SSRS: Math" "SSRS: Reading grade expectations" "SSRS: Math grade expectations"/* 
	*/ "SSRS: Motivation" "SSRS: Parental encouragement" "SSRS: Intellectual functioning" "SSRS: Classroom behavior" "SSRS: Communication skills"/*
	*/ "CBS: Behavior skills" "CBS: Independent skills" "CBS: Transitional skills" {
		putexcel A`number'=("`x'") using "$results/Skills/skills_Y2_`sex'", sheet("data") modify
		local number=`number'+2
	}
	putexcel F1=("Impact 2") using "$results/Skills/skills_Y2_`sex'", sheet("data") modify
	putexcel G1=("p-value") using "$results/Skills/skills_Y2_`sex'", sheet("data") modify

	
	local nn=`nn'+1
	
	restore


}


}

****************************************************************************
/*Probit estimates*/
****************************************************************************

if `orprobit'==1{

use "$databases/Youth_original2.dta", clear

*labels
do "$codes/data_youth.do"
keep  sampleid child tcsbs tcsis tcsts tcstot tacad p_assign zboy agechild /*
*/ tq17* /*a-j: these are the 10 SSRS subcomponents*/

*destring tcs* tacad zboy, force replace

destring sampleid, force replace
***************************************************************************
/*The X's*/


if `controls'==1{

do "$codes/skills/Xs.do"


}




*Only children who were preschoolers when they were in New Hope:
*keep if agechild<=7 /*two years after ra: 7 => they were up to 5 years old=> still eligible to pre-primary*/

gen RA=1 if p_assign=="E"
replace RA=2 if p_assign=="C"
label define ra_lbl 1 "Treatment" 2 "Control"
label values RA ra_lbl

*Rounding up variables to the nearest integer
foreach variable of varlist tcsbs tcsis tcsts {
	gen `variable'_s=round(`variable')
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
	foreach variable of varlist tq17* tcsbs tcsis tcsts {
		
		*ttest `variable', by(RA) 
		mat A=(0,0\0,0) /*treatment effect and p-values and N's*/
			

		xi: oprobit `variable' i.p_assign age_ra agechild i.marital i.ethnic d_HS higrade i.pastern2, vce(robust)
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
	putexcel F2=matrix(baseline) using "$results/Skills/skills_Y2_probit_`sex'", sheet("data") modify
	local number=2
	foreach x in "SSRS: Overall" "SSRS: Reading" "SSRS: Math" "SSRS: Reading grade expectations" "SSRS: Math grade expectations"/* 
	*/ "SSRS: Motivation" "SSRS: Parental encouragement" "SSRS: Intellectual functioning" "SSRS: Classroom behavior" "SSRS: Communication skills"/*
	*/ "CBS: Behavior skills" "CBS: Independent skills" "CBS: Transitional skills"  {
		putexcel A`number'=("`x'") using "$results/Skills/skills_Y2_probit_`sex'", sheet("data") modify
		local number=`number'+2
	}
	
	putexcel F1=("Impact 2") using "$results/Skills/skills_Y2_probit_`sex'", sheet("data") modify
	putexcel G1=("p-value") using "$results/Skills/skills_Y2_probit_`sex'", sheet("data") modify
	

	
	local nn=`nn'+1
	
	restore


}



}



/*
*Expectations: 9-12 years old
forvalues x=97/100{
	gen o`x'_cat=1 if o`x'==1 | o`x'==2
	replace o`x'_cat=0 if o`x'>=3 & o`x'<=5
	
}
label variable o97_cat "How sure: go to high school"
label variable o98_cat "How sure: finish high school"
label variable o99_cat "How sure: go to college"
label variable o100_cat "How sure: finish college"

label define exp_lbl 1 "Mostly/Very sure" 0 "Somewhat/Not really/Not at all sure"
label values o*_cat exp_lbl
*/
