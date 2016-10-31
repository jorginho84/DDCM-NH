/*
This do-file computes the effect of this program on child development and academic achievement (year 2)

outcomes two-year
-teachers' reports: social competence, compliance, autonomy, achievement, classroom behavior, discipline: I could only find
tcsbs tcsis tcsis tctot (see report year n2)
-aspirations and expectations: o97 o98 o99 o100
-parents' report: expectations: p112 p113

THIS CODE RESTRICTS THE SAMPLE TO CHILDREN WHERE THE PARTICIPANT IS THE WOMEN.
THERE ARE NO DIFFERENCES IN THE RESULTS.


*/


global databases "/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases"
global codes "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes"
global results "/mnt/Research/nealresearch/new-hope-secure/newhopemount/results"

/*
robust SE for small samples. Set to hc3 for more conservatives. 

See Angrist and Pischke for more information
"robust" SE can be misleading when the sample size is small and there is no much heteroskedasticity.
*/
global SE "hc2"


clear
clear matrix
clear mata
set maxvar 15000
set more off

*******************************************************
/*Estimates from the youth database: year-2 results*/
*******************************************************


*Recovering sex of participant
use "$databases/CFS_original.dta", clear
do "$codes/data_cfs.do"
keep sampleid gender
sort sampleid

tempfile data_1
save `data_1', replace


use "$databases/Youth_original2.dta", clear

*labels
do "$codes/data_youth.do"
keep  sampleid child tcsbs tcsis tcsts tcstot tacad p_assign zboy agechild

destring sampleid, force replace

sort sampleid

*recover gender and estimate only on women
merge m:1 sampleid using `data_1'
keep if _merge==3 /*I lose 53 obs here*/
keep if gender==2 /*only women*/


*destring tcs* tacad zboy, force replace
*Only children who were preschoolers when they were in New Hope
*keep if agechild<=8 & agechild>=5

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
	foreach variable of varlist tacad tcsbs tcsis tcsts tcstot {
		
		ttest `variable', by(RA)
		mat A=(r(mu_1),r(mu_2),r(mu_1)-r(mu_2)\r(sd_1), r(sd_2), 0)
			

		xi: reg `variable' i.RA, vce(`SE')
		mat variance=e(V)
		mat A[2,3]=variance[1,1]^0.5/*replace it with S.E.*/
		test _IRA_2=0
		mat b_aux=(r(p)\0)
		mat D=A,b_aux/*add p-value*/
		mat c_aux=(e(N)\0)
		mat D=D,c_aux/*add N*/

		if `x'==1{
			mat baseline=D
		}
		else{
			mat baseline=baseline\D
		}
		local x=`x'+1
	}


	*the table
	putexcel B2=matrix(baseline) using "$results/Skills/skills_Y2_gender_`sex'", sheet("data") modify
	local number=2
	foreach x in "SSRS: Academic scale" "CBS: Behavior skills" "CBS: Independent skills" "CBS: Transitional skills" "CBS: Total skills" {
		putexcel A`number'=("`x'") using "$results/Skills/skills_Y2_gender_`sex'", sheet("data") modify
		local number=`number'+2
	}
	putexcel B1=("Treatment") using "$results/Skills/skills_Y2_gender_`sex'", sheet("data") modify
	putexcel C1=("Control") using "$results/Skills/skills_Y2_gender_`sex'", sheet("data") modify
	putexcel D1=("T-C") using "$results/Skills/skills_Y2_gender_`sex'", sheet("data") modify
	putexcel E1=("p-value") using "$results/Skills/skills_Y2_gender_`sex'", sheet("data") modify
	putexcel F1=("N") using "$results/Skills/skills_Y2_gender_`sex'", sheet("data") modify

	
	local nn=`nn'+1
	
	restore


}


set more on

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
